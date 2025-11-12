"""
Database writer for storing processed sensor data
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
import uuid

from app.core.database import get_db, SessionLocal
from app.models.sensor import SensorReading
from app.utils.logger import setup_logging

logger = setup_logging()


class DatabaseWriter:
    """Write processed sensor data to TimescaleDB"""
    
    def __init__(self, batch_size: int = 100):
        """
        Initialize database writer
        
        Args:
            batch_size: Number of records to batch before writing
        """
        self.batch_size = batch_size
        self.batch_buffer: List[Dict[str, Any]] = []
        self.stats = {
            'total_written': 0,
            'total_errors': 0,
            'last_write_time': None,
        }
    
    def write(self, data: Dict[str, Any], flush: bool = False):
        """
        Write data to database (buffered)
        
        Args:
            data: Processed sensor data
            flush: Force immediate write
        """
        # Add to buffer
        self.batch_buffer.append(data)
        
        # Write if buffer is full or flush requested
        if len(self.batch_buffer) >= self.batch_size or flush:
            self._flush_buffer()
    
    def _flush_buffer(self):
        """Flush buffer to database"""
        if not self.batch_buffer:
            return
        
        db: Session = SessionLocal()
        
        try:
            readings_to_insert = []
            
            for data in self.batch_buffer:
                try:
                    # Parse timestamp
                    timestamp_str = data.get('timestamp') or data.get('_metadata', {}).get('timestamp')
                    try:
                        if isinstance(timestamp_str, str):
                            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        else:
                            timestamp = datetime.utcnow()
                    except Exception:
                        timestamp = datetime.utcnow()
                    
                    # Create sensor reading
                    reading = SensorReading(
                        reading_id=uuid.uuid4(),
                        well_id=data.get('well_id'),
                        sensor_type=data.get('sensor_type'),
                        sensor_value=float(data.get('sensor_value', 0)),
                        measurement_unit=data.get('measurement_unit'),
                        data_quality=data.get('data_quality') or data.get('_validation', {}).get('quality_score', 100),
                        timestamp=timestamp,
                    )
                    
                    readings_to_insert.append(reading)
                    
                except Exception as e:
                    logger.error("Error preparing reading for insert", error=str(e), data=data)
                    self.stats['total_errors'] += 1
            
            # Bulk insert
            if readings_to_insert:
                db.bulk_save_objects(readings_to_insert)
                db.commit()
                
                self.stats['total_written'] += len(readings_to_insert)
                self.stats['last_write_time'] = datetime.utcnow()
                
                logger.info(
                    "Batch written to database",
                    count=len(readings_to_insert),
                    total_written=self.stats['total_written']
                )
            
            # Clear buffer
            self.batch_buffer.clear()
            
        except Exception as e:
            db.rollback()
            logger.error("Error writing batch to database", error=str(e))
            self.stats['total_errors'] += len(self.batch_buffer)
            self.batch_buffer.clear()
        finally:
            db.close()
    
    def flush(self):
        """Force flush buffer"""
        self._flush_buffer()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get writer statistics"""
        return {
            **self.stats,
            'buffer_size': len(self.batch_buffer),
        }
    
    def write_ml_prediction(
        self,
        well_id: str,
        model_type: str,
        prediction_value: Optional[float],
        confidence_score: Optional[float],
        prediction_type: str,
        features: Optional[Dict[str, Any]] = None,
    ):
        """Write ML prediction to database"""
        db: Session = SessionLocal()
        
        try:
            from app.models.ml_prediction import MLPrediction
            
            prediction = MLPrediction(
                prediction_id=uuid.uuid4(),
                well_id=well_id,
                model_type=model_type,
                prediction_value=prediction_value,
                confidence_score=confidence_score,
                prediction_type=prediction_type,
                features=features,
                timestamp=datetime.utcnow(),
            )
            
            db.add(prediction)
            db.commit()
            
            logger.info("ML prediction written", well_id=well_id, model_type=model_type)
            
        except Exception as e:
            db.rollback()
            logger.error("Error writing ML prediction", error=str(e))
        finally:
            db.close()

