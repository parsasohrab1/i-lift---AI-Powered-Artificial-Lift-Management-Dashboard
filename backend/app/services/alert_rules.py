"""
Alert Rules Engine
Defines and evaluates alert rules based on sensor data
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertRule:
    """Alert rule definition"""
    
    def __init__(
        self,
        rule_id: str,
        name: str,
        sensor_type: str,
        condition: str,  # 'gt', 'lt', 'eq', 'between'
        threshold: float,
        threshold_max: Optional[float] = None,
        severity: AlertSeverity = AlertSeverity.MEDIUM,
        message_template: str = "{sensor_type} {condition} threshold",
        enabled: bool = True,
    ):
        self.rule_id = rule_id
        self.name = name
        self.sensor_type = sensor_type
        self.condition = condition
        self.threshold = threshold
        self.threshold_max = threshold_max
        self.severity = severity
        self.message_template = message_template
        self.enabled = enabled
    
    def evaluate(self, sensor_value: float) -> tuple[bool, Optional[str]]:
        """Evaluate rule against sensor value"""
        if not self.enabled:
            return False, None
        
        triggered = False
        message = None
        
        if self.condition == 'gt':
            triggered = sensor_value > self.threshold
            if triggered:
                message = self.message_template.format(
                    sensor_type=self.sensor_type,
                    condition=f"exceeded {self.threshold}",
                    value=sensor_value,
                )
        elif self.condition == 'lt':
            triggered = sensor_value < self.threshold
            if triggered:
                message = self.message_template.format(
                    sensor_type=self.sensor_type,
                    condition=f"below {self.threshold}",
                    value=sensor_value,
                )
        elif self.condition == 'eq':
            triggered = abs(sensor_value - self.threshold) < 0.01
            if triggered:
                message = self.message_template.format(
                    sensor_type=self.sensor_type,
                    condition=f"equals {self.threshold}",
                    value=sensor_value,
                )
        elif self.condition == 'between':
            if self.threshold_max is None:
                return False, None
            triggered = self.threshold <= sensor_value <= self.threshold_max
            if triggered:
                message = self.message_template.format(
                    sensor_type=self.sensor_type,
                    condition=f"between {self.threshold} and {self.threshold_max}",
                    value=sensor_value,
                )
        
        return triggered, message


class AlertRulesEngine:
    """Engine for managing and evaluating alert rules"""
    
    def __init__(self):
        self.rules: Dict[str, AlertRule] = {}
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Initialize default alert rules"""
        default_rules = [
            AlertRule(
                rule_id="temp_high_critical",
                name="Motor Temperature Critical",
                sensor_type="motor_temperature",
                condition="gt",
                threshold=95.0,
                severity=AlertSeverity.CRITICAL,
                message_template="Motor temperature critically high: {value}°C (threshold: {condition})",
            ),
            AlertRule(
                rule_id="temp_high_warning",
                name="Motor Temperature Warning",
                sensor_type="motor_temperature",
                condition="gt",
                threshold=85.0,
                severity=AlertSeverity.HIGH,
                message_template="Motor temperature high: {value}°C (threshold: {condition})",
            ),
            AlertRule(
                rule_id="temp_low",
                name="Motor Temperature Low",
                sensor_type="motor_temperature",
                condition="lt",
                threshold=65.0,
                severity=AlertSeverity.MEDIUM,
                message_template="Motor temperature low: {value}°C (threshold: {condition})",
            ),
            AlertRule(
                rule_id="pressure_low_critical",
                name="Intake Pressure Critical",
                sensor_type="intake_pressure",
                condition="lt",
                threshold=400.0,
                severity=AlertSeverity.CRITICAL,
                message_template="Intake pressure critically low: {value} PSI (threshold: {condition})",
            ),
            AlertRule(
                rule_id="pressure_low_warning",
                name="Intake Pressure Warning",
                sensor_type="intake_pressure",
                condition="lt",
                threshold=450.0,
                severity=AlertSeverity.HIGH,
                message_template="Intake pressure low: {value} PSI (threshold: {condition})",
            ),
            AlertRule(
                rule_id="vibration_high",
                name="Vibration High",
                sensor_type="vibration",
                condition="gt",
                threshold=4.0,
                severity=AlertSeverity.HIGH,
                message_template="Vibration high: {value} m/s² (threshold: {condition})",
            ),
            AlertRule(
                rule_id="current_high",
                name="Current High",
                sensor_type="current",
                condition="gt",
                threshold=75.0,
                severity=AlertSeverity.HIGH,
                message_template="Current high: {value} A (threshold: {condition})",
            ),
            AlertRule(
                rule_id="flow_low",
                name="Flow Rate Low",
                sensor_type="flow_rate",
                condition="lt",
                threshold=1500.0,
                severity=AlertSeverity.MEDIUM,
                message_template="Flow rate low: {value} bbl/day (threshold: {condition})",
            ),
        ]
        
        for rule in default_rules:
            self.add_rule(rule)
    
    def add_rule(self, rule: AlertRule):
        """Add an alert rule"""
        self.rules[rule.rule_id] = rule
        logger.info(f"Added alert rule: {rule.rule_id}")
    
    def remove_rule(self, rule_id: str):
        """Remove an alert rule"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            logger.info(f"Removed alert rule: {rule_id}")
    
    def get_rule(self, rule_id: str) -> Optional[AlertRule]:
        """Get an alert rule"""
        return self.rules.get(rule_id)
    
    def list_rules(self) -> List[AlertRule]:
        """List all alert rules"""
        return list(self.rules.values())
    
    def evaluate_sensor_reading(
        self,
        well_id: str,
        sensor_type: str,
        sensor_value: float,
    ) -> List[Dict[str, Any]]:
        """Evaluate sensor reading against all rules"""
        triggered_alerts = []
        
        for rule in self.rules.values():
            if rule.sensor_type == sensor_type:
                triggered, message = rule.evaluate(sensor_value)
                if triggered:
                    triggered_alerts.append({
                        'rule_id': rule.rule_id,
                        'well_id': well_id,
                        'alert_type': f"{sensor_type}_{rule.condition}",
                        'severity': rule.severity.value,
                        'message': message or f"{rule.name} triggered",
                        'sensor_type': sensor_type,
                        'sensor_value': sensor_value,
                        'threshold': rule.threshold,
                    })
        
        return triggered_alerts
    
    def update_rule(
        self,
        rule_id: str,
        **kwargs
    ) -> bool:
        """Update an alert rule"""
        rule = self.rules.get(rule_id)
        if not rule:
            return False
        
        for key, value in kwargs.items():
            if hasattr(rule, key):
                setattr(rule, key, value)
        
        logger.info(f"Updated alert rule: {rule_id}")
        return True

