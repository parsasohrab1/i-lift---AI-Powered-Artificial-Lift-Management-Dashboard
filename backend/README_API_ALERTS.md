# API Endpoints برای Alerts

راهنمای کامل API Endpoints برای مدیریت Alerts

## Base URL
```
http://localhost:8000/api/v1/alerts
```

## Authentication
تمام endpointها نیاز به authentication دارند:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## Endpoints

### 1. دریافت لیست Alerts

**GET** `/api/v1/alerts/`

دریافت لیست alerts با فیلتر و pagination

**Query Parameters:**
- `well_id` (optional): فیلتر بر اساس well ID
- `severity` (optional): فیلتر بر اساس severity (low, medium, high, critical)
- `resolved` (optional): فیلتر بر اساس resolved status (true/false)
- `alert_type` (optional): فیلتر بر اساس alert type
- `start_time` (optional): زمان شروع
- `end_time` (optional): زمان پایان
- `limit` (default: 100, max: 1000): تعداد alerts
- `offset` (default: 0): offset برای pagination

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/alerts/?well_id=Well_01&severity=critical&resolved=false" \
  -H "Authorization: Bearer TOKEN"
```

**Response:**
```json
{
  "alerts": [
    {
      "alert_id": "uuid",
      "well_id": "Well_01",
      "alert_type": "temperature_high",
      "severity": "critical",
      "message": "Motor temperature exceeded critical threshold: 110°C",
      "sensor_type": "motor_temperature",
      "resolved": false,
      "created_at": "2024-01-01T12:00:00Z",
      "resolved_at": null
    }
  ],
  "total": 50,
  "offset": 0,
  "limit": 100
}
```

### 2. دریافت Unresolved Alerts

**GET** `/api/v1/alerts/unresolved`

دریافت alerts حل نشده (cached, 30 ثانیه)

**Query Parameters:**
- `well_id` (optional): فیلتر بر اساس well ID
- `severity` (optional): فیلتر بر اساس severity

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/alerts/unresolved?severity=critical" \
  -H "Authorization: Bearer TOKEN"
```

### 3. دریافت Critical Alerts

**GET** `/api/v1/alerts/critical`

دریافت critical alerts حل نشده

**Query Parameters:**
- `well_id` (optional): فیلتر بر اساس well ID

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/alerts/critical" \
  -H "Authorization: Bearer TOKEN"
```

### 4. دریافت Alert بر اساس ID

**GET** `/api/v1/alerts/{alert_id}`

دریافت alert خاص

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/alerts/uuid" \
  -H "Authorization: Bearer TOKEN"
```

### 5. ایجاد Alert جدید

**POST** `/api/v1/alerts/`

ایجاد alert جدید

**Request Body:**
```json
{
  "well_id": "Well_01",
  "alert_type": "temperature_high",
  "severity": "critical",
  "message": "Motor temperature exceeded critical threshold",
  "sensor_type": "motor_temperature"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/alerts/" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "well_id": "Well_01",
    "alert_type": "temperature_high",
    "severity": "critical",
    "message": "Temperature too high"
  }'
```

### 6. Resolve Alert

**POST** `/api/v1/alerts/{alert_id}/resolve`

حل کردن یک alert

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/alerts/uuid/resolve" \
  -H "Authorization: Bearer TOKEN"
```

**Response:**
```json
{
  "alert_id": "uuid",
  "well_id": "Well_01",
  "alert_type": "temperature_high",
  "severity": "critical",
  "message": "Motor temperature exceeded critical threshold",
  "resolved": true,
  "created_at": "2024-01-01T12:00:00Z",
  "resolved_at": "2024-01-01T13:30:00Z"
}
```

### 7. Bulk Resolve Alerts

**POST** `/api/v1/alerts/bulk-resolve`

حل کردن چند alert به صورت همزمان (max 100)

**Request Body:**
```json
{
  "alert_ids": ["uuid1", "uuid2", "uuid3"],
  "resolved_by": "username"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/alerts/bulk-resolve" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "alert_ids": ["uuid1", "uuid2"]
  }'
