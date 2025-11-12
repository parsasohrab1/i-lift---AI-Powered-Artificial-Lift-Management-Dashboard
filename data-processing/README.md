# Synthetic Data Generator

ابزار تولید داده‌های سنتتیک واقع‌گرایانه برای سیستم‌های Artificial Lift.

## ویژگی‌ها

- ✅ تولید داده برای چندین چاه
- ✅ الگوهای واقع‌گرایانه (daily/weekly cycles)
- ✅ سناریوهای خرابی (failure scenarios)
- ✅ Anomalies تصادفی
- ✅ Export به فرمت‌های مختلف (Parquet, CSV, JSON)
- ✅ قابلیت تکرارپذیری با seed
- ✅ آمار و گزارش

## استفاده

### از طریق Command Line

```bash
cd data-processing
python synthetic_data_generator.py
```

این دستور داده‌های 6 ماهه برای 10 چاه تولید می‌کند.

### از طریق Python API

```python
from synthetic_data_generator import SyntheticALSDataGenerator
from datetime import datetime, timedelta

# Initialize generator
generator = SyntheticALSDataGenerator(seed=42)

# Generate data for one well
start_date = datetime.now() - timedelta(days=180)
df = generator.generate_well_data(
    well_id="Well_01",
    start_date=start_date,
    days=180,
    interval_seconds=1,
    include_anomalies=True,
    include_failures=True,
    failure_probability=0.1,
)

# Generate for multiple wells
well_ids = ["Well_01", "Well_02", "Well_03"]
df = generator.generate_multiple_wells(
    well_ids=well_ids,
    start_date=start_date,
    days=180,
)

# Export to different formats
generator.export_to_parquet(df, "data/synthetic_data.parquet")
generator.export_to_csv(df, "data/synthetic_data.csv")
generator.export_to_json(df.head(1000), "data/synthetic_data_sample.json")

# Get statistics
stats = generator.get_statistics(df)
print(stats)
```

### از طریق REST API

```bash
# Generate synthetic data
curl -X POST "http://localhost:8000/api/v1/synthetic-data/generate" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "well_ids": ["Well_01", "Well_02"],
    "days": 180,
    "interval_seconds": 1,
    "include_anomalies": true,
    "include_failures": true,
    "failure_probability": 0.1,
    "export_format": "parquet",
    "seed": 42
  }'

# Get statistics
curl -X GET "http://localhost:8000/api/v1/synthetic-data/stats?file_path=data/generated/synthetic_data_20240101_120000.parquet" \
  -H "Authorization: Bearer TOKEN"
```

## پارامترها

### generate_well_data()

- `well_id`: شناسه چاه
- `start_date`: تاریخ شروع
- `days`: تعداد روزها (پیش‌فرض: 180)
- `interval_seconds`: فاصله زمانی به ثانیه (پیش‌فرض: 1)
- `include_anomalies`: شامل anomalies (پیش‌فرض: True)
- `include_failures`: شامل failure scenarios (پیش‌فرض: True)
- `failure_probability`: احتمال خرابی (0-1, پیش‌فرض: 0.1)

## سنسورها

داده‌های تولید شده شامل این سنسورها هستند:

1. **motor_temperature**: دمای موتور (65-120°C)
2. **intake_pressure**: فشار ورودی (450-600 psi)
3. **discharge_pressure**: فشار خروجی (800-1200 psi)
4. **vibration**: ارتعاش (0.5-5.0 g)
5. **current**: جریان (30-80 A)
6. **flow_rate**: نرخ جریان (1500-2500 bpd)

## الگوهای داده

### Daily Cycle
تغییرات روزانه (day/night) با استفاده از sine wave

### Weekly Trend
روند هفتگی برای شبیه‌سازی برنامه تولید

### Gradual Drift
Drift تدریجی برای شبیه‌سازی aging تجهیزات

### Failure Scenarios
- **Temperature/Vibration**: افزایش تدریجی (overheating, bearing wear)
- **Pressure**: کاهش تدریجی (pump degradation)
- **Current**: نوسانات افزایشی (motor issues)
- **Flow Rate**: کاهش تدریجی (production decline)

### Anomalies
- 1% از داده‌ها شامل anomalies تصادفی
- Spike یا drop ناگهانی
- Magnitude: 2-5x standard deviation

## Export Formats

### Parquet (توصیه شده)
- فشرده و سریع
- مناسب برای datasets بزرگ
- حفظ انواع داده

### CSV
- سازگار با اکثر ابزارها
- قابل تقسیم به chunks برای فایل‌های بزرگ

### JSON
- مناسب برای API/testing
- محدود به نمونه‌های کوچک (تا 10K records)

## آمار و گزارش

```python
stats = generator.get_statistics(df)
# Returns:
# {
#   'total_records': 15552000,
#   'date_range': {...},
#   'wells': ['Well_01', ...],
#   'sensors': [...],
#   'sensor_statistics': {...},
#   'status_distribution': {...}
# }
```

## مثال‌ها

### تولید داده برای تست
```python
# 1 روز داده با interval 1 ثانیه
df = generator.generate_well_data(
    well_id="Test_Well",
    start_date=datetime.now() - timedelta(days=1),
    days=1,
    interval_seconds=1,
    include_failures=False,  # بدون failure برای تست
)
```

### تولید داده با failure
```python
# 30 روز با احتمال خرابی بالا
df = generator.generate_well_data(
    well_id="Well_08",
    start_date=datetime.now() - timedelta(days=30),
    days=30,
    failure_probability=0.5,  # 50% احتمال خرابی
)
```

### تولید داده برای ML Training
```python
# 6 ماه داده برای training
well_ids = [f"Well_{i:02d}" for i in range(1, 21)]  # 20 wells
df = generator.generate_multiple_wells(
    well_ids=well_ids,
    start_date=datetime.now() - timedelta(days=180),
    days=180,
    include_anomalies=True,
    include_failures=True,
)

# Export for ML
generator.export_to_parquet(df, "data/ml_training_data.parquet")
```

## نکات

1. **Memory**: برای datasets بزرگ، از Parquet استفاده کنید
2. **Reproducibility**: از seed برای تکرارپذیری استفاده کنید
3. **Performance**: interval_seconds را برای کاهش حجم داده افزایش دهید
4. **Realism**: failure_probability را بر اساس نیاز تنظیم کنید

