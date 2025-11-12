"""
Main data processing pipeline orchestrator
"""
from typing import Dict, Any, Optional
from threading import Thread
import time

from app.services.processing.kafka_consumer import KafkaDataConsumer
from app.services.processing.stream_processor import StreamProcessor
from app.services.processing.feature_engineer import FeatureEngineer
from app.services.processing.database_writer import DatabaseWriter
from app.core.config import settings
from app.utils.logger import setup_logging

logger = setup_logging()


class DataProcessingPipeline:
    """Main orchestrator for data processing pipeline"""
    
    def __init__(
        self,
        batch_size: int = 100,
        window_size: int = 60,
    ):
        """
        Initialize processing pipeline
        
        Args:
            batch_size: Batch size for database writes
            window_size: Window size for stream processing (seconds)
        """
        self.kafka_consumer: Optional[KafkaDataConsumer] = None
        self.stream_processor = StreamProcessor(window_size=window_size)
        self.feature_engineer = FeatureEngineer()
        self.database_writer = DatabaseWriter(batch_size=batch_size)
        
        self.is_running = False
        self.processing_thread: Optional[Thread] = None
        
        self.stats = {
            'total_processed': 0,
            'total_errors': 0,
            'processing_rate': 0,
            'last_processed_time': None,
        }
    
    def start(self):
        """Start the processing pipeline"""
        if self.is_running:
            logger.warning("Pipeline already running")
            return
        
        try:
            # Initialize Kafka consumer
            self.kafka_consumer = KafkaDataConsumer(
                auto_offset_reset='latest'
            )
            
            # Start processing in background thread
            self.is_running = True
            self.processing_thread = Thread(target=self._run_processing, daemon=True)
            self.processing_thread.start()
            
            logger.info("Data processing pipeline started")
            
        except Exception as e:
            logger.error("Failed to start processing pipeline", error=str(e))
            raise
    
    def _run_processing(self):
        """Run processing loop"""
        try:
            self.kafka_consumer.start(callback=self._process_message)
        except Exception as e:
            logger.error("Processing loop error", error=str(e))
            self.is_running = False
    
    def _process_message(self, data: Dict[str, Any]):
        """Process a single message from Kafka"""
        try:
            start_time = time.time()
            
            # Step 1: Stream processing
            processed_data = self.stream_processor.process(data)
            
            # Step 2: Feature engineering
            engineered_data = self.feature_engineer.engineer_features(processed_data)
            
            # Step 3: Write to database
            self.database_writer.write(engineered_data)
            
            # Update stats
            self.stats['total_processed'] += 1
            self.stats['last_processed_time'] = time.time()
            
            processing_time = time.time() - start_time
            if processing_time > 0:
                self.stats['processing_rate'] = 1 / processing_time
            
            logger.debug(
                "Message processed",
                well_id=engineered_data.get('well_id'),
                sensor_type=engineered_data.get('sensor_type'),
                processing_time=f"{processing_time:.3f}s"
            )
            
        except Exception as e:
            logger.error("Error processing message", error=str(e), data=data)
            self.stats['total_errors'] += 1
    
    def stop(self):
        """Stop the processing pipeline"""
        self.is_running = False
        
        if self.kafka_consumer:
            self.kafka_consumer.stop()
        
        # Flush database writer
        self.database_writer.flush()
        
        if self.processing_thread:
            self.processing_thread.join(timeout=5)
        
        logger.info("Data processing pipeline stopped")
    
    def pause(self):
        """Pause processing"""
        if self.kafka_consumer:
            self.kafka_consumer.pause()
        logger.info("Processing pipeline paused")
    
    def resume(self):
        """Resume processing"""
        if self.kafka_consumer:
            self.kafka_consumer.resume()
        logger.info("Processing pipeline resumed")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics"""
        return {
            **self.stats,
            'is_running': self.is_running,
            'database_writer': self.database_writer.get_stats(),
            'kafka_consumer_running': self.kafka_consumer.is_running if self.kafka_consumer else False,
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for pipeline"""
        return {
            'status': 'healthy' if self.is_running else 'stopped',
            'is_running': self.is_running,
            'kafka_connected': self.kafka_consumer is not None,
            'total_processed': self.stats['total_processed'],
            'total_errors': self.stats['total_errors'],
            'error_rate': self.stats['total_errors'] / max(self.stats['total_processed'], 1),
        }

