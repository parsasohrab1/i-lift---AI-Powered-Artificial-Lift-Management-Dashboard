"""
Enhanced Synthetic Data Generator for Artificial Lift Systems
Generates realistic sensor data with patterns, anomalies, and failure scenarios
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json
import random


class SyntheticALSDataGenerator:
    """Generate synthetic sensor data for Artificial Lift Systems"""
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize generator
        
        Args:
            seed: Random seed for reproducibility
        """
        if seed:
            np.random.seed(seed)
            random.seed(seed)
        
        # Sensor specifications with realistic ranges
        self.sensor_specs = {
            'motor_temperature': {
                'min': 65, 'max': 120, 'unit': 'C',
                'normal_mean': 75, 'normal_std': 3,
                'warning_threshold': 95, 'critical_threshold': 110
            },
            'intake_pressure': {
                'min': 450, 'max': 600, 'unit': 'psi',
                'normal_mean': 525, 'normal_std': 25,
                'warning_threshold': 580, 'critical_threshold': 590
            },
            'discharge_pressure': {
                'min': 800, 'max': 1200, 'unit': 'psi',
                'normal_mean': 1000, 'normal_std': 50,
                'warning_threshold': 1150, 'critical_threshold': 1180
            },
            'vibration': {
                'min': 0.5, 'max': 5.0, 'unit': 'g',
                'normal_mean': 2.0, 'normal_std': 0.3,
                'warning_threshold': 3.5, 'critical_threshold': 4.5
            },
            'current': {
                'min': 30, 'max': 80, 'unit': 'A',
                'normal_mean': 50, 'normal_std': 5,
                'warning_threshold': 70, 'critical_threshold': 75
            },
            'flow_rate': {
                'min': 1500, 'max': 2500, 'unit': 'bpd',
                'normal_mean': 2000, 'normal_std': 100,
                'warning_threshold': 2400, 'critical_threshold': 2450
            },
        }
        
        # Equipment statuses
        self.statuses = ['normal', 'warning', 'critical', 'maintenance', 'offline']
    
    def generate_well_data(
        self,
        well_id: str,
        start_date: datetime,
        days: int = 180,
        interval_seconds: int = 1,
        include_anomalies: bool = True,
        include_failures: bool = True,
        failure_probability: float = 0.1,
    ) -> pd.DataFrame:
        """
        Generate sensor data for a well
        
        Args:
            well_id: Well identifier
            start_date: Start date for data generation
            days: Number of days to generate
            interval_seconds: Data interval in seconds
            include_anomalies: Include random anomalies
            include_failures: Include failure scenarios
            failure_probability: Probability of failure (0-1)
        
        Returns:
            DataFrame with sensor readings
        """
        total_samples = days * 24 * 60 * 60 // interval_seconds
        timestamps = pd.date_range(
            start=start_date,
            periods=total_samples,
            freq=f'{interval_seconds}S'
        )
        
        # Generate base data for each sensor
        data = {
            'timestamp': timestamps,
            'well_id': well_id,
        }
        
        # Generate each sensor type
        for sensor_type, spec in self.sensor_specs.items():
            data[sensor_type] = self._generate_sensor_data(
                total_samples,
                sensor_type,
                spec,
                well_id,
                include_anomalies,
                include_failures,
                failure_probability
            )
        
        # Generate equipment status
        data['equipment_status'] = self._generate_status_data(
            total_samples,
            well_id,
            data,
            include_failures,
            failure_probability
        )
        
        # Add metadata
        data['data_quality'] = self._generate_quality_scores(total_samples)
        
        df = pd.DataFrame(data)
        
        # Add derived metrics
        df = self._add_derived_metrics(df)
        
        return df
    
    def _generate_sensor_data(
        self,
        n_samples: int,
        sensor_type: str,
        spec: Dict,
        well_id: str,
        include_anomalies: bool,
        include_failures: bool,
        failure_probability: float,
    ) -> np.ndarray:
        """Generate data for a specific sensor"""
        # Base normal distribution
        base_values = np.random.normal(
            spec['normal_mean'],
            spec['normal_std'],
            n_samples
        )
        
        # Add daily cycle (simulate day/night variations)
        daily_cycle = np.sin(2 * np.pi * np.arange(n_samples) / (24 * 60 * 60)) * 2
        
        # Add weekly trend (simulate production schedule)
        weekly_trend = np.sin(2 * np.pi * np.arange(n_samples) / (7 * 24 * 60 * 60)) * 1
        
        # Combine
        values = base_values + daily_cycle + weekly_trend
        
        # Add gradual drift (simulate equipment aging)
        drift = np.linspace(0, 0.5, n_samples) * np.random.choice([-1, 1])
        values += drift
        
        # Add random anomalies if enabled
        if include_anomalies:
            anomaly_indices = np.random.choice(
                n_samples,
                size=int(n_samples * 0.01),  # 1% anomalies
                replace=False
            )
            for idx in anomaly_indices:
                # Random spike or drop
                anomaly_magnitude = np.random.uniform(2, 5) * spec['normal_std']
                values[idx] += np.random.choice([-1, 1]) * anomaly_magnitude
        
        # Add failure scenario if enabled
        if include_failures and np.random.random() < failure_probability:
            values = self._add_failure_scenario(values, sensor_type, spec)
        
        # Clip to valid range
        values = np.clip(values, spec['min'], spec['max'])
        
        return values
    
    def _add_failure_scenario(
        self,
        values: np.ndarray,
        sensor_type: str,
        spec: Dict,
    ) -> np.ndarray:
        """Add realistic failure scenario to sensor data"""
        n_samples = len(values)
        
        # Failure starts in last 10% of data
        failure_start = int(n_samples * 0.9)
        
        # Different failure patterns based on sensor type
        if sensor_type in ['motor_temperature', 'vibration']:
            # Gradual increase (overheating, bearing wear)
            ramp = np.linspace(0, 1, n_samples - failure_start)
            failure_signal = ramp * (spec['max'] - spec['normal_mean']) * 0.8
            values[failure_start:] += failure_signal
        
        elif sensor_type in ['intake_pressure', 'discharge_pressure']:
            # Gradual decrease (pump degradation)
            ramp = np.linspace(0, 1, n_samples - failure_start)
            failure_signal = -ramp * (spec['normal_mean'] - spec['min']) * 0.6
            values[failure_start:] += failure_signal
        
        elif sensor_type == 'current':
            # Fluctuating increase (motor issues)
            ramp = np.linspace(0, 1, n_samples - failure_start)
            noise = np.random.normal(0, 2, n_samples - failure_start)
            failure_signal = ramp * (spec['max'] - spec['normal_mean']) * 0.5 + noise
            values[failure_start:] += failure_signal
        
        elif sensor_type == 'flow_rate':
            # Gradual decrease (production decline)
            ramp = np.linspace(0, 1, n_samples - failure_start)
            failure_signal = -ramp * (spec['normal_mean'] - spec['min']) * 0.4
            values[failure_start:] += failure_signal
        
        return values
    
    def _generate_status_data(
        self,
        n_samples: int,
        well_id: str,
        sensor_data: Dict,
        include_failures: bool,
        failure_probability: float,
    ) -> List[str]:
        """Generate equipment status based on sensor values"""
        statuses = []
        
        for i in range(n_samples):
            # Check sensor values for this timestamp
            temp = sensor_data.get('motor_temperature', [])[i] if 'motor_temperature' in sensor_data else None
            vib = sensor_data.get('vibration', [])[i] if 'vibration' in sensor_data else None
            current = sensor_data.get('current', [])[i] if 'current' in sensor_data else None
            
            # Determine status based on values
            if temp and temp > self.sensor_specs['motor_temperature']['critical_threshold']:
                status = 'critical'
            elif vib and vib > self.sensor_specs['vibration']['critical_threshold']:
                status = 'critical'
            elif current and current > self.sensor_specs['current']['critical_threshold']:
                status = 'critical'
            elif temp and temp > self.sensor_specs['motor_temperature']['warning_threshold']:
                status = 'warning'
            elif vib and vib > self.sensor_specs['vibration']['warning_threshold']:
                status = 'warning'
            elif current and current > self.sensor_specs['current']['warning_threshold']:
                status = 'warning'
            else:
                status = 'normal'
            
            # Random maintenance periods
            if random.random() < 0.001:  # 0.1% chance
                status = 'maintenance'
            
            # Random offline periods
            if random.random() < 0.0005:  # 0.05% chance
                status = 'offline'
            
            statuses.append(status)
        
        return statuses
    
    def _generate_quality_scores(self, n_samples: int) -> np.ndarray:
        """Generate data quality scores"""
        # Most data is high quality
        scores = np.random.normal(95, 5, n_samples)
        scores = np.clip(scores, 0, 100)
        
        # Some low quality readings
        low_quality_indices = np.random.choice(
            n_samples,
            size=int(n_samples * 0.02),  # 2% low quality
            replace=False
        )
        scores[low_quality_indices] = np.random.uniform(50, 80, len(low_quality_indices))
        
        return scores.astype(int)
    
    def _add_derived_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add derived metrics to dataframe"""
        # Pressure differential
        if 'discharge_pressure' in df.columns and 'intake_pressure' in df.columns:
            df['pressure_differential'] = (
                df['discharge_pressure'] - df['intake_pressure']
            )
        
        # Efficiency metric (flow rate / current)
        if 'flow_rate' in df.columns and 'current' in df.columns:
            df['efficiency'] = df['flow_rate'] / (df['current'] + 1e-6)  # Avoid division by zero
        
        # Temperature rise rate
        if 'motor_temperature' in df.columns:
            df['temperature_rise_rate'] = df['motor_temperature'].diff()
        
        return df
    
    def generate_multiple_wells(
        self,
        well_ids: List[str],
        start_date: datetime,
        days: int = 180,
        **kwargs
    ) -> pd.DataFrame:
        """Generate data for multiple wells"""
        all_data = []
        
        for well_id in well_ids:
            well_data = self.generate_well_data(
                well_id=well_id,
                start_date=start_date,
                days=days,
                **kwargs
            )
            all_data.append(well_data)
        
        return pd.concat(all_data, ignore_index=True)
    
    def export_to_parquet(
        self,
        df: pd.DataFrame,
        output_path: Path,
        compression: str = 'snappy'
    ):
        """Export dataframe to Parquet format"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        df.to_parquet(output_path, compression=compression, index=False)
        print(f"Exported {len(df)} records to {output_path}")
    
    def export_to_csv(
        self,
        df: pd.DataFrame,
        output_path: Path,
        chunk_size: Optional[int] = None
    ):
        """Export dataframe to CSV format"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if chunk_size and len(df) > chunk_size:
            # Export in chunks
            for i, chunk in enumerate(range(0, len(df), chunk_size)):
                chunk_path = output_path.parent / f"{output_path.stem}_part{i+1}.csv"
                df.iloc[chunk:chunk+chunk_size].to_csv(chunk_path, index=False)
            print(f"Exported {len(df)} records in chunks to {output_path.parent}")
        else:
            df.to_csv(output_path, index=False)
            print(f"Exported {len(df)} records to {output_path}")
    
    def export_to_json(
        self,
        df: pd.DataFrame,
        output_path: Path,
        orient: str = 'records'
    ):
        """Export dataframe to JSON format"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        df.to_json(output_path, orient=orient, date_format='iso', index=False)
        print(f"Exported {len(df)} records to {output_path}")
    
    def get_statistics(self, df: pd.DataFrame) -> Dict:
        """Get statistics about generated data"""
        stats = {
            'total_records': len(df),
            'date_range': {
                'start': df['timestamp'].min().isoformat(),
                'end': df['timestamp'].max().isoformat(),
            },
            'wells': df['well_id'].unique().tolist(),
            'sensors': list(self.sensor_specs.keys()),
            'sensor_statistics': {},
        }
        
        for sensor in self.sensor_specs.keys():
            if sensor in df.columns:
                stats['sensor_statistics'][sensor] = {
                    'mean': float(df[sensor].mean()),
                    'std': float(df[sensor].std()),
                    'min': float(df[sensor].min()),
                    'max': float(df[sensor].max()),
                }
        
        # Status distribution
        if 'equipment_status' in df.columns:
            stats['status_distribution'] = df['equipment_status'].value_counts().to_dict()
        
        return stats


def main():
    """Example usage"""
    generator = SyntheticALSDataGenerator(seed=42)
    
    # Generate data for 10 wells, 6 months
    start_date = datetime.now() - timedelta(days=180)
    well_ids = [f"Well_{i:02d}" for i in range(1, 11)]
    
    print("Generating synthetic data...")
    df = generator.generate_multiple_wells(
        well_ids=well_ids,
        start_date=start_date,
        days=180,
        interval_seconds=1,
        include_anomalies=True,
        include_failures=True,
        failure_probability=0.1,
    )
    
    print(f"Generated {len(df):,} records")
    
    # Export to different formats
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)
    
    # Parquet (recommended for large datasets)
    generator.export_to_parquet(
        df,
        output_dir / 'synthetic_als_data_6months.parquet'
    )
    
    # CSV (for compatibility)
    generator.export_to_csv(
        df,
        output_dir / 'synthetic_als_data_6months.csv',
        chunk_size=1000000  # 1M records per file
    )
    
    # JSON (for API/testing)
    generator.export_to_json(
        df.head(1000),  # Sample for JSON
        output_dir / 'synthetic_als_data_sample.json'
    )
    
    # Print statistics
    stats = generator.get_statistics(df)
    print("\nStatistics:")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
