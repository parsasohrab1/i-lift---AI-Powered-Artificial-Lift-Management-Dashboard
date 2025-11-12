"""
Kafka Consumer for receiving sensor data
"""
from typing import Callable, Optional, Dict, Any
import json
from kafka import KafkaConsumer
from kafka.errors import KafkaError

from app.core.config import settings
from app.utils.logger import setup_logging

logger = setup_logging()


class KafkaDataConsumer:
    """Kafka consumer for receiving sensor data from message queue"""
    
    def __init__(
        self,
        bootstrap_servers: Optional[str] = None,
        topic: Optional[str] = None,
        group_id: Optional[str] = None,
        auto_offset_reset: str = 'latest',
    ):
        self.bootstrap_servers = bootstrap_servers or settings.KAFKA_BOOTSTRAP_SERVERS
        self.topic = topic or settings.KAFKA_TOPIC_SENSOR_DATA
        self.group_id = group_id or "ilift_processing_group"
        self.auto_offset_reset = auto_offset_reset
        
        self.consumer: Optional[KafkaConsumer] = None
        self.is_running = False
        self.message_callback: Optional[Callable] = None
    
    def _connect(self):
        """Connect to Kafka broker"""
        try:
            self.consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=self.bootstrap_servers.split(','),
                group_id=self.group_id,
                auto_offset_reset=self.auto_offset_reset,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                key_deserializer=lambda k: k.decode('utf-8') if k else None,
                enable_auto_commit=True,
                auto_commit_interval_ms=1000,
                max_poll_records=100,
            )
            logger.info("Kafka consumer connected", topic=self.topic, group_id=self.group_id)
        except Exception as e:
            logger.error("Failed to connect to Kafka", error=str(e))
            raise
    
    def start(self, callback: Callable):
        """Start consuming messages"""
        if not self.consumer:
            self._connect()
        
        self.message_callback = callback
        self.is_running = True
        
        logger.info("Kafka consumer started", topic=self.topic)
        
        try:
            for message in self.consumer:
                if not self.is_running:
                    break
                
                try:
                    data = message.value
                    key = message.key
                    partition = message.partition
                    offset = message.offset
                    
                    # Add Kafka metadata
                    if '_metadata' not in data:
                        data['_metadata'] = {}
                    data['_metadata']['kafka'] = {
                        'topic': message.topic,
                        'partition': partition,
                        'offset': offset,
                        'key': key,
                    }
                    
                    # Call callback
                    if self.message_callback:
                        self.message_callback(data)
                    else:
                        logger.warning("No message callback set")
                        
                except Exception as e:
                    logger.error("Error processing Kafka message", error=str(e), offset=message.offset)
                    
        except KeyboardInterrupt:
            logger.info("Kafka consumer interrupted")
        except Exception as e:
            logger.error("Kafka consumer error", error=str(e))
        finally:
            self.stop()
    
    def stop(self):
        """Stop consuming messages"""
        self.is_running = False
        if self.consumer:
            self.consumer.close()
            logger.info("Kafka consumer stopped")
    
    def pause(self):
        """Pause consumption"""
        if self.consumer:
            self.consumer.pause()
            logger.info("Kafka consumer paused")
    
    def resume(self):
        """Resume consumption"""
        if self.consumer:
            self.consumer.resume()
            logger.info("Kafka consumer resumed")

