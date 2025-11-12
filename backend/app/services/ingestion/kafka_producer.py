"""
Kafka Producer for streaming sensor data
"""
from typing import Dict, Any, Optional
import json
from datetime import datetime
from kafka import KafkaProducer
from kafka.errors import KafkaError

from app.core.config import settings
from app.utils.logger import setup_logging

logger = setup_logging()


class KafkaDataProducer:
    """Kafka producer for sending sensor data to message queue"""
    
    def __init__(
        self,
        bootstrap_servers: Optional[str] = None,
        topic: Optional[str] = None,
    ):
        self.bootstrap_servers = bootstrap_servers or settings.KAFKA_BOOTSTRAP_SERVERS
        self.topic = topic or settings.KAFKA_TOPIC_SENSOR_DATA
        
        self.producer: Optional[KafkaProducer] = None
        self._connect()
    
    def _connect(self):
        """Connect to Kafka broker"""
        try:
            # Build producer configuration
            producer_config = {
                'bootstrap_servers': self.bootstrap_servers.split(','),
                'value_serializer': lambda v: json.dumps(v).encode('utf-8'),
                'key_serializer': lambda k: k.encode('utf-8') if k else None,
                'acks': 'all',  # Wait for all replicas
                'retries': 3,
                'max_in_flight_requests_per_connection': 1,
                'compression_type': 'gzip',
            }
            
            # Add SSL configuration if needed
            if settings.KAFKA_SECURITY_PROTOCOL in ['SSL', 'SASL_SSL']:
                if settings.KAFKA_SSL_CAFILE:
                    producer_config['ssl_cafile'] = settings.KAFKA_SSL_CAFILE
                if settings.KAFKA_SSL_CERTFILE:
                    producer_config['ssl_certfile'] = settings.KAFKA_SSL_CERTFILE
                if settings.KAFKA_SSL_KEYFILE:
                    producer_config['ssl_keyfile'] = settings.KAFKA_SSL_KEYFILE
            
            # Add SASL configuration if needed
            if settings.KAFKA_SECURITY_PROTOCOL in ['SASL_PLAINTEXT', 'SASL_SSL']:
                if settings.KAFKA_SASL_MECHANISM:
                    producer_config['sasl_mechanism'] = settings.KAFKA_SASL_MECHANISM
                if settings.KAFKA_SASL_USERNAME:
                    producer_config['sasl_plain_username'] = settings.KAFKA_SASL_USERNAME
                if settings.KAFKA_SASL_PASSWORD:
                    producer_config['sasl_plain_password'] = settings.KAFKA_SASL_PASSWORD
            
            # Set security protocol
            producer_config['security_protocol'] = settings.KAFKA_SECURITY_PROTOCOL
            
            self.producer = KafkaProducer(**producer_config)
            logger.info("Kafka producer connected", servers=self.bootstrap_servers, protocol=settings.KAFKA_SECURITY_PROTOCOL)
        except Exception as e:
            logger.error("Failed to connect to Kafka", error=str(e))
            raise
    
    def send(self, data: Dict[str, Any], topic: Optional[str] = None, key: Optional[str] = None):
        """Send data to Kafka topic"""
        if not self.producer:
            raise ConnectionError("Kafka producer not connected")
        
        try:
            # Add timestamp if not present
            if '_metadata' not in data:
                data['_metadata'] = {}
            
            if 'timestamp' not in data['_metadata']:
                data['_metadata']['timestamp'] = datetime.utcnow().isoformat()
            
            # Determine topic
            target_topic = topic or self.topic
            
            # Determine key (use well_id if available)
            message_key = key or data.get('well_id') or data.get('node_id')
            
            # Send message
            future = self.producer.send(
                target_topic,
                value=data,
                key=message_key
            )
            
            # Wait for send to complete
            record_metadata = future.get(timeout=10)
            
            logger.debug(
                "Message sent to Kafka",
                topic=record_metadata.topic,
                partition=record_metadata.partition,
                offset=record_metadata.offset
            )
            
            return record_metadata
            
        except KafkaError as e:
            logger.error("Kafka send error", error=str(e), topic=target_topic)
            raise
        except Exception as e:
            logger.error("Error sending to Kafka", error=str(e))
            raise
    
    def send_batch(self, data_list: list[Dict[str, Any]], topic: Optional[str] = None):
        """Send batch of data to Kafka"""
        if not self.producer:
            raise ConnectionError("Kafka producer not connected")
        
        try:
            target_topic = topic or self.topic
            futures = []
            
            for data in data_list:
                # Add timestamp if not present
                if '_metadata' not in data:
                    data['_metadata'] = {}
                
                if 'timestamp' not in data['_metadata']:
                    data['_metadata']['timestamp'] = datetime.utcnow().isoformat()
                
                message_key = data.get('well_id') or data.get('node_id')
                
                future = self.producer.send(
                    target_topic,
                    value=data,
                    key=message_key
                )
                futures.append(future)
            
            # Wait for all sends to complete
            for future in futures:
                record_metadata = future.get(timeout=10)
                logger.debug(
                    "Batch message sent",
                    topic=record_metadata.topic,
                    partition=record_metadata.partition
                )
            
            logger.info("Batch sent to Kafka", count=len(data_list), topic=target_topic)
            
        except Exception as e:
            logger.error("Error sending batch to Kafka", error=str(e))
            raise
    
    def flush(self):
        """Flush pending messages"""
        if self.producer:
            self.producer.flush()
    
    def close(self):
        """Close Kafka producer"""
        if self.producer:
            self.producer.close()
            logger.info("Kafka producer closed")

