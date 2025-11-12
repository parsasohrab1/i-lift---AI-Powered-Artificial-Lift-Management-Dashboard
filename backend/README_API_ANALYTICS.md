# API Endpoints برای Analytics

راهنمای کامل API Endpoints برای Analytics و KPI

## Base URL
```
http://localhost:8000/api/v1/analytics
```

## Authentication
تمام endpointها نیاز به authentication دارند:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## Endpoints

### 1. دریافت KPI Analytics

**GET** `/api/v1/analytics/kpi`

دریافت KPI analytics برای چاه‌ها

**Query Parameters:**
- `well_id` (optional): فیلتر بر اساس well ID
- `start_time` (optional): زمان شروع (ISO format)
- `end_time` (optional): زمان پایان (ISO format)

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/kpi?well_id=Well_01" \
  -H "Authorization: Bearer TOKEN"
```

**Response:**
```json
{
  "kpis": {
    "total_readings": 10000,
    "active_wells": 5,
    "time_range": {
      "start": "2024-01-01T00:00:00Z",
      "end": "2024-01-31T23:59:59Z"
    },
    "motor_temperature_avg": 75.2,
    "motor_temperature_min": 65.0,
    "motor_temperature_max": 95.0,
    "intake_pressure_avg": 525.5,
    "flow_rate_avg": 2000.0,
    "average_efficiency": 40.5,
    "data_quality_percentage": 95.2,
    "average_pressure_differential": 475.0
  }
}
```

### 2. دریافت Trend Analysis

**GET** `/api/v1/analytics/trends`

تحلیل روند برای یک metric

**Query Parameters:**
- `well_id` (required): Well ID
- `metric` (required): نام metric (temperature, pressure, flow, vibration, current)
- `days` (default: 30, max: 365): تعداد روزها

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/trends?well_id=Well_01&metric=temperature&days=30" \
  -H "Authorization: Bearer TOKEN"
```

**Response:**
```json
{
  "well_id": "Well_01",
  "metric": "temperature",
  "sensor_type": "motor_temperature",
  "time_range": {
    "start": "2024-01-01T00:00:00Z",
    "end": "2024-01-31T23:59:59Z",
    "days": 30
  },
  "data_points": [
    {
      "date": "2024-01-01T00:00:00Z",
      "avg": 75.2,
      "min": 72.0,
      "max": 78.5,
      "count": 24
    }
  ],
  "trend": {
    "direction": "increasing",
    "slope": 0.15,
    "strength": 0.8,
    "intercept": 74.5
  },
  "statistics": {
    "current": 76.5,
    "average": 75.2,
    "change_percent": 1.7
  }
}
```

### 3. مقایسه چاه‌ها (Comparison)

**GET** `/api/v1/analytics/comparison`

مقایسه چند چاه برای یک metric

**Query Parameters:**
- `well_ids` (required): لیست well IDs (2-10 چاه)
- `metric` (required): metric برای مقایسه
- `start_time` (optional): زمان شروع
- `end_time` (optional): زمان پایان

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/comparison?well_ids=Well_01&well_ids=Well_02&well_ids=Well_03&metric=flow" \
  -H "Authorization: Bearer TOKEN"
```

**Response:**
```json
{
  "metric": "flow",
  "sensor_type": "flow_rate",
  "time_range": {
    "start": "2024-01-01T00:00:00Z",
    "end": "2024-01-31T23:59:59Z"
  },
  "wells": {
    "Well_01": {
      "avg": 2100.5,
      "min": 1800.0,
      "max": 2400.0,
      "std": 150.2,
      "count": 720
    },
    "Well_02": {
      "avg": 1950.0,
      "min": 1700.0,
      "max": 2200.0,
      "std": 120.5,
      "count": 720
    }
  },
  "rankings": {
    "Well_01": 1,
    "Well_02": 2
  },
  "best_performer": "Well_01",
  "worst_performer": "Well_02"
}
```

### 4. دریافت Performance Metrics

**GET** `/api/v1/analytics/performance`

دریافت معیارهای عملکرد

**Query Parameters:**
- `well_id` (optional): فیلتر بر اساس well ID
- `start_time` (optional): زمان شروع
- `end_time` (optional): زمان پایان

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/performance" \
  -H "Authorization: Bearer TOKEN"
```

