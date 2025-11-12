"""
Metrics collection service using Prometheus
"""
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from prometheus_client import Counter, Histogram, Gauge, Summary, generate_latest, REGISTRY
from prometheus_client.core import CollectorRegistry
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db
from app.utils.logger import setup_logging

logger = setup_logging()

# Create a custom registry for application metrics
metrics_registry = CollectorRegistry()

# HTTP Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status'],
    registry=metrics_registry
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    registry=metrics_registry
)

http_request_size_bytes = Summary(
    'http_request_size_bytes',
    'HTTP request size in bytes',
    ['method', 'endpoint'],
    registry=metrics_registry
)

# Business Metrics
sensor_readings_total = Counter(
    'sensor_readings_total',
    'Total sensor readings processed',
    ['well_id', 'sensor_type', 'status'],
    registry=metrics_registry
)

alerts_total = Counter(
    'alerts_total',
    'Total alerts created',
    ['severity', 'alert_type', 'well_id'],
    registry=metrics_registry
)

ml_predictions_total = Counter(
    'ml_predictions_total',
    'Total ML predictions made',
    ['model_type', 'well_id', 'status'],
    registry=metrics_registry
)

# System Metrics
active_wells = Gauge(
    'active_wells',
    'Number of active wells',
    registry=metrics_registry
)

active_sensors = Gauge(
    'active_sensors',
    'Number of active sensors',
    ['well_id'],
    registry=metrics_registry
)

active_alerts = Gauge(
    'active_alerts',
    'Number of active alerts',
    ['severity'],
    registry=metrics_registry
)

data_ingestion_rate = Gauge(
    'data_ingestion_rate',
    'Data ingestion rate (records per second)',
    ['source'],
    registry=metrics_registry
)

# Database Metrics
db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['query_type'],
    registry=metrics_registry
)

db_connections_active = Gauge(
    'db_connections_active',
    'Active database connections',
    registry=metrics_registry
)

db_connections_idle = Gauge(
    'db_connections_idle',
    'Idle database connections',
    registry=metrics_registry
)

# Kafka Metrics
kafka_messages_produced = Counter(
    'kafka_messages_produced',
    'Total Kafka messages produced',
    ['topic'],
    registry=metrics_registry
)

kafka_messages_consumed = Counter(
    'kafka_messages_consumed',
    'Total Kafka messages consumed',
    ['topic'],
    registry=metrics_registry
)

kafka_consumer_lag = Gauge(
    'kafka_consumer_lag',
    'Kafka consumer lag',
    ['topic', 'partition'],
    registry=metrics_registry
)

# Redis Metrics
redis_operations_total = Counter(
    'redis_operations_total',
    'Total Redis operations',
    ['operation', 'status'],
    registry=metrics_registry
)

redis_cache_hits = Counter(
    'redis_cache_hits',
    'Redis cache hits',
    registry=metrics_registry
)

redis_cache_misses = Counter(
    'redis_cache_misses',
    'Redis cache misses',
    registry=metrics_registry
)


