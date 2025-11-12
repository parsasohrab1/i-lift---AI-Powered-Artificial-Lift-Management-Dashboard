"""
Data validation and cleaning service
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import re

from app.utils.logger import setup_logging

logger = setup_logging()


class DataValidator:
    """Validate and clean ingested sensor data"""
    
    # Sensor value ranges (can be configured)
    SENSOR_RANGES = {
        'motor_temperature': {'min': 65, 'max': 120, 'unit': 'C'},
        'intake_pressure': {'min': 450, 'max': 600, 'unit': 'psi'},
        'discharge_pressure': {'min': 800, 'max': 1200, 'unit': 'psi'},
        'vibration': {'min': 0.5, 'max': 5.0, 'unit': 'g'},
        'current': {'min': 30, 'max': 80, 'unit': 'A'},
        'flow_rate': {'min': 1500, 'max': 2500, 'unit': 'bpd'},
    }
    
    def __init__(self):
        self.validation_errors: List[str] = []
    
    def validate(self, data: Dict[str, Any]) -> tuple[bool, Dict[str, Any], List[str]]:
        """
        Validate sensor data
        
        Returns:
            (is_valid, cleaned_data, errors)
        """
        self.validation_errors = []
        cleaned_data = data.copy()
        
        # Required fields
        required_fields = ['well_id', 'sensor_type', 'sensor_value']
        for field in required_fields:
            if field not in data:
                self.validation_errors.append(f"Missing required field: {field}")
        
        if self.validation_errors:
            return False, cleaned_data, self.validation_errors
        
        # Validate well_id format
        if 'well_id' in data:
            if not re.match(r'^[A-Za-z0-9_-]+$', str(data['well_id'])):
                self.validation_errors.append("Invalid well_id format")
        
        # Validate sensor_type
        if 'sensor_type' in data:
            sensor_type = data['sensor_type']
            if sensor_type not in self.SENSOR_RANGES:
                logger.warning("Unknown sensor type", sensor_type=sensor_type)
        
        # Validate sensor_value
        if 'sensor_value' in data:
            try:
                value = float(data['sensor_value'])
                cleaned_data['sensor_value'] = value
                
                # Check range if sensor type is known
                sensor_type = data.get('sensor_type')
                if sensor_type in self.SENSOR_RANGES:
                    range_config = self.SENSOR_RANGES[sensor_type]
                    if value < range_config['min'] or value > range_config['max']:
                        self.validation_errors.append(
                            f"Value {value} out of range [{range_config['min']}, {range_config['max']}]"
                        )
                        # Flag as outlier but don't reject
                        cleaned_data['_is_outlier'] = True
                
            except (ValueError, TypeError):
                self.validation_errors.append("Invalid sensor_value: must be numeric")
        
        # Validate timestamp
        if 'timestamp' in data:
            try:
                if isinstance(data['timestamp'], str):
                    datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                cleaned_data['timestamp'] = data['timestamp']
            except (ValueError, TypeError):
                self.validation_errors.append("Invalid timestamp format")
                # Use current timestamp as fallback
                cleaned_data['timestamp'] = datetime.utcnow().isoformat()
        else:
            # Add timestamp if missing
            cleaned_data['timestamp'] = datetime.utcnow().isoformat()
        
        # Calculate data quality score
        quality_score = self._calculate_quality_score(cleaned_data, self.validation_errors)
        cleaned_data['data_quality'] = quality_score
        
        # Add validation metadata
        cleaned_data['_validation'] = {
            'is_valid': len(self.validation_errors) == 0,
            'errors': self.validation_errors,
            'validated_at': datetime.utcnow().isoformat(),
        }
        
        is_valid = len(self.validation_errors) == 0
        return is_valid, cleaned_data, self.validation_errors
    
    def _calculate_quality_score(self, data: Dict[str, Any], errors: List[str]) -> int:
        """Calculate data quality score (0-100)"""
        score = 100
        
        # Deduct points for errors
        score -= len(errors) * 10
        
        # Deduct points for outliers
        if data.get('_is_outlier'):
            score -= 20
        
        # Deduct points for missing optional fields
        optional_fields = ['measurement_unit', 'data_quality']
        for field in optional_fields:
            if field not in data:
                score -= 5
        
        return max(0, min(100, score))
    
    def normalize_sensor_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize sensor data to standard format"""
        normalized = {
            'well_id': data.get('well_id') or data.get('node_id') or data.get('device_id'),
            'sensor_type': data.get('sensor_type') or data.get('sensor') or data.get('metric'),
            'sensor_value': data.get('sensor_value') or data.get('value') or data.get('reading'),
            'measurement_unit': data.get('measurement_unit') or data.get('unit'),
            'timestamp': data.get('timestamp') or data.get('time') or datetime.utcnow().isoformat(),
        }
        
        # Preserve metadata
        if '_metadata' in data:
            normalized['_metadata'] = data['_metadata']
        
        return normalized

