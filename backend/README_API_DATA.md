# API Endpoints برای Data

راهنمای کامل API Endpoints برای کار با داده‌های سنسور

## Base URL
```
http://localhost:8000/api/v1/sensors
```

## Authentication
تمام endpointها نیاز به authentication دارند:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## Endpoints

### 1. دریافت لیست Sensor Readings

**GET** `/api/v1/sensors/`

دریافت لیست readings با فیلتر و pagination

**Query Parameters:**
- `well_id` (optional): فیلتر بر اساس well ID
- `sensor_type` (optional): فیلتر بر اساس نوع سنسور
- `start_time` (optional): زمان شروع (ISO format)
- `end_time` (optional): زمان پایان (ISO format)
- `limit` (default: 100, max: 1000): تعداد records
- `offset` (default: 0): offset برای pagination

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/sensors/?well_id=Well_01&sensor_type=motor_temperature&limit=50" \
  -H "Authorization: Bearer TOKEN"
```

**Response:**
```json
{
  "readings": [
    {
      "reading_id": "uuid",
      "well_id": "Well_01",
      "sensor_type": "motor_temperature",
      "sensor_value": 75.5,
      "measurement_unit": "C",
      "data_quality": 95,
      "timestamp": "2024-01-01T12:00:00Z",
      "created_at": "2024-01-01T12:00:01Z"
    }
  ],
  "total": 1000,
  "offset": 0,
  "limit": 50
}
```

### 2. دریافت Latest Readings

**GET** `/api/v1/sensors/latest`

دریافت آخرین reading برای هر sensor

**Query Parameters:**
- `well_id` (optional): فیلتر بر اساس well ID
- `sensor_type` (optional): فیلتر بر اساس نوع سنسور

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/sensors/latest?well_id=Well_01" \
  -H "Authorization: Bearer TOKEN"
```

### 3. دریافت Real-time Data

**GET** `/api/v1/sensors/realtime`

دریافت داده‌های real-time (cached, به‌روزرسانی هر 5 ثانیه)

**Query Parameters:**
- `well_id` (optional): فیلتر بر اساس well ID

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/sensors/realtime" \
  -H "Authorization: Bearer TOKEN"
```

**Response:**
```json
{
  "data": {
    "Well_01": {
      "motor_temperature": {
        "value": 75.5,
        "unit": "C",
        "timestamp": "2024-01-01T12:00:00Z",
        "quality": 95
      },
      "intake_pressure": {
        "value": 500.0,
        "unit": "psi",
        "timestamp": "2024-01-01T12:00:00Z",
        "quality": 98
      }
    }
  },
  "timestamp": "2024-01-01T12:00:05Z"
}
```

### 4. ایجاد Sensor Reading

**POST** `/api/v1/sensors/`

ایجاد reading جدید

**Request Body:**
```json
{
  "well_id": "Well_01",
  "sensor_type": "motor_temperature",
  "sensor_value": 75.5,
  "measurement_unit": "C",
  "data_quality": 95,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/sensors/" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "well_id": "Well_01",
    "sensor_type": "motor_temperature",
    "sensor_value": 75.5,
    "measurement_unit": "C"
  }'
```

### 5. دریافت Aggregated Data

**GET** `/api/v1/sensors/aggregated`

دریافت داده‌های aggregated (hourly, daily, weekly)

**Query Parameters:**
- `well_id` (required): Well ID
- `sensor_type` (required): نوع سنسور
- `start_time` (required): زمان شروع
- `end_time` (required): زمان پایان
- `aggregation` (default: "hourly"): نوع aggregation (hourly, daily, weekly)

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/sensors/aggregated?well_id=Well_01&sensor_type=motor_temperature&start_time=2024-01-01T00:00:00Z&end_time=2024-01-07T00:00:00Z&aggregation=daily" \
  -H "Authorization: Bearer TOKEN"
```

**Response:**
```json
[
  {
    "timestamp": "2024-01-01T00:00:00Z",
    "well_id": "Well_01",
    "sensor_type": "motor_temperature",
    "avg_value": 75.2,
    "min_value": 72.0,
    "max_value": 78.5,
    "std_value": 1.5,
    "count": 24
  }
]
```

### 6. دریافت Statistics

**GET** `/api/v1/sensors/statistics`

دریافت آمار برای sensor data

**Query Parameters:**
- `well_id` (optional): فیلتر بر اساس well ID
- `sensor_type` (optional): فیلتر بر اساس نوع سنسور
- `start_time` (optional): زمان شروع
- `end_time` (optional): زمان پایان

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/sensors/statistics?well_id=Well_01" \
  -H "Authorization: Bearer TOKEN"
```

**Response:**
```json
{
  "statistics": {
    "Well_01_motor_temperature": {
      "well_id": "Well_01",
      "sensor_type": "motor_temperature",
      "count": 10000,
      "avg": 75.2,
      "min": 65.0,
      "max": 95.0,
      "std": 3.5
    }
  }
}
```

### 7. Export Data

**GET** `/api/v1/sensors/export`

Export داده‌ها به فرمت‌های مختلف

**Query Parameters:**
- `well_id` (optional): فیلتر بر اساس well ID
- `sensor_type` (optional): فیلتر بر اساس نوع سنسور
- `start_time` (optional): زمان شروع
- `end_time` (optional): زمان پایان
- `format` (default: "csv"): فرمت export (csv, json, parquet)
- `limit` (default: 10000, max: 100000): تعداد records

**Example:**
```bash
# Export to CSV
curl -X GET "http://localhost:8000/api/v1/sensors/export?well_id=Well_01&format=csv" \
  -H "Authorization: Bearer TOKEN" \
  -o sensor_data.csv

# Export to JSON
curl -X GET "http://localhost:8000/api/v1/sensors/export?well_id=Well_01&format=json" \
  -H "Authorization: Bearer TOKEN" \
  -o sensor_data.json

# Export to Parquet
curl -X GET "http://localhost:8000/api/v1/sensors/export?well_id=Well_01&format=parquet" \
  -H "Authorization: Bearer TOKEN" \
  -o sensor_data.parquet
```

## Sensor Types

سنسورهای پشتیبانی شده:
- `motor_temperature` - دمای موتور (°C)
- `intake_pressure` - فشار ورودی (psi)
- `discharge_pressure` - فشار خروجی (psi)
- `vibration` - ارتعاش (g)
- `current` - جریان (A)
- `flow_rate` - نرخ جریان (bpd)

## Permissions

- `VIEW_SENSOR_DATA`: برای مشاهده داده‌ها
- `CREATE_SENSOR_DATA`: برای ایجاد reading جدید

## Error Responses

### 403 Forbidden
```json
{
  "detail": "Permission denied"
}
```

### 404 Not Found
```json
{
  "detail": "No data found"
}
```

### 400 Bad Request
```json
{
  "detail": "End time must be after start time"
}
```

## Best Practices

1. **Pagination**: برای datasets بزرگ از `limit` و `offset` استفاده کنید
2. **Caching**: از `/realtime` endpoint استفاده کنید که cached است
3. **Aggregation**: برای داده‌های تاریخی از `/aggregated` استفاده کنید
4. **Export**: برای export حجم زیاد، از Parquet استفاده کنید
5. **Time Ranges**: محدوده زمانی را محدود کنید (max 1 year برای aggregated)

## Rate Limiting

- Real-time endpoint: 5 second cache
- Other endpoints: No specific rate limit (depends on server config)

