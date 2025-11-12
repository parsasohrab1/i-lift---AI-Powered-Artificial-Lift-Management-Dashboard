# User Guide

راهنمای کاربری IntelliLift AI Dashboard

## Getting Started

### Login

1. باز کردن مرورگر و رفتن به `http://localhost:3000`
2. وارد کردن username و password
3. کلیک روی "Login"

### Dashboard Overview

پس از login، به صفحه Dashboard هدایت می‌شوید که شامل:

- **KPI Widgets**: شاخص‌های کلیدی عملکرد
- **Real-time Metrics**: متریک‌های real-time
- **Well Status**: وضعیت چاه‌ها
- **Active Alerts**: هشدارهای فعال
- **Activity Feed**: فید فعالیت‌ها

## Navigation

### Main Menu

- **Dashboard**: صفحه اصلی
- **Wells**: مدیریت چاه‌ها
- **Sensors**: مدیریت سنسورها
- **Alerts**: مدیریت هشدارها
- **Analytics**: تحلیل‌ها
- **ML Predictions**: پیش‌بینی‌های ML
- **Monitoring**: مانیتورینگ سیستم
- **Settings**: تنظیمات

## Features

### Wells Management

#### Viewing Wells

1. رفتن به "Wells" از منوی اصلی
2. مشاهده لیست تمام چاه‌ها
3. فیلتر کردن بر اساس status, type, location

#### Creating a Well

1. کلیک روی "Add Well"
2. پر کردن فرم:
   - Name
   - Location
   - Coordinates (Latitude, Longitude)
   - Well Type (ESP, PCP, Gas Lift, Rod Pump)
3. کلیک روی "Create"

#### Viewing Well Details

1. کلیک روی یک well از لیست
2. مشاهده:
   - اطلاعات کلی
   - سنسورها
   - داده‌های real-time
   - تاریخچه
   - Alerts

### Sensors Management

#### Viewing Sensors

1. رفتن به "Sensors"
2. مشاهده لیست سنسورها
3. فیلتر بر اساس well, type, status

#### Sensor Readings

1. کلیک روی یک sensor
2. مشاهده:
   - Current value
   - Historical chart
   - Statistics
   - Quality metrics

### Alerts

#### Viewing Alerts

1. رفتن به "Alerts"
2. مشاهده لیست alerts
3. فیلتر بر اساس:
   - Status (Active, Resolved)
   - Severity (Critical, Warning, Info)
   - Well
   - Date range

#### Resolving Alerts

1. کلیک روی یک alert
2. مشاهده جزئیات
3. کلیک روی "Resolve"
4. وارد کردن resolution notes
5. کلیک روی "Confirm"

### Analytics

#### KPIs

1. رفتن به "Analytics" > "KPIs"
2. انتخاب well و time range
3. مشاهده:
   - Total readings
   - Average values
   - Min/Max values
   - Trends

#### Trends

1. رفتن به "Analytics" > "Trends"
2. انتخاب:
   - Well(s)
   - Metric
   - Time range
3. مشاهده trend chart

#### Comparison

1. رفتن به "Analytics" > "Comparison"
2. انتخاب چند well
3. انتخاب metric
4. مشاهده مقایسه

### ML Predictions

#### Viewing Predictions

1. رفتن به "ML Predictions"
2. مشاهده:
   - Anomaly detection results
   - Predictive maintenance forecasts
   - Failure predictions

#### Running Anomaly Detection

1. رفتن به "ML Predictions" > "Anomaly Detection"
2. انتخاب:
   - Well
   - Sensor type
   - Time range
3. کلیک روی "Detect Anomalies"
4. مشاهده results

### Monitoring

#### System Health

1. رفتن به "Monitoring"
2. مشاهده:
   - Overall system status
   - Database health
   - Redis health
   - System resources (CPU, Memory)

#### Metrics

1. رفتن به "Monitoring" > "Metrics"
2. مشاهده:
   - Business metrics
   - System metrics
   - Performance metrics

## Tips & Tricks

### Keyboard Shortcuts

- `Ctrl + K`: Quick search
- `Esc`: Close modal
- `Ctrl + /`: Show shortcuts

### Filters

- استفاده از filters برای محدود کردن نتایج
- ذخیره filters برای استفاده بعدی
- Export filtered data

### Charts

- Zoom in/out با scroll
- Hover برای مشاهده مقادیر دقیق
- Download chart به عنوان image

## Troubleshooting

### Common Issues

#### Cannot Login

- بررسی username و password
- بررسی اتصال به اینترنت
- تماس با administrator

#### Data Not Loading

- Refresh صفحه
- بررسی اتصال به backend
- Clear browser cache

#### Charts Not Displaying

- بررسی داده‌های موجود
- بررسی time range
- Refresh صفحه

## Support

برای کمک و پشتیبانی:
- **Documentation**: مراجعه به مستندات
- **Issues**: گزارش مشکل در GitHub
- **Email**: support@example.com