**Response:**
```json
{
  "total_readings": 50000,
  "active_wells": 10,
  "data_quality_score": 95.5,
  "average_efficiency": 40.2,
  "time_range": {
    "start": "2024-01-01T00:00:00Z",
    "end": "2024-01-31T23:59:59Z"
  },
  "well_performance": {
    "Well_01": {
      "readings_count": 5000,
      "sensor_types": ["motor_temperature", "intake_pressure", "flow_rate"]
    }
  }
}
```

### 5. دریافت Time Series Data

**GET** `/api/v1/analytics/timeseries`

دریافت داده‌های time series برای visualization

**Query Parameters:**
- `well_id` (required): Well ID
- `sensor_type` (required): نوع سنسور
- `start_time` (required): زمان شروع
- `end_time` (required): زمان پایان
- `aggregation` (default: "hourly"): سطح aggregation (raw, hourly, daily)
- `limit` (default: 1000, max: 10000): حداکثر تعداد data points

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/timeseries?well_id=Well_01&sensor_type=motor_temperature&start_time=2024-01-01T00:00:00Z&end_time=2024-01-07T00:00:00Z&aggregation=daily" \
  -H "Authorization: Bearer TOKEN"
```

**Response:**
```json
{
  "metric": "motor_temperature",
  "sensor_type": "motor_temperature",
  "data_points": [
    {
      "timestamp": "2024-01-01T00:00:00Z",
      "value": 75.2,
      "well_id": "Well_01"
    }
  ],
  "time_range": {
    "start": "2024-01-01T00:00:00Z",
    "end": "2024-01-07T00:00:00Z"
  }
}
```

### 6. دریافت Analytics Summary

**GET** `/api/v1/analytics/summary`

دریافت خلاصه کامل analytics

**Query Parameters:**
- `well_id` (optional): فیلتر بر اساس well ID
- `days` (default: 30, max: 365): تعداد روزها

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/summary?days=7" \
  -H "Authorization: Bearer TOKEN"
```

**Response:**
```json
{
  "kpis": {...},
  "performance": {...},
  "time_range": {
    "start": "2024-01-25T00:00:00Z",
    "end": "2024-02-01T00:00:00Z",
    "days": 7
  }
}
```

## Metrics پشتیبانی شده

- `temperature` → motor_temperature
- `pressure` → intake_pressure
- `flow` → flow_rate
- `vibration` → vibration
- `current` → current

## KPIs محاسبه شده

### Basic KPIs:
- `total_readings`: تعداد کل readings
- `active_wells`: تعداد چاه‌های فعال
- `data_quality_percentage`: درصد کیفیت داده

### Sensor-specific KPIs:
- `{sensor_type}_avg`: میانگین
- `{sensor_type}_min`: حداقل
- `{sensor_type}_max`: حداکثر
- `{sensor_type}_std`: انحراف معیار

### Derived KPIs:
- `average_efficiency`: میانگین کارایی (flow_rate / current)
- `average_pressure_differential`: تفاضل فشار (discharge - intake)

## Trend Analysis

### Trend Direction:
- `increasing`: روند صعودی
- `decreasing`: روند نزولی
- `stable`: روند ثابت

### Trend Strength:
- محاسبه شده بر اساس slope و standard deviation
- هرچه بیشتر باشد، روند قوی‌تر است

## Permissions

- `VIEW_ANALYTICS`: برای مشاهده analytics
- `EXPORT_ANALYTICS`: برای export داده‌ها

## Best Practices

1. **Time Ranges**: محدوده زمانی را محدود کنید (max 1 year)
2. **Aggregation**: برای داده‌های تاریخی از aggregation استفاده کنید
3. **Caching**: نتایج analytics را cache کنید
4. **Pagination**: برای time series از limit استفاده کنید
5. **Comparison**: حداکثر 10 چاه را همزمان مقایسه کنید

## Performance Tips

- از aggregation برای کاهش حجم داده استفاده کنید
- برای real-time analytics از cache استفاده کنید
- محدوده زمانی را محدود کنید
- از indexes در database استفاده کنید

