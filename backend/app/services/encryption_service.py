"""
Encryption Service
Handles data encryption and decryption for sensitive data
"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class EncryptionService:
    """Service for data encryption"""
    
    def __init__(self, key: Optional[bytes] = None):
        if key:
            self.key = key
        else:
            # Try to get from environment or generate
            key_str = os.getenv("ENCRYPTION_KEY")
            if key_str:
                self.key = key_str.encode()
            else:
                # Generate a new key (should be stored securely in production)
                self.key = Fernet.generate_key()
                logger.warning("Generated new encryption key. Store it securely!")
        
        self.cipher = Fernet(self.key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt a string"""
        try:
            encrypted = self.cipher.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Error encrypting data: {e}")
            raise
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt a string"""
        try:
            decoded = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.cipher.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Error decrypting data: {e}")
            raise
    
    def encrypt_dict(self, data: dict) -> dict:
        """Encrypt sensitive fields in a dictionary"""
        encrypted = {}
        sensitive_fields = ['password', 'token', 'secret', 'api_key', 'credential']
        
        for key, value in data.items():
            if any(field in key.lower() for field in sensitive_fields):
                if isinstance(value, str):
                    encrypted[key] = self.encrypt(value)
                else:
                    encrypted[key] = value
            else:
                encrypted[key] = value
        
        return encrypted
    
    @staticmethod
    def generate_key() -> str:
        """Generate a new encryption key"""
        key = Fernet.generate_key()
        return key.decode()

