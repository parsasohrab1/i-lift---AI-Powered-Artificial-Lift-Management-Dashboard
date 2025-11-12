# Monitoring و Observability

راهنمای کامل Monitoring و Observability features

## Overview

سیستم Monitoring و Observability شامل:
- **Metrics Collection**: جمع‌آوری metrics با Prometheus
- **Health Checks**: بررسی سلامت سرویس‌ها
- **System Monitoring**: مانیتورینگ منابع سیستم
- **Business Metrics**: metrics مربوط به business
- **Logging**: ثبت و مدیریت لاگ‌ها
- **Tracing**: ردیابی درخواست‌ها

## Metrics Collection

### Prometheus Integration

سیستم از Prometheus برای جمع‌آوری metrics استفاده می‌کند.

#### HTTP Metrics:
- `http_requests_total`: تعداد کل درخواست‌های HTTP
- `http_request_duration_seconds`: مدت زمان درخواست‌های HTTP
- `http_request_size_bytes`: حجم درخواست‌های HTTP

#### Business Metrics:
- `sensor_readings_total`: تعداد کل خوانش‌های سنسور
- `alerts_total`: تعداد کل alertها
- `ml_predictions_total`: تعداد کل پیش‌بینی‌های ML

#### System Metrics:
- `active_wells`: تعداد چاه‌های فعال
- `active_sensors`: تعداد سنسورهای فعال
- `active_alerts`: تعداد alertهای فعال
- `data_ingestion_rate`: نرخ ingestion داده

#### Database Metrics:
- `db_query_duration_seconds`: مدت زمان queryهای دیتابیس
- `db_connections_active`: اتصالات فعال دیتابیس
- `db_connections_idle`: اتصالات idle دیتابیس

#### Kafka Metrics:
- `kafka_messages_produced`: تعداد پیام‌های تولید شده
- `kafka_messages_consumed`: تعداد پیام‌های مصرف شده
- `kafka_consumer_lag`: lag مصرف‌کننده Kafka

#### Redis Metrics:
- `redis_operations_total`: تعداد کل عملیات Redis
- `redis_cache_hits`: تعداد cache hitها
- `redis_cache_misses`: تعداد cache missها

### Accessing Metrics

برای دسترسی به Prometheus metrics:

```bash
GET /api/v1/monitoring/metrics
```

این endpoint metrics را در فرمت Prometheus text format برمی‌گرداند.

## Health Checks

### Health Check Endpoints

#### Basic Health Check (Public):
```bash
GET /api/v1/monitoring/health
```

#### Detailed Health Check:
```bash
GET /api/v1/monitoring/health/detailed?include_system=true
```

این endpoint سلامت تمام سرویس‌ها را بررسی می‌کند:
- Database
- Redis
- Kafka
- ML Services (optional)
- System Resources (optional)

#### Health Summary:
```bash
GET /api/v1/monitoring/health/summary
```

برای dashboard - خلاصه سلامت سیستم

