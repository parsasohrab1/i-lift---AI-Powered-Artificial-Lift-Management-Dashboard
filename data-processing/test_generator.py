"""
Test script for Synthetic Data Generator
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from synthetic_data_generator import SyntheticALSDataGenerator


def test_basic_generation():
    """Test basic data generation"""
    print("=" * 60)
    print("Test 1: Basic Data Generation")
    print("=" * 60)
    
    generator = SyntheticALSDataGenerator(seed=42)
    
    start_date = datetime.now() - timedelta(days=7)  # 7 days for quick test
    df = generator.generate_well_data(
        well_id="Test_Well_01",
        start_date=start_date,
        days=7,
        interval_seconds=60,  # 1 minute intervals for faster generation
        include_anomalies=True,
        include_failures=False,
    )
    
    print(f"✓ Generated {len(df):,} records")
    print(f"✓ Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"✓ Columns: {list(df.columns)}")
    print(f"✓ Memory usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
    
    # Check data quality
    assert len(df) > 0, "DataFrame is empty"
    assert 'well_id' in df.columns, "Missing well_id column"
    assert 'timestamp' in df.columns, "Missing timestamp column"
    assert all(col in df.columns for col in generator.sensor_specs.keys()), "Missing sensor columns"
    
    print("✓ All basic tests passed!\n")
    return df


def test_multiple_wells():
    """Test multiple wells generation"""
    print("=" * 60)
    print("Test 2: Multiple Wells Generation")
    print("=" * 60)
    
    generator = SyntheticALSDataGenerator(seed=42)
    
    start_date = datetime.now() - timedelta(days=1)
    well_ids = ["Well_01", "Well_02", "Well_03"]
    
    df = generator.generate_multiple_wells(
        well_ids=well_ids,
        start_date=start_date,
        days=1,
        interval_seconds=300,  # 5 minute intervals
    )
    
    print(f"✓ Generated {len(df):,} records for {len(well_ids)} wells")
    print(f"✓ Unique wells: {df['well_id'].unique().tolist()}")
    print(f"✓ Records per well: {df['well_id'].value_counts().to_dict()}")
    
    assert len(df['well_id'].unique()) == len(well_ids), "Wrong number of wells"
    print("✓ All multiple wells tests passed!\n")
    return df


def test_failure_scenarios():
    """Test failure scenario generation"""
    print("=" * 60)
    print("Test 3: Failure Scenarios")
    print("=" * 60)
    
    generator = SyntheticALSDataGenerator(seed=42)
    
    start_date = datetime.now() - timedelta(days=30)
    df = generator.generate_well_data(
        well_id="Failing_Well",
        start_date=start_date,
        days=30,
        interval_seconds=3600,  # 1 hour intervals
        include_failures=True,
        failure_probability=1.0,  # 100% failure
    )
    
    # Check if failure pattern exists (values should change in last 10%)
    last_10_percent = int(len(df) * 0.9)
    temp_start = df['motor_temperature'].iloc[last_10_percent - 100:last_10_percent].mean()
    temp_end = df['motor_temperature'].iloc[-100:].mean()
    
    print(f"✓ Temperature at start of failure period: {temp_start:.2f}°C")
    print(f"✓ Temperature at end: {temp_end:.2f}°C")
    print(f"✓ Temperature increase: {temp_end - temp_start:.2f}°C")
    
    # Failure should show increase in temperature
    assert temp_end > temp_start, "Failure scenario not detected"
    print("✓ Failure scenario test passed!\n")
    return df


def test_export_formats():
    """Test export to different formats"""
    print("=" * 60)
    print("Test 4: Export Formats")
    print("=" * 60)
    
    generator = SyntheticALSDataGenerator(seed=42)
    
    start_date = datetime.now() - timedelta(days=1)
    df = generator.generate_well_data(
        well_id="Export_Test",
        start_date=start_date,
        days=1,
        interval_seconds=3600,
    )
    
    output_dir = Path("data/test_output")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Test Parquet export
    parquet_path = output_dir / "test_data.parquet"
    generator.export_to_parquet(df, parquet_path)
    assert parquet_path.exists(), "Parquet file not created"
    print(f"✓ Parquet export: {parquet_path}")
    
    # Test CSV export
    csv_path = output_dir / "test_data.csv"
    generator.export_to_csv(df, csv_path)
    assert csv_path.exists(), "CSV file not created"
    print(f"✓ CSV export: {csv_path}")
    
    # Test JSON export
    json_path = output_dir / "test_data.json"
    generator.export_to_json(df.head(100), json_path)
    assert json_path.exists(), "JSON file not created"
    print(f"✓ JSON export: {json_path}")
    
    print("✓ All export format tests passed!\n")


def test_statistics():
    """Test statistics generation"""
    print("=" * 60)
    print("Test 5: Statistics")
    print("=" * 60)
    
    generator = SyntheticALSDataGenerator(seed=42)
    
    start_date = datetime.now() - timedelta(days=7)
    df = generator.generate_well_data(
        well_id="Stats_Test",
        start_date=start_date,
        days=7,
        interval_seconds=3600,
    )
    
    stats = generator.get_statistics(df)
    
    print(f"✓ Total records: {stats['total_records']:,}")
    print(f"✓ Wells: {stats['wells']}")
    print(f"✓ Sensors: {stats['sensors']}")
    print(f"✓ Date range: {stats['date_range']['start']} to {stats['date_range']['end']}")
    
    assert stats['total_records'] == len(df), "Record count mismatch"
    assert len(stats['sensor_statistics']) > 0, "No sensor statistics"
    
    print("✓ Statistics test passed!\n")


def test_derived_metrics():
    """Test derived metrics calculation"""
    print("=" * 60)
    print("Test 6: Derived Metrics")
    print("=" * 60)
    
    generator = SyntheticALSDataGenerator(seed=42)
    
    start_date = datetime.now() - timedelta(days=1)
    df = generator.generate_well_data(
        well_id="Metrics_Test",
        start_date=start_date,
        days=1,
        interval_seconds=3600,
    )
    
    # Check derived metrics
    if 'pressure_differential' in df.columns:
        print(f"✓ Pressure differential calculated")
        assert df['pressure_differential'].notna().any(), "Pressure differential is all NaN"
    
    if 'efficiency' in df.columns:
        print(f"✓ Efficiency metric calculated")
        assert df['efficiency'].notna().any(), "Efficiency is all NaN"
    
    if 'temperature_rise_rate' in df.columns:
        print(f"✓ Temperature rise rate calculated")
    
    print("✓ Derived metrics test passed!\n")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Synthetic Data Generator - Test Suite")
    print("=" * 60 + "\n")
    
    try:
        # Run all tests
        test_basic_generation()
        test_multiple_wells()
        test_failure_scenarios()
        test_export_formats()
        test_statistics()
        test_derived_metrics()
        
        print("=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

