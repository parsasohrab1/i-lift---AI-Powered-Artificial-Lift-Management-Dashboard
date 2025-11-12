"""
Analytics service for KPI calculations and data analysis
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, text
import statistics

from app.schemas.analytics import AnalyticsResponse, TrendResponse, ComparisonResponse
from app.models.sensor import SensorReading as SensorReadingModel
from app.models.well import Well
from app.core.database import get_db
from app.core.redis_client import redis_client
from app.utils.logger import setup_logging

logger = setup_logging()


class AnalyticsService:
    """Service for analytics operations"""
    
    def __init__(self, db: Session = None):
        if db:
            self.db = db
        else:
            self.db = next(get_db())
    
    async def get_kpis(
        self,
        well_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get KPI analytics"""
        try:
            # Default time range: last 30 days
            if not end_time:
                end_time = datetime.utcnow()
            if not start_time:
                start_time = end_time - timedelta(days=30)
            
            # Build query
            query = self.db.query(SensorReadingModel).filter(
                SensorReadingModel.timestamp >= start_time,
                SensorReadingModel.timestamp <= end_time,
            )
            
            if well_id:
                query = query.filter(SensorReadingModel.well_id == well_id)
            
            readings = query.all()
            
            if not readings:
                return {
                    'total_readings': 0,
                    'active_wells': 0,
                    'average_temperature': 0,
                    'average_pressure': 0,
                    'average_flow_rate': 0,
                    'uptime_percentage': 0,
                    'efficiency_score': 0,
                }
            
            # Calculate KPIs
            kpis = {
                'total_readings': len(readings),
                'active_wells': len(set(r.well_id for r in readings)),
                'time_range': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat(),
                },
            }
            
            # Sensor-specific KPIs
            sensor_data = {}
            for reading in readings:
                if reading.sensor_type not in sensor_data:
                    sensor_data[reading.sensor_type] = []
                sensor_data[reading.sensor_type].append(reading.sensor_value)
            
            # Calculate averages and statistics
            for sensor_type, values in sensor_data.items():
                if values:
                    kpis[f'{sensor_type}_avg'] = statistics.mean(values)
                    kpis[f'{sensor_type}_min'] = min(values)
                    kpis[f'{sensor_type}_max'] = max(values)
                    kpis[f'{sensor_type}_std'] = statistics.stdev(values) if len(values) > 1 else 0
            
            # Calculate derived KPIs
            kpis.update(self._calculate_derived_kpis(readings, well_id))
            
            return kpis
            
        except Exception as e:
            logger.error("Error calculating KPIs", error=str(e))
            raise
    
    def _calculate_derived_kpis(
        self,
        readings: List[SensorReadingModel],
        well_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Calculate derived KPIs"""
        kpis = {}
        
        # Organize by well and sensor
        well_sensor_data = {}
        for reading in readings:
            if reading.well_id not in well_sensor_data:
                well_sensor_data[reading.well_id] = {}
            if reading.sensor_type not in well_sensor_data[reading.well_id]:
                well_sensor_data[reading.well_id][reading.sensor_type] = []
            well_sensor_data[reading.well_id][reading.sensor_type].append(reading)
        
        # Calculate efficiency (flow_rate / current)
        efficiency_scores = []
        for well_id, sensors in well_sensor_data.items():
            if 'flow_rate' in sensors and 'current' in sensors:
                flow_readings = sensors['flow_rate']
                current_readings = sensors['current']
                
                # Match by timestamp (simplified - in production use proper time alignment)
                for flow in flow_readings[:min(len(flow_readings), len(current_readings))]:
                    if flow.sensor_value > 0 and current_readings[0].sensor_value > 0:
                        efficiency = flow.sensor_value / current_readings[0].sensor_value
                        efficiency_scores.append(efficiency)
        
        if efficiency_scores:
            kpis['average_efficiency'] = statistics.mean(efficiency_scores)
            kpis['efficiency_range'] = {
                'min': min(efficiency_scores),
                'max': max(efficiency_scores),
            }
        
        # Calculate uptime (based on data quality and status)
        total_readings = len(readings)
        high_quality_readings = sum(1 for r in readings if r.data_quality and r.data_quality >= 80)
        kpis['data_quality_percentage'] = (high_quality_readings / total_readings * 100) if total_readings > 0 else 0
        
        # Calculate pressure differential
        pressure_differentials = []
        for well_id, sensors in well_sensor_data.items():
            if 'discharge_pressure' in sensors and 'intake_pressure' in sensors:
                discharge = sensors['discharge_pressure']
                intake = sensors['intake_pressure']
                for d, i in zip(discharge[:min(len(discharge), len(intake))], intake[:min(len(discharge), len(intake))]):
                    diff = d.sensor_value - i.sensor_value
                    pressure_differentials.append(diff)
        
        if pressure_differentials:
            kpis['average_pressure_differential'] = statistics.mean(pressure_differentials)
        
        return kpis
    
    async def get_trends(
        self,
        well_id: str,
        metric: str,
        days: int = 30,
    ) -> Dict[str, Any]:
        """Get trend analysis for a metric"""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days)
            
            # Map metric to sensor type
            metric_map = {
                'temperature': 'motor_temperature',
                'pressure': 'intake_pressure',
                'flow': 'flow_rate',
                'vibration': 'vibration',
                'current': 'current',
            }
            
            sensor_type = metric_map.get(metric.lower(), metric)
            
            # Get aggregated data (daily)
            query = text("""
                SELECT 
                    time_bucket('1 day', timestamp) AS bucket,
                    AVG(sensor_value) AS avg_value,
                    MIN(sensor_value) AS min_value,
                    MAX(sensor_value) AS max_value,
                    COUNT(*) AS count
                FROM sensor_readings
                WHERE well_id = :well_id
                  AND sensor_type = :sensor_type
                  AND timestamp >= :start_time
                  AND timestamp <= :end_time
                GROUP BY bucket
                ORDER BY bucket
            """)
            
            result = self.db.execute(
                query,
                {
                    'well_id': well_id,
                    'sensor_type': sensor_type,
                    'start_time': start_time,
                    'end_time': end_time,
                }
            )
            
            data_points = []
            for row in result:
                data_points.append({
                    'date': row.bucket.isoformat(),
                    'avg': float(row.avg_value),
                    'min': float(row.min_value),
                    'max': float(row.max_value),
                    'count': row.count,
                })
            
            # Calculate trend (linear regression)
            if len(data_points) >= 2:
                x = list(range(len(data_points)))
                y = [d['avg'] for d in data_points]
                
                # Simple linear regression
                n = len(x)
                sum_x = sum(x)
                sum_y = sum(y)
                sum_xy = sum(x[i] * y[i] for i in range(n))
                sum_x2 = sum(x[i] ** 2 for i in range(n))
                
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2) if (n * sum_x2 - sum_x ** 2) != 0 else 0
                intercept = (sum_y - slope * sum_x) / n
                
                trend_direction = 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable'
                trend_strength = abs(slope) / (statistics.stdev(y) if len(y) > 1 else 1) if statistics.stdev(y) > 0 else 0
            else:
                slope = 0
                intercept = 0
                trend_direction = 'stable'
                trend_strength = 0
            
            return {
                'well_id': well_id,
                'metric': metric,
                'sensor_type': sensor_type,
                'time_range': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat(),
                    'days': days,
                },
                'data_points': data_points,
                'trend': {
                    'direction': trend_direction,
                    'slope': slope,
                    'strength': trend_strength,
                    'intercept': intercept,
                },
                'statistics': {
                    'current': data_points[-1]['avg'] if data_points else 0,
                    'average': statistics.mean([d['avg'] for d in data_points]) if data_points else 0,
                    'change_percent': ((data_points[-1]['avg'] - data_points[0]['avg']) / data_points[0]['avg'] * 100) if data_points and data_points[0]['avg'] != 0 else 0,
                },
            }
            
        except Exception as e:
            logger.error("Error calculating trends", error=str(e))
            raise
    
    async def get_comparison(
        self,
        well_ids: List[str],
        metric: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Compare multiple wells for a metric"""
        try:
            if not end_time:
                end_time = datetime.utcnow()
            if not start_time:
                start_time = end_time - timedelta(days=30)
            
            metric_map = {
                'temperature': 'motor_temperature',
                'pressure': 'intake_pressure',
                'flow': 'flow_rate',
                'vibration': 'vibration',
                'current': 'current',
            }
            
            sensor_type = metric_map.get(metric.lower(), metric)
            
            # Get aggregated data for each well
            comparison_data = {}
            
            for well_id in well_ids:
                query = text("""
                    SELECT 
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
                """)
                
                result = self.db.execute(
                    query,
                    {
                        'well_id': well_id,
                        'sensor_type': sensor_type,
                        'start_time': start_time,
                        'end_time': end_time,
                    }
                ).first()
                
                if result and result.avg_value:
                    comparison_data[well_id] = {
                        'avg': float(result.avg_value),
                        'min': float(result.min_value),
                        'max': float(result.max_value),
                        'std': float(result.std_value) if result.std_value else 0,
                        'count': result.count,
                    }
            
            # Calculate rankings
            if comparison_data:
                sorted_wells = sorted(
                    comparison_data.items(),
                    key=lambda x: x[1]['avg'],
                    reverse=True
                )
                
                rankings = {}
                for rank, (well_id, _) in enumerate(sorted_wells, 1):
                    rankings[well_id] = rank
            else:
                rankings = {}
            
            return {
                'metric': metric,
                'sensor_type': sensor_type,
                'time_range': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat(),
                },
                'wells': comparison_data,
                'rankings': rankings,
                'best_performer': sorted_wells[0][0] if sorted_wells else None,
                'worst_performer': sorted_wells[-1][0] if sorted_wells else None,
            }
            
        except Exception as e:
            logger.error("Error calculating comparison", error=str(e))
            raise
    
    async def get_performance_metrics(
        self,
        well_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get performance metrics"""
        try:
            if not end_time:
                end_time = datetime.utcnow()
            if not start_time:
                start_time = end_time - timedelta(days=30)
            
            # Get all sensor readings in time range
            query = self.db.query(SensorReadingModel).filter(
                SensorReadingModel.timestamp >= start_time,
                SensorReadingModel.timestamp <= end_time,
            )
            
            if well_id:
                query = query.filter(SensorReadingModel.well_id == well_id)
            
            readings = query.all()
            
            if not readings:
                return {
                    'total_readings': 0,
                    'data_quality_score': 0,
                    'uptime_percentage': 0,
                    'efficiency_score': 0,
                }
            
            # Calculate performance metrics
            total_readings = len(readings)
            high_quality = sum(1 for r in readings if r.data_quality and r.data_quality >= 80)
            
            # Organize by well
            well_data = {}
            for reading in readings:
                if reading.well_id not in well_data:
                    well_data[reading.well_id] = {}
                if reading.sensor_type not in well_data[reading.well_id]:
                    well_data[reading.well_id][reading.sensor_type] = []
                well_data[reading.well_id][reading.sensor_type].append(reading)
            
            # Calculate efficiency per well
            efficiency_scores = []
            for well_id, sensors in well_data.items():
                if 'flow_rate' in sensors and 'current' in sensors:
                    flow_avg = statistics.mean([r.sensor_value for r in sensors['flow_rate']])
                    current_avg = statistics.mean([r.sensor_value for r in sensors['current']])
                    if current_avg > 0:
                        efficiency_scores.append(flow_avg / current_avg)
            
            return {
                'total_readings': total_readings,
                'active_wells': len(well_data),
                'data_quality_score': (high_quality / total_readings * 100) if total_readings > 0 else 0,
                'average_efficiency': statistics.mean(efficiency_scores) if efficiency_scores else 0,
                'time_range': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat(),
                },
                'well_performance': {
                    well_id: {
                        'readings_count': sum(len(sensors) for sensors in sensors_dict.values()),
                        'sensor_types': list(sensors_dict.keys()),
                    }
                    for well_id, sensors_dict in well_data.items()
                },
            }
            
        except Exception as e:
            logger.error("Error calculating performance metrics", error=str(e))
            raise