### Health Check Response

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "checks": {
    "database": {
      "status": "healthy",
      "response_time_ms": 2.5,
      "connection_pool": {
        "size": 10,
        "checked_in": 8,
        "checked_out": 2,
        "overflow": 0
      }
    },
    "redis": {
      "status": "healthy",
      "response_time_ms": 1.2,
      "connected_clients": 5,
      "used_memory_human": "10MB",
      "redis_version": "7.0.0"
    },
    "kafka": {
      "status": "healthy",
      "response_time_ms": 5.0,
      "topics_count": 3
    }
  }
}
```

## System Monitoring

### System Resources

سیستم منابع زیر را مانیتور می‌کند:
- **CPU**: درصد استفاده CPU
- **Memory**: استفاده از حافظه
- **Disk**: استفاده از دیسک

### Accessing System Metrics

```bash
GET /api/v1/monitoring/metrics/system
```

**Response:**
```json
{
  "status": "healthy",
  "cpu": {
    "percent": 45.2,
    "count": 8
  },
  "memory": {
    "total_gb": 16.0,
    "available_gb": 8.5,
    "used_percent": 46.9
  },
  "disk": {
    "total_gb": 500.0,
    "free_gb": 300.0,
    "used_percent": 40.0
  }
}
```

## Business Metrics

### Business Metrics Endpoint

```bash
GET /api/v1/monitoring/metrics/business?hours=24
```

**Response:**
```json
{
  "sensor_readings": 10000,
  "alerts": 25,
  "ml_predictions": 500,
  "active_wells": 10,
  "time_range": {
    "start": "2024-01-01T00:00:00Z",
    "end": "2024-01-02T00:00:00Z"
  }
}
```

### Metrics Summary

```bash
GET /api/v1/monitoring/metrics/summary
```

**Response:**
```json
{
  "active_wells": 10,
  "active_sensors": 50,
  "active_alerts_by_severity": {
    "critical": 2,
    "warning": 5,
    "info": 10
  },
  "sensor_readings_last_hour": 1000,
  "alerts_last_hour": 5,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Logging

### Structured Logging

سیستم از structured logging با structlog استفاده می‌کند.

### Log Levels

- **DEBUG**: اطلاعات debug
- **INFO**: اطلاعات عمومی
- **WARNING**: هشدارها
- **ERROR**: خطاها
- **CRITICAL**: خطاهای بحرانی

### Accessing Logs

```bash
GET /api/v1/monitoring/logs?level=ERROR&hours=24&limit=100
```

**Query Parameters:**
- `level`: Filter by log level (optional)
- `hours`: Hours to look back (default: 24)
- `limit`: Maximum number of logs (default: 100)

## Tracing

### Distributed Tracing

سیستم از distributed tracing برای ردیابی درخواست‌ها استفاده می‌کند.

### Accessing Traces

```bash
GET /api/v1/monitoring/tracing?service=backend&hours=1&limit=50
```

**Query Parameters:**
- `trace_id`: Filter by trace ID (optional)
- `service`: Filter by service (optional)
- `hours`: Hours to look back (default: 1)
- `limit`: Maximum number of traces (default: 50)

## Integration with Middleware

### Metrics Middleware

`LoggingMiddleware` به صورت خودکار metrics را ثبت می‌کند:
- HTTP request metrics
- Response time
- Status codes
- Request sizes

### Usage in Code

```python
from app.services.metrics_service import metrics_service

# Record sensor reading
metrics_service.record_sensor_reading(
    well_id="well-1",
    sensor_type="temperature",
    status="success"
)

# Record alert
metrics_service.record_alert(
    severity="critical",
    alert_type="temperature_high",
    well_id="well-1"
)

# Record ML prediction
metrics_service.record_ml_prediction(
    model_type="anomaly_detection",
    well_id="well-1",
    status="success"
)
```

## Prometheus Configuration

### Prometheus Scrape Config

```yaml
scrape_configs:
  - job_name: 'backend-api'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/api/v1/monitoring/metrics'
```

## Grafana Dashboards

### Recommended Dashboards

1. **System Health Dashboard**
   - Overall system status
   - Service health checks
   - System resources

2. **Business Metrics Dashboard**
   - Sensor readings
   - Alerts
   - ML predictions
   - Active wells/sensors

3. **Performance Dashboard**
   - HTTP request metrics
   - Response times
   - Error rates
   - Throughput

4. **Infrastructure Dashboard**
   - Database metrics
   - Redis metrics
   - Kafka metrics
   - Connection pools

## Alerting

### Metrics-Based Alerts

می‌توانید alertهای Prometheus بر اساس metrics ایجاد کنید:

```yaml
groups:
  - name: system_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        annotations:
          summary: "High error rate detected"
      
      - alert: HighResponseTime
        expr: http_request_duration_seconds{quantile="0.95"} > 1
        for: 5m
        annotations:
          summary: "High response time detected"
      
      - alert: DatabaseConnectionPoolExhausted
        expr: db_connections_active / db_connections_idle > 0.9
        for: 5m
        annotations:
          summary: "Database connection pool nearly exhausted"
```

## Best Practices

1. **Metrics Collection**: تمام عملیات مهم را instrument کنید
2. **Health Checks**: health check endpoints را به صورت منظم بررسی کنید
3. **Alerting**: alertهای مناسب برای metrics مهم تنظیم کنید
4. **Dashboard**: dashboardهای Grafana برای visualization ایجاد کنید
5. **Logging**: از structured logging استفاده کنید
6. **Tracing**: برای debugging از distributed tracing استفاده کنید

## Monitoring Stack

### Recommended Stack

- **Metrics**: Prometheus
- **Visualization**: Grafana
- **Logging**: ELK Stack یا Loki
- **Tracing**: Jaeger یا Zipkin
- **Alerting**: Alertmanager

## Performance Considerations

1. **Metrics Collection**: metrics collection overhead را minimize کنید
2. **Sampling**: برای high-volume metrics از sampling استفاده کنید
3. **Retention**: retention policy مناسب برای metrics تنظیم کنید
4. **Cardinality**: از high cardinality labels اجتناب کنید

