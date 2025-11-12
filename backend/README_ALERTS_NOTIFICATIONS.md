# Alert System و Notifications

راهنمای کامل سیستم Alert و Notifications

## Overview

سیستم Alert شامل:
- **Alert Rules Engine**: تعریف و ارزیابی قوانین alert
- **Alert Detection Service**: تشخیص خودکار alerts از sensor data
- **Notification Service**: ارسال notifications از طریق کانال‌های مختلف
- **Alert Management**: مدیریت alerts (create, resolve, delete)

## Alert Rules

### Default Rules

سیستم با قوانین پیش‌فرض زیر شروع می‌شود:

1. **Motor Temperature Critical** (>95°C)
2. **Motor Temperature Warning** (>85°C)
3. **Motor Temperature Low** (<65°C)
4. **Intake Pressure Critical** (<400 PSI)
5. **Intake Pressure Warning** (<450 PSI)
6. **Vibration High** (>4.0 m/s²)
7. **Current High** (>75 A)
8. **Flow Rate Low** (<1500 bbl/day)

### Rule Conditions

- `gt`: Greater than threshold
- `lt`: Less than threshold
- `eq`: Equals threshold
- `between`: Between two thresholds

### Severity Levels

- `low`: نیاز به توجه
- `medium`: نیاز به بررسی
- `high`: نیاز به اقدام فوری
- `critical`: نیاز به اقدام فوری

## API Endpoints

### Alert Rules

#### GET `/api/v1/alert-rules/`
لیست تمام alert rules

#### POST `/api/v1/alert-rules/`
ایجاد alert rule جدید (admin only)

#### GET `/api/v1/alert-rules/{rule_id}`
دریافت alert rule خاص

#### PUT `/api/v1/alert-rules/{rule_id}`
به‌روزرسانی alert rule (admin only)

#### DELETE `/api/v1/alert-rules/{rule_id}`
حذف alert rule (admin only)

### Notifications

#### POST `/api/v1/notifications/send`
ارسال notification برای یک alert

#### GET `/api/v1/notifications/preferences`
دریافت تنظیمات notifications کاربر

#### PUT `/api/v1/notifications/preferences`
به‌روزرسانی تنظیمات notifications

## Notification Channels

### 1. Email
- برای alerts با severity medium و بالاتر
- قابل تنظیم برای هر کاربر

### 2. SMS
- برای alerts با severity critical
- نیاز به تنظیم SMS provider

### 3. Push Notifications
- برای تمام alerts
- Real-time browser notifications

### 4. Webhook
- برای integration با سیستم‌های خارجی
- POST request به URL مشخص

## Alert Detection

### Automatic Detection

`AlertDetectionService` به صورت خودکار:
1. Sensor readings را monitor می‌کند
2. آنها را با alert rules مقایسه می‌کند
3. Alerts را ایجاد می‌کند
4. Notifications را ارسال می‌کند

### Manual Detection

می‌توانید به صورت دستی یک well را check کنید:

```python
from app.services.alert_detection_service import AlertDetectionService

service = AlertDetectionService()
alerts = await service.check_well_status("Well_01")
```

## راه‌اندازی Alert Monitor

```bash
python backend/scripts/start_alert_monitor.py
```

این script به صورت continuous sensor data را monitor می‌کند و alerts ایجاد می‌کند.

## Notification Configuration

### Email Configuration

```python
# TODO: Configure SMTP settings in config.py
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "your-email@gmail.com"
SMTP_PASSWORD = "your-password"
```

### SMS Configuration

```python
# TODO: Configure SMS provider (Twilio, etc.)
SMS_PROVIDER = "twilio"
SMS_ACCOUNT_SID = "your-account-sid"
SMS_AUTH_TOKEN = "your-auth-token"
SMS_FROM_NUMBER = "+1234567890"
```

### Push Notifications

```python
# TODO: Configure push notification service
PUSH_SERVICE_URL = "https://your-push-service.com"
PUSH_API_KEY = "your-api-key"
```

## Example Usage

### ایجاد Alert Rule جدید

```bash
curl -X POST "http://localhost:8000/api/v1/alert-rules/" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "rule_id": "custom_rule_1",
    "name": "Custom Temperature Rule",
    "sensor_type": "motor_temperature",
    "condition": "gt",
    "threshold": 90.0,
    "severity": "high",
    "message_template": "Custom alert: {value}°C"
  }'
```

### ارسال Notification

```bash
curl -X POST "http://localhost:8000/api/v1/notifications/send" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "alert_id": "uuid",
    "channels": ["email", "push"],
    "recipients": ["user@example.com"]
  }'
```

## Alert Lifecycle

1. **Detection**: Alert rule triggered
2. **Creation**: Alert created in database
3. **Notification**: Notifications sent via channels
4. **Resolution**: Alert resolved by user
5. **Archival**: Alert archived (optional)

## Best Practices

1. **Rule Design**: قوانین را به گونه‌ای طراحی کنید که false positives کمتری داشته باشند
2. **Severity Levels**: از severity levels به درستی استفاده کنید
3. **Notification Channels**: برای هر severity level کانال مناسب انتخاب کنید
4. **Monitoring**: Alert monitor را به صورت continuous اجرا کنید
5. **Resolution**: Alerts را به موقع resolve کنید

## Integration

### با Sensor Service:
- Sensor readings به صورت خودکار check می‌شوند
- Alerts به صورت real-time ایجاد می‌شوند

### با ML Service:
- ML predictions می‌توانند triggers برای alerts باشند
- Anomaly detection alerts به صورت خودکار ایجاد می‌شوند

### با Dashboard:
- Alerts در dashboard نمایش داده می‌شوند
- Real-time updates برای alerts

