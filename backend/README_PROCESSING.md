# راهنمای Data Processing Pipeline

Pipeline پردازش داده برای پردازش real-time داده‌های دریافتی از Kafka و ذخیره در پایگاه داده طراحی شده است.

## معماری Pipeline

```
[Kafka] → [Consumer] → [Stream Processor] → [Feature Engineer] → [Database Writer] → [TimescaleDB]
            ↓                ↓                      ↓                    ↓
        Message        Sliding Window        Statistical Features    Batch Insert
        Queue          Statistics            Time Features           Optimized
```

## مراحل پردازش

### 1. Kafka Consumer
- دریافت داده از Kafka topic `sensor-data`
- Deserialization JSON
- Error handling و retry

### 2. Stream Processing
- پردازش real-time با sliding window
- محاسبه آمار (mean, std, min, max)
- تشخیص anomaly با z-score
- محاسبه rate of change

### 3. Feature Engineering
- Time-based features (hour, day, month, cyclical)
- Statistical features (mean, std, percentiles)
- Trend features (slope, acceleration, volatility)
- Historical window analysis

### 4. Database Writer
- Batch writing برای بهینه‌سازی
- Bulk insert به TimescaleDB
- Error handling و retry

## استفاده

### راه‌اندازی Pipeline

#### از طریق API:
```bash
# Start pipeline
curl -X POST "http://localhost:8000/api/v1/processing/start" \
  -H "Authorization: Bearer ADMIN_TOKEN"

# Check stats
curl -X GET "http://localhost:8000/api/v1/processing/stats" \
  -H "Authorization: Bearer TOKEN"

# Health check
curl -X GET "http://localhost:8000/api/v1/processing/health" \
  -H "Authorization: Bearer TOKEN"

# Stop pipeline
curl -X POST "http://localhost:8000/api/v1/processing/stop" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

#### از طریق Script:
```bash
cd backend
python scripts/start_processing_pipeline.py
```

### کنترل Pipeline

```bash
# Pause
curl -X POST "http://localhost:8000/api/v1/processing/pause" \
  -H "Authorization: Bearer ADMIN_TOKEN"

# Resume
curl -X POST "http://localhost:8000/api/v1/processing/resume" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

## Features محاسبه شده

### Stream Processing Features
- `window_size`: تعداد readings در window
- `mean`: میانگین
- `median`: میانه
- `std`: انحراف معیار
- `min/max`: حداقل/حداکثر
- `range`: دامنه
- `change_from_mean`: تغییر از میانگین
- `change_percent`: درصد تغییر
- `rate_of_change`: نرخ تغییر
- `z_score`: Z-score
- `is_anomaly`: تشخیص anomaly

### Feature Engineering Features

#### Time Features:
- `hour`, `day_of_week`, `day_of_month`, `month`
- `is_weekend`
- `hour_sin/cos`, `day_sin/cos` (cyclical encoding)

#### Statistical Features:
- `mean`, `std`, `min`, `max`, `median`
- `percentile_25`, `percentile_75`
- `iqr` (Interquartile Range)

#### Trend Features:
- `trend`: شیب خط روند
- `acceleration`: شتاب تغییر
- `volatility`: نوسانات

#### Cyclical Features:
- `day_of_year`, `week_of_year`, `quarter`
- `day_of_year_sin/cos`

## پیکربندی

### Environment Variables:
```env
# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC_SENSOR_DATA=sensor-data

# Processing
BATCH_SIZE=100
WINDOW_SIZE=60
```

### Pipeline Parameters:
```python
pipeline = DataProcessingPipeline(
    batch_size=100,      # تعداد records در batch
    window_size=60,      # اندازه window به ثانیه
)
```

## Monitoring

### Statistics Response:
```json
{
  "total_processed": 10000,
  "total_errors": 5,
  "processing_rate": 50.5,
  "last_processed_time": 1234567890.123,
  "is_running": true,
  "database_writer": {
    "total_written": 10000,
    "total_errors": 0,
    "buffer_size": 45,
    "last_write_time": "2024-01-01T12:00:00Z"
  },
  "kafka_consumer_running": true
}
```

### Health Check Response:
```json
{
  "status": "healthy",
  "is_running": true,
  "kafka_connected": true,
  "total_processed": 10000,
  "total_errors": 5,
  "error_rate": 0.0005
}
```

## Performance Optimization

### Batch Writing
- داده‌ها در buffer جمع می‌شوند
- وقتی buffer پر شد یا flush شود، bulk insert انجام می‌شود
- کاهش تعداد write operations

### Sliding Window
- فقط داده‌های اخیر نگه داشته می‌شوند
- حافظه محدود با maxlen
- محاسبات سریع

### Error Handling
- خطاها log می‌شوند
- پردازش ادامه پیدا می‌کند
- آمار خطاها نگه داشته می‌شود

## Troubleshooting

### Pipeline Not Processing
1. بررسی کنید Kafka consumer متصل است
2. بررسی کنید Kafka topic وجود دارد
3. بررسی logs برای خطاها

### High Error Rate
1. بررسی format داده‌ها
2. بررسی database connection
3. بررسی validation errors

### Slow Processing
1. افزایش batch_size
2. کاهش window_size
3. بررسی database performance

## Best Practices

1. **Monitoring**: آمار pipeline را به صورت منظم بررسی کنید
2. **Error Handling**: خطاها را log و monitor کنید
3. **Batch Size**: batch_size را بر اساس throughput تنظیم کنید
4. **Window Size**: window_size را بر اساس نیاز analytics تنظیم کنید
5. **Health Checks**: health check را به صورت منظم اجرا کنید

## Integration با سایر Components

### با Ingestion:
- داده‌های validated از ingestion به Kafka می‌روند
- Pipeline از Kafka می‌خواند

### با Database:
- داده‌های processed به TimescaleDB ذخیره می‌شوند
- از hypertable برای بهینه‌سازی استفاده می‌شود

### با ML Services:
- Features engineered برای ML models آماده هستند
- می‌توانند برای training و prediction استفاده شوند

