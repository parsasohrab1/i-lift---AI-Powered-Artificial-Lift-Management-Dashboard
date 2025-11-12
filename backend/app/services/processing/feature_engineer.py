"""
Feature engineering for sensor data
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
import numpy as np

from app.utils.logger import setup_logging

logger = setup_logging()


class FeatureEngineer:
    """Engineer features from sensor data for ML models"""
    
    def __init__(self):
        self.historical_data: Dict[str, List[Dict[str, Any]]] = {}  # well_id -> list of readings
    
    def engineer_features(self, data: Dict[str, Any], historical_window: int = 100) -> Dict[str, Any]:
        """
        Engineer features from current and historical data
        
        Args:
            data: Current sensor reading
            historical_window: Number of historical readings to consider
        
        Returns:
            Data with engineered features
        """
        well_id = data.get('well_id')
        sensor_type = data.get('sensor_type')
        sensor_value = data.get('sensor_value')
        
        if not well_id:
            return data
        
        # Initialize historical data storage
        key = f"{well_id}_{sensor_type}"
        if key not in self.historical_data:
            self.historical_data[key] = []
        
        # Add current reading to history
        self.historical_data[key].append({
            'value': float(sensor_value),
            'timestamp': datetime.utcnow(),
            'data': data.copy(),
        })
        
        # Keep only recent history
        if len(self.historical_data[key]) > historical_window:
            self.historical_data[key] = self.historical_data[key][-historical_window:]
        
        # Calculate time-based features
        time_features = self._calculate_time_features(data)
        
        # Calculate statistical features
        statistical_features = self._calculate_statistical_features(key)
        
        # Calculate trend features
        trend_features = self._calculate_trend_features(key)
        
        # Calculate cyclical features
        cyclical_features = self._calculate_cyclical_features(data)
        
        # Combine all features
        engineered_data = data.copy()
        engineered_data['_engineered_features'] = {
            **time_features,
            **statistical_features,
            **trend_features,
            **cyclical_features,
        }
        
        return engineered_data
    
    def _calculate_time_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate time-based features"""
        timestamp_str = data.get('timestamp') or data.get('_metadata', {}).get('timestamp')
        
        try:
            if isinstance(timestamp_str, str):
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                timestamp = datetime.utcnow()
        except Exception:
            timestamp = datetime.utcnow()
        
        return {
            'hour': timestamp.hour,
            'day_of_week': timestamp.weekday(),
            'day_of_month': timestamp.day,
            'month': timestamp.month,
            'is_weekend': timestamp.weekday() >= 5,
            'hour_sin': np.sin(2 * np.pi * timestamp.hour / 24),
            'hour_cos': np.cos(2 * np.pi * timestamp.hour / 24),
            'day_sin': np.sin(2 * np.pi * timestamp.day / 31),
            'day_cos': np.cos(2 * np.pi * timestamp.day / 31),
        }
    
    def _calculate_statistical_features(self, key: str) -> Dict[str, Any]:
        """Calculate statistical features from historical data"""
        if key not in self.historical_data or len(self.historical_data[key]) < 2:
            return {
                'mean': 0,
                'std': 0,
                'min': 0,
                'max': 0,
                'median': 0,
                'percentile_25': 0,
                'percentile_75': 0,
            }
        
        values = [r['value'] for r in self.historical_data[key]]
        
        return {
            'mean': float(np.mean(values)),
            'std': float(np.std(values)),
            'min': float(np.min(values)),
            'max': float(np.max(values)),
            'median': float(np.median(values)),
            'percentile_25': float(np.percentile(values, 25)),
            'percentile_75': float(np.percentile(values, 75)),
            'iqr': float(np.percentile(values, 75) - np.percentile(values, 25)),
        }
    
    def _calculate_trend_features(self, key: str) -> Dict[str, Any]:
        """Calculate trend features"""
        if key not in self.historical_data or len(self.historical_data[key]) < 3:
            return {
                'trend': 0,
                'acceleration': 0,
                'volatility': 0,
            }
        
        history = self.historical_data[key]
        values = [r['value'] for r in history[-10:]]  # Last 10 readings
        
        if len(values) < 2:
            return {
                'trend': 0,
                'acceleration': 0,
                'volatility': 0,
            }
        
        # Calculate trend (slope)
        x = np.arange(len(values))
        trend = float(np.polyfit(x, values, 1)[0]) if len(values) > 1 else 0
        
        # Calculate acceleration (change in trend)
        if len(values) >= 3:
            first_half_trend = np.polyfit(x[:len(values)//2], values[:len(values)//2], 1)[0]
            second_half_trend = np.polyfit(x[len(values)//2:], values[len(values)//2:], 1)[0]
            acceleration = float(second_half_trend - first_half_trend)
        else:
            acceleration = 0
        
        # Calculate volatility (standard deviation of changes)
        changes = [values[i] - values[i-1] for i in range(1, len(values))]
        volatility = float(np.std(changes)) if changes else 0
        
        return {
            'trend': trend,
            'acceleration': acceleration,
            'volatility': volatility,
        }
    
    def _calculate_cyclical_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate cyclical/seasonal features"""
        timestamp_str = data.get('timestamp') or data.get('_metadata', {}).get('timestamp')
        
        try:
            if isinstance(timestamp_str, str):
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                timestamp = datetime.utcnow()
        except Exception:
            timestamp = datetime.utcnow()
        
        # Day of year (1-365)
        day_of_year = timestamp.timetuple().tm_yday
        
        return {
            'day_of_year': day_of_year,
            'day_of_year_sin': np.sin(2 * np.pi * day_of_year / 365),
            'day_of_year_cos': np.cos(2 * np.pi * day_of_year / 365),
            'week_of_year': timestamp.isocalendar()[1],
            'quarter': (timestamp.month - 1) // 3 + 1,
        }
    
    def clear_history(self, well_id: str, sensor_type: str):
        """Clear historical data for a specific well and sensor"""
        key = f"{well_id}_{sensor_type}"
        if key in self.historical_data:
            self.historical_data[key].clear()
            logger.info("History cleared", key=key)

