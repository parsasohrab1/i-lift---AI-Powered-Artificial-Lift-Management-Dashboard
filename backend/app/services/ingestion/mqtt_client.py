"""
MQTT Client Service for IoT sensor data ingestion
"""
import json
import asyncio
from typing import Callable, Optional, Dict, Any
from datetime import datetime
import paho.mqtt.client as mqtt
from threading import Thread

from app.core.config import settings
from app.utils.logger import setup_logging

logger = setup_logging()


class MQTTClient:
    """MQTT client for receiving sensor data"""
    
    def __init__(
        self,
        broker_host: str = "localhost",
        broker_port: int = 1883,
        username: Optional[str] = None,
        password: Optional[str] = None,
        client_id: Optional[str] = None,
    ):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.username = username
        self.password = password
        self.client_id = client_id or f"ilift_ingestion_{datetime.now().timestamp()}"
        
        self.client: Optional[mqtt.Client] = None
        self.is_connected = False
        self.message_callback: Optional[Callable] = None
        self.topics: list = []
        
    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker"""
        if rc == 0:
            self.is_connected = True
            logger.info("MQTT client connected", broker=f"{self.broker_host}:{self.broker_port}")
            
            # Subscribe to topics
            for topic in self.topics:
                client.subscribe(topic)
                logger.info("Subscribed to topic", topic=topic)
        else:
            logger.error("MQTT connection failed", return_code=rc)
            self.is_connected = False
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from MQTT broker"""
        self.is_connected = False
        logger.warning("MQTT client disconnected", return_code=rc)
    
    def _on_message(self, client, userdata, msg):
        """Callback when message is received"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            # Parse JSON payload
            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                logger.error("Invalid JSON payload", topic=topic, payload=payload)
                return
            
            # Add metadata
            data['_metadata'] = {
                'topic': topic,
                'timestamp': datetime.utcnow().isoformat(),
                'source': 'mqtt',
            }
            
            # Call message callback if set
            if self.message_callback:
                self.message_callback(data)
            else:
                logger.warning("No message callback set for MQTT client")
                
        except Exception as e:
            logger.error("Error processing MQTT message", error=str(e), topic=msg.topic)
    
    def connect(self):
        """Connect to MQTT broker"""
        try:
            self.client = mqtt.Client(
                client_id=self.client_id,
                clean_session=True
            )
            
            # Set callbacks
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message
            
            # Set credentials if provided
            if self.username and self.password:
                self.client.username_pw_set(self.username, self.password)
            
            # Connect
            self.client.connect(self.broker_host, self.broker_port, keepalive=60)
            
            # Start loop in background thread
            self.client.loop_start()
            
            logger.info("MQTT client started", broker=f"{self.broker_host}:{self.broker_port}")
            
        except Exception as e:
            logger.error("Failed to connect to MQTT broker", error=str(e))
            raise
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.is_connected = False
            logger.info("MQTT client disconnected")
    
    def subscribe(self, topic: str, qos: int = 0):
        """Subscribe to a topic"""
        if topic not in self.topics:
            self.topics.append(topic)
        
        if self.client and self.is_connected:
            self.client.subscribe(topic, qos)
            logger.info("Subscribed to topic", topic=topic, qos=qos)
    
    def unsubscribe(self, topic: str):
        """Unsubscribe from a topic"""
        if topic in self.topics:
            self.topics.remove(topic)
        
        if self.client and self.is_connected:
            self.client.unsubscribe(topic)
            logger.info("Unsubscribed from topic", topic=topic)
    
    def set_message_callback(self, callback: Callable):
        """Set callback function for received messages"""
        self.message_callback = callback

