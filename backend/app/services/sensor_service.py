"""
Sensor data service with database operations
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from sqlalchemy.sql import text

from app.schemas.sensor import SensorReading, SensorReadingResponse
from app.models.sensor import SensorReading as SensorReadingModel
from app.core.database import get_db
from app.core.redis_client import redis_client
from app.utils.logger import setup_logging

logger = setup_logging()


class SensorService:
    """Service for sensor data operations"""
    
    def __init__(self, db: Session = None):
        if db:
            self.db = db
        else:
            self.db = next(get_db())
    
    async def get_readings(
        self,
        well_id: Optional[str] = None,
        sensor_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[SensorReadingResponse]:
        """Get sensor readings with filters"""
        try:
            query = self.db.query(SensorReadingModel)
            
            # Apply filters
            if well_id:
                query = query.filter(SensorReadingModel.well_id == well_id)
            if sensor_type:
                query = query.filter(SensorReadingModel.sensor_type == sensor_type)
            if start_time:
                query = query.filter(SensorReadingModel.timestamp >= start_time)
            if end_time:
                query = query.filter(SensorReadingModel.timestamp <= end_time)
            
            # Order by timestamp descending
            query = query.order_by(desc(SensorReadingModel.timestamp))
            
            # Apply pagination
            readings = query.offset(offset).limit(limit).all()
            
            return [SensorReadingResponse.model_validate(r) for r in readings]
            
        except Exception as e:
            logger.error("Error getting sensor readings", error=str(e))
            raise
    
    async def get_latest_readings(
        self,
        well_id: Optional[str] = None,
        sensor_type: Optional[str] = None,
    ) -> List[SensorReadingResponse]:
        """Get latest reading for each sensor"""
        try:
            # Use window function to get latest reading per well/sensor
            subquery = (
                self.db.query(
                    SensorReadingModel.well_id,
                    SensorReadingModel.sensor_type,
                    func.max(SensorReadingModel.timestamp).label('max_timestamp')
                )
                .group_by(SensorReadingModel.well_id, SensorReadingModel.sensor_type)
                .subquery()
            )
            
            query = (
                self.db.query(SensorReadingModel)
                .join(
                    subquery,
                    and_(
                        SensorReadingModel.well_id == subquery.c.well_id,
                        SensorReadingModel.sensor_type == subquery.c.sensor_type,
                        SensorReadingModel.timestamp == subquery.c.max_timestamp
                    )
                )
            )
            
            if well_id:
                query = query.filter(SensorReadingModel.well_id == well_id)
            if sensor_type:
                query = query.filter(SensorReadingModel.sensor_type == sensor_type)
            
            readings = query.all()
            return [SensorReadingResponse.model_validate(r) for r in readings]
            
        except Exception as e:
            logger.error("Error getting latest readings", error=str(e))
            raise
    
    async def get_realtime_data(
        self,
        well_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get real-time sensor data (cached)"""
        try:
            cache_key = f"realtime:{well_id}" if well_id else "realtime:all"
            
            # Try cache first
            cached = redis_client.get(cache_key)
            if cached:
                return cached
            
            # Get latest readings
            readings = await self.get_latest_readings(well_id=well_id)
            
            # Organize by well and sensor
            result = {}
            for reading in readings:
                if reading.well_id not in result:
                    result[reading.well_id] = {}
                result[reading.well_id][reading.sensor_type] = {
                    'value': reading.sensor_value,
                    'unit': reading.measurement_unit,
                    'timestamp': reading.timestamp.isoformat(),
                    'quality': reading.data_quality,
                }
            
            # Cache for 5 seconds
            redis_client.set(cache_key, result, ttl=5)
            
            return result
            
        except Exception as e:
            logger.error("Error getting realtime data", error=str(e))
            raise
    
    async def create_reading(self, reading: SensorReading) -> SensorReadingResponse:
        """Create a new sensor reading"""
        try:
            # Parse timestamp
            timestamp = reading.timestamp or datetime.utcnow()
            
            db_reading = SensorReadingModel(
                well_id=reading.well_id,
                sensor_type=reading.sensor_type,
                sensor_value=reading.sensor_value,
                measurement_unit=reading.measurement_unit,
                data_quality=reading.data_quality,
                timestamp=timestamp,
            )
            
            self.db.add(db_reading)
            self.db.commit()
            self.db.refresh(db_reading)
            
            # Invalidate cache
            redis_client.delete(f"realtime:{reading.well_id}")
            redis_client.delete("realtime:all")
            
            return SensorReadingResponse.from_orm(db_reading)
            
        except Exception as e:
            self.db.rollback()
            logger.error("Error creating sensor reading", error=str(e))
            raise
    
    async def get_aggregated_data(
        self,
        well_id: str,
        sensor_type: str,
        start_time: datetime,
        end_time: datetime,
        aggregation: str = 'hourly',  # hourly, daily, weekly
    ) -> List[Dict[str, Any]]:
        """Get aggregated sensor data"""
        try:
            # Map aggregation to time bucket
            bucket_map = {
                'hourly': '1 hour',
                'daily': '1 day',
                'weekly': '1 week',
            }
            
            bucket = bucket_map.get(aggregation, '1 hour')
            
            # Use TimescaleDB time_bucket function
            query = text("""
                SELECT 
                    time_bucket(:bucket, timestamp) AS bucket,
                    well_id,
                    sensor_type,
                    AVG(sensor_value) AS avg_value,
                    MIN(sensor_value) AS min_value,
                    MAX(sensor_value) AS max_value,
                    STDDEV(sensor_value) AS std_value,
                    COUNT(*) AS count
                FROM sensor_readings
                WHERE well_id = :well_id
                  AND sensor_type = :sensor_type
                  AND timestamp >= :start_time
                  AND timestamp <= :end_time
                GROUP BY bucket, well_id, sensor_type
                ORDER BY bucket
            """)
            
            result = self.db.execute(
                query,
                {
                    'bucket': bucket,
                    'well_id': well_id,
                    'sensor_type': sensor_type,
                    'start_time': start_time,
                    'end_time': end_time,
                }
            )
            
            aggregated = []
            for row in result:
                aggregated.append({
                    'timestamp': row.bucket.isoformat(),
                    'well_id': row.well_id,
                    'sensor_type': row.sensor_type,
                    'avg_value': float(row.avg_value),
                    'min_value': float(row.min_value),
                    'max_value': float(row.max_value),
                    'std_value': float(row.std_value) if row.std_value else 0,
                    'count': row.count,
                })
            
            return aggregated
            
        except Exception as e:
            logger.error("Error getting aggregated data", error=str(e))
            raise
    
    async def get_statistics(
        self,
        well_id: Optional[str] = None,
        sensor_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get statistics for sensor data"""
        try:
            query = self.db.query(
                SensorReadingModel.well_id,
                SensorReadingModel.sensor_type,
                func.count(SensorReadingModel.reading_id).label('count'),
                func.avg(SensorReadingModel.sensor_value).label('avg'),
                func.min(SensorReadingModel.sensor_value).label('min'),
                func.max(SensorReadingModel.sensor_value).label('max'),
                func.stddev(SensorReadingModel.sensor_value).label('std'),
            )
            
            if well_id:
                query = query.filter(SensorReadingModel.well_id == well_id)
            if sensor_type:
                query = query.filter(SensorReadingModel.sensor_type == sensor_type)
            if start_time:
                query = query.filter(SensorReadingModel.timestamp >= start_time)
            if end_time:
                query = query.filter(SensorReadingModel.timestamp <= end_time)
            
            query = query.group_by(
                SensorReadingModel.well_id,
                SensorReadingModel.sensor_type
            )
            
            results = query.all()
            
            stats = {}
            for row in results:
                key = f"{row.well_id}_{row.sensor_type}"
                stats[key] = {
                    'well_id': row.well_id,
                    'sensor_type': row.sensor_type,
                    'count': row.count,
                    'avg': float(row.avg) if row.avg else 0,
                    'min': float(row.min) if row.min else 0,
                    'max': float(row.max) if row.max else 0,
                    'std': float(row.std) if row.std else 0,
                }
            
            return stats
            
        except Exception as e:
            logger.error("Error getting statistics", error=str(e))
            raise
