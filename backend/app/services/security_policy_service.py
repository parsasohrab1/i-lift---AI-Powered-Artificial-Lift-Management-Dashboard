"""
Security Policy Service
Manages security policies and compliance rules
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SecurityPolicyType(str, Enum):
    """Types of security policies"""
    PASSWORD = "password"
    SESSION = "session"
    DATA_RETENTION = "data_retention"
    ACCESS_CONTROL = "access_control"
    ENCRYPTION = "encryption"
    AUDIT = "audit"


class SecurityPolicyService:
    """Service for managing security policies"""
    
    def __init__(self):
        self.policies = self._load_default_policies()
    
    def _load_default_policies(self) -> Dict[str, Dict[str, Any]]:
        """Load default security policies"""
        return {
            'password': {
                'min_length': 8,
                'require_uppercase': True,
                'require_lowercase': True,
                'require_numbers': True,
                'require_special_chars': True,
                'max_age_days': 90,
                'history_count': 5,
            },
            'session': {
                'timeout_minutes': 30,
                'max_concurrent_sessions': 5,
                'require_https': True,
                'same_site': 'strict',
            },
            'data_retention': {
                'sensor_data_days': 365,
                'audit_logs_days': 2555,  # 7 years
                'alerts_days': 180,
                'ml_predictions_days': 365,
            },
            'access_control': {
                'require_mfa': False,
                'ip_whitelist': [],
                'ip_blacklist': [],
                'rate_limit_per_minute': 100,
            },
            'encryption': {
                'encrypt_sensitive_fields': True,
                'encryption_algorithm': 'AES-256',
            },
            'audit': {
                'log_all_actions': True,
                'retention_days': 2555,
                'alert_on_suspicious': True,
            },
        }
    
    def get_policy(self, policy_type: SecurityPolicyType) -> Dict[str, Any]:
        """Get a security policy"""
        return self.policies.get(policy_type.value, {})
    
    def update_policy(
        self,
        policy_type: SecurityPolicyType,
        updates: Dict[str, Any],
    ) -> bool:
        """Update a security policy"""
        if policy_type.value not in self.policies:
            return False
        
        self.policies[policy_type.value].update(updates)
        logger.info(f"Updated security policy: {policy_type.value}")
        return True
    
    def validate_password(self, password: str) -> tuple[bool, List[str]]:
        """Validate password against policy"""
        policy = self.get_policy(SecurityPolicyType.PASSWORD)
        errors = []
        
        if len(password) < policy.get('min_length', 8):
            errors.append(f"Password must be at least {policy['min_length']} characters")
        
        if policy.get('require_uppercase') and not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if policy.get('require_lowercase') and not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        if policy.get('require_numbers') and not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one number")
        
        if policy.get('require_special_chars'):
            special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            if not any(c in special_chars for c in password):
                errors.append("Password must contain at least one special character")
        
        return len(errors) == 0, errors
    
    def check_data_retention(
        self,
        data_type: str,
        created_at: datetime,
    ) -> bool:
        """Check if data should be retained"""
        policy = self.get_policy(SecurityPolicyType.DATA_RETENTION)
        
        retention_key = f"{data_type}_days"
        retention_days = policy.get(retention_key, 365)
        
        age_days = (datetime.utcnow() - created_at).days
        return age_days <= retention_days
    
    def get_retention_date(
        self,
        data_type: str,
    ) -> datetime:
        """Get the date before which data should be deleted"""
        policy = self.get_policy(SecurityPolicyType.DATA_RETENTION)
        
        retention_key = f"{data_type}_days"
        retention_days = policy.get(retention_key, 365)
        
        return datetime.utcnow() - timedelta(days=retention_days)
    
    def check_rate_limit(
        self,
        user_id: str,
        action_count: int,
    ) -> bool:
        """Check if user has exceeded rate limit"""
        policy = self.get_policy(SecurityPolicyType.ACCESS_CONTROL)
        rate_limit = policy.get('rate_limit_per_minute', 100)
        
        return action_count <= rate_limit
    
    def is_ip_allowed(self, ip_address: str) -> bool:
        """Check if IP address is allowed"""
        policy = self.get_policy(SecurityPolicyType.ACCESS_CONTROL)
        
        blacklist = policy.get('ip_blacklist', [])
        if ip_address in blacklist:
            return False
        
        whitelist = policy.get('ip_whitelist', [])
        if whitelist and ip_address not in whitelist:
            return False
        
        return True