```

**Response:**
```json
{
  "total": 2,
  "resolved": 2,
  "failed": 0,
  "failed_ids": []
}
```

### 8. حذف Alert

**DELETE** `/api/v1/alerts/{alert_id}`

حذف alert (admin only)

**Example:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/alerts/uuid" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### 9. دریافت Alert Statistics

**GET** `/api/v1/alerts/statistics/summary`

دریافت آمار alerts

**Query Parameters:**
- `well_id` (optional): فیلتر بر اساس well ID
- `start_time` (optional): زمان شروع
- `end_time` (optional): زمان پایان
- `days` (default: 30, max: 365): تعداد روزها

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/alerts/statistics/summary?days=7" \
  -H "Authorization: Bearer TOKEN"
```

**Response:**
```json
{
  "total_alerts": 150,
  "resolved_count": 120,
  "unresolved_count": 30,
  "resolution_rate": 80.0,
  "severity_distribution": {
    "critical": 10,
    "high": 25,
    "medium": 50,
    "low": 65
  },
  "type_distribution": {
    "temperature_high": 40,
    "pressure_low": 30,
    "vibration_high": 20
  },
  "well_distribution": {
    "Well_01": 50,
    "Well_02": 40
  },
  "average_resolution_time_hours": 2.5,
  "time_range": {
    "start": "2024-01-01T00:00:00Z",
    "end": "2024-01-31T23:59:59Z"
  }
}
```

### 10. دریافت Real-time Alert Count

**GET** `/api/v1/alerts/realtime/count`

دریافت تعداد alerts در real-time (cached)

**Query Parameters:**
- `well_id` (optional): فیلتر بر اساس well ID
- `severity` (optional): فیلتر بر اساس severity

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/alerts/realtime/count" \
  -H "Authorization: Bearer TOKEN"
```

**Response:**
```json
{
  "total": 15,
  "by_severity": {
    "critical": 3,
    "high": 5,
    "medium": 4,
    "low": 3
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## Alert Types

انواع alerts پشتیبانی شده:
- `temperature_high`: دمای بالا
- `temperature_low`: دمای پایین
- `pressure_high`: فشار بالا
- `pressure_low`: فشار پایین
- `vibration_high`: ارتعاش بالا
- `current_high`: جریان بالا
- `flow_low`: جریان پایین
- `anomaly_detected`: anomaly تشخیص داده شده
- `equipment_failure`: خرابی تجهیزات
- `maintenance_due`: نیاز به maintenance

## Severity Levels

- `low`: کم (نیاز به توجه)
- `medium`: متوسط (نیاز به بررسی)
- `high`: بالا (نیاز به اقدام فوری)
- `critical`: بحرانی (نیاز به اقدام فوری)

## Permissions

- `VIEW_ALERTS`: برای مشاهده alerts
- `CREATE_ALERTS`: برای ایجاد alert
- `RESOLVE_ALERTS`: برای حل کردن alerts
- Admin: برای حذف alerts

## Best Practices

1. **Caching**: از `/unresolved` endpoint استفاده کنید که cached است
2. **Filtering**: از فیلترها برای کاهش حجم داده استفاده کنید
3. **Bulk Operations**: برای resolve کردن چند alert از bulk endpoint استفاده کنید
4. **Monitoring**: alert statistics را به صورت منظم بررسی کنید
5. **Real-time**: از `/realtime/count` برای dashboard استفاده کنید

## Error Responses

### 403 Forbidden
```json
{
  "detail": "Permission denied: RESOLVE_ALERTS required"
}
```

### 404 Not Found
```json
{
  "detail": "Alert not found"
}
```

### 400 Bad Request
```json
{
  "detail": "Invalid severity. Must be one of: low, medium, high, critical"
}
```

## Alert Lifecycle

1. **Created**: Alert ایجاد می‌شود
2. **Active**: Alert فعال است (unresolved)
3. **Resolved**: Alert حل می‌شود (resolved_at set)
4. **Deleted**: Alert حذف می‌شود (admin only)

## Integration با سایر Components

### با ML Service:
- ML predictions می‌توانند alerts ایجاد کنند
- Anomaly detection alerts به صورت خودکار ایجاد می‌شوند

### با Sensor Service:
- Sensor readings می‌توانند triggers برای alerts باشند
- Threshold-based alerts از sensor values استفاده می‌کنند

