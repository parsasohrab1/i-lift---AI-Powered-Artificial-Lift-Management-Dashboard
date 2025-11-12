# Quick Start Guide - Synthetic Data Generator

راهنمای سریع برای استفاده از Synthetic Data Generator

## نصب وابستگی‌ها

```bash
pip install pandas numpy
```

## استفاده سریع

### 1. تولید داده ساده

```python
from synthetic_data_generator import SyntheticALSDataGenerator
from datetime import datetime, timedelta

# ایجاد generator
generator = SyntheticALSDataGenerator(seed=42)

# تولید داده برای یک چاه
df = generator.generate_well_data(
    well_id="Well_01",
    start_date=datetime.now() - timedelta(days=7),
    days=7,
    interval_seconds=60,  # هر 1 دقیقه
)

print(f"تولید شد: {len(df):,} رکورد")
```

### 2. تولید داده برای چند چاه

```python
well_ids = ["Well_01", "Well_02", "Well_03"]
df = generator.generate_multiple_wells(
    well_ids=well_ids,
    start_date=datetime.now() - timedelta(days=30),
    days=30,
)
```

### 3. Export به فایل

```python
# Export به Parquet (توصیه شده)
generator.export_to_parquet(df, "data/my_data.parquet")

# Export به CSV
generator.export_to_csv(df, "data/my_data.csv")

# Export به JSON (برای نمونه کوچک)
generator.export_to_json(df.head(1000), "data/sample.json")
```

### 4. مشاهده آمار

```python
stats = generator.get_statistics(df)
print(stats)
```

## مثال‌های کاربردی

### مثال 1: داده برای تست (1 روز)

```python
generator = SyntheticALSDataGenerator(seed=42)
df = generator.generate_well_data(
    well_id="Test_Well",
    start_date=datetime.now() - timedelta(days=1),
    days=1,
    interval_seconds=60,  # هر دقیقه
    include_failures=False,  # بدون failure
)
generator.export_to_parquet(df, "data/test_data.parquet")
```

### مثال 2: داده با Failure Scenario

```python
generator = SyntheticALSDataGenerator(seed=42)
df = generator.generate_well_data(
    well_id="Failing_Well",
    start_date=datetime.now() - timedelta(days=30),
    days=30,
    failure_probability=1.0,  # 100% احتمال failure
)
generator.export_to_parquet(df, "data/failure_data.parquet")
```

### مثال 3: داده برای ML Training (6 ماه)

```python
generator = SyntheticALSDataGenerator(seed=42)
well_ids = [f"Well_{i:02d}" for i in range(1, 21)]  # 20 چاه

df = generator.generate_multiple_wells(
    well_ids=well_ids,
    start_date=datetime.now() - timedelta(days=180),
    days=180,
    interval_seconds=3600,  # هر ساعت (برای کاهش حجم)
    include_anomalies=True,
    include_failures=True,
)

generator.export_to_parquet(df, "data/ml_training_data.parquet")
print(f"تولید شد: {len(df):,} رکورد")
```

## تست Generator

```bash
cd data-processing
python test_generator.py
```

این اسکریپت تمام قابلیت‌های generator را تست می‌کند.

## نکات مهم

1. **Memory**: برای datasets بزرگ، `interval_seconds` را افزایش دهید
2. **Reproducibility**: از `seed` برای تکرارپذیری استفاده کنید
3. **Format**: برای datasets بزرگ از Parquet استفاده کنید
4. **Performance**: 
   - 1 ثانیه interval: ~15.5M records/day
   - 60 ثانیه interval: ~1,440 records/day
   - 3600 ثانیه interval: ~24 records/day

## مشکلات رایج

### مشکل: Memory Error
**راه حل**: `interval_seconds` را افزایش دهید یا `days` را کاهش دهید

### مشکل: فایل خیلی بزرگ
**راه حل**: از Parquet با compression استفاده کنید یا interval را افزایش دهید

### مشکل: داده‌ها یکسان هستند
**راه حل**: `seed` را تغییر دهید یا حذف کنید

