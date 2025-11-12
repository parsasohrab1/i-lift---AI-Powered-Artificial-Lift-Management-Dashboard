# API Endpoints برای ML & Predictions

راهنمای کامل API Endpoints برای Machine Learning و Predictions

## Base URL
```
http://localhost:8000/api/v1/ml
```

## Authentication
تمام endpointها نیاز به authentication دارند:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## Endpoints

### 1. دریافت Predictions

**GET** `/api/v1/ml/predictions`

دریافت لیست predictions

**Query Parameters:**
- `well_id` (optional): فیلتر بر اساس well ID
- `model_type` (optional): فیلتر بر اساس model type
- `limit` (default: 100, max: 1000): تعداد predictions

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/ml/predictions?well_id=Well_01&model_type=predictive_maintenance" \
  -H "Authorization: Bearer TOKEN"
```

**Response:**
```json
[
  {
    "prediction_id": "uuid",
    "well_id": "Well_01",
    "model_type": "predictive_maintenance",
    "prediction_value": 0.75,
    "confidence_score": 0.85,
    "prediction_type": "failure_probability",
    "timestamp": "2024-01-01T12:00:00Z",
    "features": {
      "motor_temperature_mean": 78.5,
      "vibration_mean": 2.5
    }
  }
]
```

### 2. ایجاد Prediction جدید

**POST** `/api/v1/ml/predict`

ایجاد prediction جدید

**Request Body:**
```json
{
  "well_id": "Well_01",
  "model_type": "predictive_maintenance",
  "features": {
    "additional_feature": 123.45
  }
}
```

**Model Types:**
- `anomaly_detection`: تشخیص anomaly
- `predictive_maintenance`: پیش‌بینی خرابی
- `production_optimization`: بهینه‌سازی تولید

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/ml/predict" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "well_id": "Well_01",
    "model_type": "predictive_maintenance"
  }'
```

### 3. دریافت Anomalies

**GET** `/api/v1/ml/anomalies`

دریافت anomalies تشخیص داده شده

**Query Parameters:**
- `well_id` (optional): فیلتر بر اساس well ID
- `start_time` (optional): زمان شروع
- `end_time` (optional): زمان پایان
- `threshold` (default: 0.5): حد آستانه anomaly score

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/ml/anomalies?well_id=Well_01&threshold=0.7" \
  -H "Authorization: Bearer TOKEN"
```

**Response:**
```json
[
  {
    "prediction_id": "uuid",
    "well_id": "Well_01",
    "anomaly_score": 0.85,
    "confidence": 0.92,
    "timestamp": "2024-01-01T12:00:00Z",
    "features": {
      "latest_motor_temperature": 98.5,
      "latest_vibration": 4.5
    }
  }
]
```

### 4. دریافت Real-time Anomalies

**GET** `/api/v1/ml/anomalies/realtime`

دریافت anomalies در یک ساعت گذشته

**Query Parameters:**
- `well_id` (optional): فیلتر بر اساس well ID

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/ml/anomalies/realtime" \
  -H "Authorization: Bearer TOKEN"
```

### 5. دریافت Latest Predictions

**GET** `/api/v1/ml/predictions/latest`

دریافت آخرین prediction برای هر well/model

**Query Parameters:**
- `well_id` (optional): فیلتر بر اساس well ID
- `model_type` (optional): فیلتر بر اساس model type

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/ml/predictions/latest" \
  -H "Authorization: Bearer TOKEN"
```

### 6. دریافت لیست Models

**GET** `/api/v1/ml/models`

دریافت لیست models موجود

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/ml/models" \
  -H "Authorization: Bearer TOKEN"
```

**Response:**
```json
[
  {
    "model_type": "anomaly_detection",
    "model_name": "Anomaly Detection Model",
    "version": "1.0.0",
    "status": "active",
    "accuracy": 0.92,
    "last_trained": "2024-01-01T00:00:00Z",
    "description": "Detects anomalies in sensor data"
  }
]
```

### 7. دریافت Model Performance

**GET** `/api/v1/ml/models/{model_type}/performance`

دریافت معیارهای عملکرد model

**Path Parameters:**
- `model_type`: نوع model

**Query Parameters:**
- `start_time` (optional): زمان شروع
- `end_time` (optional): زمان پایان

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/ml/models/predictive_maintenance/performance" \
  -H "Authorization: Bearer TOKEN"
```

**Response:**
```json
{
  "model_type": "predictive_maintenance",
  "total_predictions": 1000,
  "average_confidence": 0.85,
  "predictions_by_well": {
    "Well_01": 250,
    "Well_02": 300
  },
  "time_range": {
    "start": "2024-01-01T00:00:00Z",
    "end": "2024-01-31T23:59:59Z"
  }
}
```

### 8. Training Model

**POST** `/api/v1/ml/models/train`

آموزش model جدید (admin only)

**Request Body:**
```json
{
  "model_type": "anomaly_detection",
  "well_ids": ["Well_01", "Well_02"],
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-06-30T23:59:59Z",
  "parameters": {
    "n_estimators": 100,
    "contamination": 0.1
  }
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/ml/models/train" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model_type": "anomaly_detection",
    "well_ids": ["Well_01", "Well_02"]
  }'
```

**Response:**
```json
{
  "training_id": "uuid",
  "model_type": "anomaly_detection",
  "status": "started",
  "message": "Training started for anomaly_detection model",
  "started_at": "2024-01-01T12:00:00Z",
  "completed_at": null,
  "metrics": null
}
```

## Model Types

### 1. Anomaly Detection
- **Type**: `anomaly_detection`
- **Output**: Anomaly score (0-1)
- **Use Case**: تشخیص anomalies در داده‌های سنسور

### 2. Predictive Maintenance
- **Type**: `predictive_maintenance`
- **Output**: Failure probability (0-1)
- **Use Case**: پیش‌بینی احتمال خرابی تجهیزات

### 3. Production Optimization
- **Type**: `production_optimization`
- **Output**: Optimal value (e.g., optimal flow rate)
- **Use Case**: بهینه‌سازی پارامترهای تولید

## Prediction Types

- `anomaly_score`: نمره anomaly (0-1)
- `failure_probability`: احتمال خرابی (0-1)
- `optimal_value`: مقدار بهینه

## Features

Features به صورت خودکار از آخرین sensor readings استخراج می‌شوند:
- Statistical features (mean, min, max, std)
- Latest sensor values
- Trend features

همچنین می‌توانید features اضافی در request ارسال کنید.

## Permissions

- `VIEW_ML_PREDICTIONS`: برای مشاهده predictions
- `CREATE_ML_PREDICTIONS`: برای ایجاد prediction
- `TRAIN_MODELS`: برای آموزش models (admin only)

## Best Practices

1. **Caching**: از `/predictions/latest` برای real-time استفاده کنید
2. **Threshold**: threshold مناسب برای anomalies تنظیم کنید
3. **Features**: features اضافی را در صورت نیاز ارسال کنید
4. **Monitoring**: model performance را به صورت منظم بررسی کنید
5. **Training**: models را به صورت دوره‌ای retrain کنید

## Error Responses

### 403 Forbidden
```json
{
  "detail": "Permission denied: TRAIN_MODELS required"
}
```

### 400 Bad Request
```json
{
  "detail": "Invalid model_type. Must be one of: anomaly_detection, predictive_maintenance, production_optimization"
}
```

### 404 Not Found
```json
{
  "detail": "No sensor data found for well Well_01"
}
```

