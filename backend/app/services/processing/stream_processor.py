"""
Stream processing for real-time data transformation
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import deque
import statistics

from app.utils.logger import setup_logging

logger = setup_logging()


class StreamProcessor:
    """Process streaming sensor data in real-time"""
    
    def __init__(self, window_size: int = 60):
        """
        Initialize stream processor
        
        Args:
            window_size: Size of sliding window in seconds
        """
        self.window_size = window_size
        self.windows: Dict[str, deque] = {}  # well_id -> deque of readings
        self.last_processed: Dict[str, datetime] = {}
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single data point
        
        Returns:
            Processed data with additional features
        """
        well_id = data.get('well_id')
        sensor_type = data.get('sensor_type')
        sensor_value = data.get('sensor_value')
        timestamp_str = data.get('timestamp') or data.get('_metadata', {}).get('timestamp')
        
        if not well_id or not sensor_type or sensor_value is None:
            logger.warning("Invalid data for processing", data=data)
            return data
        
        # Parse timestamp
        try:
            if isinstance(timestamp_str, str):
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                timestamp = datetime.utcnow()
        except Exception:
            timestamp = datetime.utcnow()
        
        # Initialize window for this well if needed
        window_key = f"{well_id}_{sensor_type}"
        if window_key not in self.windows:
            self.windows[window_key] = deque(maxlen=1000)  # Max 1000 readings per window
        
        # Add to window
        reading = {
            'value': float(sensor_value),
            'timestamp': timestamp,
        }
        self.windows[window_key].append(reading)
        
        # Calculate features
        features = self._calculate_features(window_key, reading)
        
        # Add features to data
        processed_data = data.copy()
        processed_data['_features'] = features
        processed_data['_processed_at'] = datetime.utcnow().isoformat()
        
        return processed_data
    
    def _calculate_features(self, window_key: str, current_reading: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate statistical features from sliding window"""
        window = self.windows[window_key]
        
        if len(window) < 2:
            return {
                'window_size': len(window),
                'mean': current_reading['value'],
                'std': 0,
                'min': current_reading['value'],
                'max': current_reading['value'],
            }
        
        values = [r['value'] for r in window]
        
        features = {
            'window_size': len(window),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'std': statistics.stdev(values) if len(values) > 1 else 0,
            'min': min(values),
            'max': max(values),
            'range': max(values) - min(values),
            'current_value': current_reading['value'],
            'change_from_mean': current_reading['value'] - statistics.mean(values),
            'change_percent': ((current_reading['value'] - statistics.mean(values)) / statistics.mean(values) * 100) if statistics.mean(values) != 0 else 0,
        }
        
        # Calculate rate of change
        if len(window) >= 2:
            recent_values = [r['value'] for r in list(window)[-5:]]
            if len(recent_values) >= 2:
                features['rate_of_change'] = recent_values[-1] - recent_values[0]
            else:
                features['rate_of_change'] = 0
        else:
            features['rate_of_change'] = 0
        
        # Detect anomalies (simple z-score based)
        if features['std'] > 0:
            z_score = abs((current_reading['value'] - features['mean']) / features['std'])
            features['z_score'] = z_score
            features['is_anomaly'] = z_score > 3  # 3-sigma rule
        else:
            features['z_score'] = 0
            features['is_anomaly'] = False
        
        return features
    
    def get_window_stats(self, well_id: str, sensor_type: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific window"""
        window_key = f"{well_id}_{sensor_type}"
        if window_key not in self.windows or len(self.windows[window_key]) == 0:
            return None
        
        window = self.windows[window_key]
        values = [r['value'] for r in window]
        
        return {
            'count': len(values),
            'mean': statistics.mean(values),
            'std': statistics.stdev(values) if len(values) > 1 else 0,
            'min': min(values),
            'max': max(values),
        }
    
    def clear_window(self, well_id: str, sensor_type: str):
        """Clear window for a specific well and sensor"""
        window_key = f"{well_id}_{sensor_type}"
        if window_key in self.windows:
            self.windows[window_key].clear()
            logger.info("Window cleared", window_key=window_key)

