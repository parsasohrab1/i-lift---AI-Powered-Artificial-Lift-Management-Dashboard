"""
Main ingestion service orchestrator
"""
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.services.ingestion.mqtt_client import MQTTClient
from app.services.ingestion.opcua_client import OPCUAClient
from app.services.ingestion.kafka_producer import KafkaDataProducer
from app.services.ingestion.data_validator import DataValidator
from app.core.config import settings
from app.utils.logger import setup_logging

logger = setup_logging()


class IngestionService:
    """Main service for orchestrating data ingestion from multiple sources"""
    
    def __init__(self):
        self.mqtt_client: Optional[MQTTClient] = None
        self.opcua_client: Optional[OPCUAClient] = None
        self.kafka_producer: Optional[KafkaDataProducer] = None
        self.validator = DataValidator()
        
        self.is_running = False
        self.stats = {
            'total_received': 0,
            'total_validated': 0,
            'total_sent_to_kafka': 0,
            'total_errors': 0,
            'sources': {}
        }
    
    def initialize(self):
        """Initialize ingestion service"""
        try:
            # Initialize Kafka producer
            self.kafka_producer = KafkaDataProducer()
            logger.info("Ingestion service initialized")
        except Exception as e:
            logger.error("Failed to initialize ingestion service", error=str(e))
            raise
    
    def start_mqtt_ingestion(
        self,
        broker_host: str = "localhost",
        broker_port: int = 1883,
        topics: List[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        """Start MQTT data ingestion"""
        try:
            if self.mqtt_client and self.mqtt_client.is_connected:
                logger.warning("MQTT client already connected")
                return
            
            self.mqtt_client = MQTTClient(
                broker_host=broker_host,
                broker_port=broker_port,
                username=username,
                password=password,
            )
            
            # Set message callback
            self.mqtt_client.set_message_callback(self._handle_ingested_data)
            
            # Connect
            self.mqtt_client.connect()
            
            # Subscribe to topics
            if topics:
                for topic in topics:
                    self.mqtt_client.subscribe(topic)
            
            logger.info("MQTT ingestion started", broker=f"{broker_host}:{broker_port}")
            
        except Exception as e:
            logger.error("Failed to start MQTT ingestion", error=str(e))
            raise
    
    def stop_mqtt_ingestion(self):
        """Stop MQTT data ingestion"""
        if self.mqtt_client:
            self.mqtt_client.disconnect()
            self.mqtt_client = None
            logger.info("MQTT ingestion stopped")
    
    async def start_opcua_ingestion(
        self,
        endpoint_url: str,
        node_ids: List[str],
        username: Optional[str] = None,
        password: Optional[str] = None,
        sampling_interval: int = 1000,
    ):
        """Start OPC-UA data ingestion"""
        try:
            if self.opcua_client and self.opcua_client.is_connected:
                logger.warning("OPC-UA client already connected")
                return
            
            self.opcua_client = OPCUAClient(
                endpoint_url=endpoint_url,
                username=username,
                password=password,
            )
            
            # Connect
            await self.opcua_client.connect()
            
            # Set data callback
            self.opcua_client.data_callback = self._handle_ingested_data
            
            # Monitor nodes
            await self.opcua_client.monitor_nodes(
                node_ids=node_ids,
                sampling_interval=sampling_interval,
                callback=self._handle_ingested_data
            )
            
            logger.info("OPC-UA ingestion started", endpoint=endpoint_url, node_count=len(node_ids))
            
        except Exception as e:
            logger.error("Failed to start OPC-UA ingestion", error=str(e))
            raise
    
    async def stop_opcua_ingestion(self):
        """Stop OPC-UA data ingestion"""
        if self.opcua_client:
            await self.opcua_client.disconnect()
            self.opcua_client = None
            logger.info("OPC-UA ingestion stopped")
    
    def ingest_rest_data(self, data: Dict[str, Any] | List[Dict[str, Any]]) -> Dict[str, Any]:
        """Ingest data from REST API"""
        try:
            # Handle single or batch data
            if isinstance(data, dict):
                data_list = [data]
            else:
                data_list = data
            
            results = {
                'total': len(data_list),
                'validated': 0,
                'sent_to_kafka': 0,
                'errors': 0,
                'errors_detail': []
            }
            
            for item in data_list:
                try:
                    self._handle_ingested_data(item, source='rest')
                    results['validated'] += 1
                    results['sent_to_kafka'] += 1
                except Exception as e:
                    results['errors'] += 1
                    results['errors_detail'].append(str(e))
                    logger.error("Error ingesting REST data", error=str(e))
            
            self.stats['total_received'] += results['total']
            self.stats['total_errors'] += results['errors']
            
            return results
            
        except Exception as e:
            logger.error("Error in REST data ingestion", error=str(e))
            raise
    
    def _handle_ingested_data(self, data: Dict[str, Any], source: Optional[str] = None):
        """Handle ingested data from any source"""
        try:
            self.stats['total_received'] += 1
            
            # Determine source
            if not source:
                source = data.get('_metadata', {}).get('source', 'unknown')
            
            # Update source stats
            if source not in self.stats['sources']:
                self.stats['sources'][source] = 0
            self.stats['sources'][source] += 1
            
            # Normalize data
            normalized_data = self.validator.normalize_sensor_data(data)
            
            # Validate
            is_valid, cleaned_data, errors = self.validator.validate(normalized_data)
            
            if not is_valid:
                logger.warning(
                    "Data validation failed",
                    errors=errors,
                    well_id=cleaned_data.get('well_id'),
                    source=source
                )
                self.stats['total_errors'] += 1
                # Still send to Kafka for analysis, but flagged
            
            # Send to Kafka
            if self.kafka_producer:
                try:
                    self.kafka_producer.send(cleaned_data)
                    self.stats['total_sent_to_kafka'] += 1
                    if is_valid:
                        self.stats['total_validated'] += 1
                except Exception as e:
                    logger.error("Failed to send to Kafka", error=str(e))
                    self.stats['total_errors'] += 1
            else:
                logger.warning("Kafka producer not initialized")
            
        except Exception as e:
            logger.error("Error handling ingested data", error=str(e))
            self.stats['total_errors'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get ingestion statistics"""
        return {
            **self.stats,
            'is_running': self.is_running,
            'mqtt_connected': self.mqtt_client.is_connected if self.mqtt_client else False,
            'opcua_connected': self.opcua_client.is_connected if self.opcua_client else False,
        }
    
    def shutdown(self):
        """Shutdown ingestion service"""
        try:
            self.stop_mqtt_ingestion()
            
            if self.opcua_client:
                import asyncio
                asyncio.run(self.stop_opcua_ingestion())
            
            if self.kafka_producer:
                self.kafka_producer.close()
            
            logger.info("Ingestion service shut down")
        except Exception as e:
            logger.error("Error shutting down ingestion service", error=str(e))