class MetricsService:
    """Service for collecting and exposing metrics"""
    
    def __init__(self, db: Optional[Session] = None):
        self.db = db
    
    def record_http_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration: float,
        size: Optional[int] = None
    ):
        """Record HTTP request metrics"""
        http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status=status_code
        ).inc()
        
        http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
        
        if size:
            http_request_size_bytes.labels(
                method=method,
                endpoint=endpoint
            ).observe(size)
    
    def record_sensor_reading(
        self,
        well_id: str,
        sensor_type: str,
        status: str = "success"
    ):
        """Record sensor reading metric"""
        sensor_readings_total.labels(
            well_id=well_id,
            sensor_type=sensor_type,
            status=status
        ).inc()
    
    def record_alert(
        self,
        severity: str,
        alert_type: str,
        well_id: Optional[str] = None
    ):
        """Record alert metric"""
        alerts_total.labels(
            severity=severity,
            alert_type=alert_type,
            well_id=well_id or "unknown"
        ).inc()
    
    def record_ml_prediction(
        self,
        model_type: str,
        well_id: str,
        status: str = "success"
    ):
        """Record ML prediction metric"""
        ml_predictions_total.labels(
            model_type=model_type,
            well_id=well_id,
            status=status
        ).inc()
    
    def update_active_wells(self, count: int):
        """Update active wells gauge"""
        active_wells.set(count)
    
    def update_active_sensors(self, well_id: str, count: int):
        """Update active sensors gauge"""
        active_sensors.labels(well_id=well_id).set(count)
    
    def update_active_alerts(self, severity: str, count: int):
        """Update active alerts gauge"""
        active_alerts.labels(severity=severity).set(count)
    
    def update_data_ingestion_rate(self, source: str, rate: float):
        """Update data ingestion rate"""
        data_ingestion_rate.labels(source=source).set(rate)
    
    def record_db_query(self, query_type: str, duration: float):
        """Record database query metric"""
        db_query_duration_seconds.labels(query_type=query_type).observe(duration)
    
    def update_db_connections(self, active: int, idle: int):
        """Update database connection metrics"""
        db_connections_active.set(active)
        db_connections_idle.set(idle)
    
    def record_kafka_message_produced(self, topic: str):
        """Record Kafka message produced"""
        kafka_messages_produced.labels(topic=topic).inc()
    
    def record_kafka_message_consumed(self, topic: str):
        """Record Kafka message consumed"""
        kafka_messages_consumed.labels(topic=topic).inc()
    
    def update_kafka_consumer_lag(self, topic: str, partition: int, lag: int):
        """Update Kafka consumer lag"""
        kafka_consumer_lag.labels(topic=topic, partition=partition).set(lag)
    
    def record_redis_operation(self, operation: str, status: str = "success"):
        """Record Redis operation"""
        redis_operations_total.labels(operation=operation, status=status).inc()
    
    def record_redis_cache_hit(self):
        """Record Redis cache hit"""
        redis_cache_hits.inc()
    
    def record_redis_cache_miss(self):
        """Record Redis cache miss"""
        redis_cache_misses.inc()
    
    def get_metrics_summary(self, db: Session) -> Dict[str, Any]:
        """Get summary of all metrics"""
        try:
            # Get active wells count
            wells_count = db.execute(
                text("SELECT COUNT(*) FROM wells WHERE is_active = true")
            ).scalar()
            
            # Get active sensors count
            sensors_count = db.execute(
                text("SELECT COUNT(*) FROM sensors WHERE is_active = true")
            ).scalar()
            
            # Get active alerts count by severity
            alerts_by_severity = db.execute(
                text("""
                    SELECT severity, COUNT(*) 
                    FROM alerts 
                    WHERE status = 'active' 
                    GROUP BY severity
                """)
            ).fetchall()
            
            alerts_dict = {row[0]: row[1] for row in alerts_by_severity}
            
            # Get sensor readings in last hour
            readings_count = db.execute(
                text("""
                    SELECT COUNT(*) 
                    FROM sensor_readings 
                    WHERE timestamp >= NOW() - INTERVAL '1 hour'
                """)
            ).scalar()
            
            # Get alerts in last hour
            alerts_count = db.execute(
                text("""
                    SELECT COUNT(*) 
                    FROM alerts 
                    WHERE created_at >= NOW() - INTERVAL '1 hour'
                """)
            ).scalar()
            
            return {
                "active_wells": wells_count or 0,
                "active_sensors": sensors_count or 0,
                "active_alerts_by_severity": alerts_dict,
                "sensor_readings_last_hour": readings_count or 0,
                "alerts_last_hour": alerts_count or 0,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting metrics summary: {e}")
            return {
                "active_wells": 0,
                "active_sensors": 0,
                "active_alerts_by_severity": {},
                "sensor_readings_last_hour": 0,
                "alerts_last_hour": 0,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_prometheus_metrics(self) -> bytes:
        """Get Prometheus metrics in text format"""
        return generate_latest(metrics_registry)


# Global metrics service instance
metrics_service = MetricsService()

