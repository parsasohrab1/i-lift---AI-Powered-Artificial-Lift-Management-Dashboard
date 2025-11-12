"""
Redis client configuration and utilities
"""
import redis
from typing import Optional, Any
import json
from app.core.config import settings


class RedisClient:
    """Redis client wrapper with connection pooling"""
    
    def __init__(self):
        self.client: Optional[redis.Redis] = None
        self._connect()
    
    def _connect(self):
        """Connect to Redis"""
        try:
            # Build connection kwargs
            connection_kwargs = {
                "decode_responses": True,
                "socket_connect_timeout": 5,
                "socket_keepalive": True,
                "health_check_interval": 30
            }
            
            # Add SSL configuration if enabled
            if settings.REDIS_SSL:
                connection_kwargs["ssl"] = True
                if settings.REDIS_SSL_CA_CERTS:
                    connection_kwargs["ssl_ca_certs"] = settings.REDIS_SSL_CA_CERTS
            
            # Add password if provided
            if settings.REDIS_PASSWORD:
                connection_kwargs["password"] = settings.REDIS_PASSWORD
            
            # Parse URL and update connection kwargs
            redis_url = settings.REDIS_URL
            
            self.client = redis.from_url(
                redis_url,
                **connection_kwargs
            )
            # Test connection
            self.client.ping()
        except Exception as e:
            print(f"Redis connection error: {e}")
            self.client = None
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis"""
        if not self.client:
            return None
        try:
            value = self.client.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception as e:
            print(f"Redis get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in Redis"""
        if not self.client:
            return False
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            ttl = ttl or settings.REDIS_CACHE_TTL
            return self.client.setex(key, ttl, value)
        except Exception as e:
            print(f"Redis set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        if not self.client:
            return False
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.client:
            return False
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            print(f"Redis exists error: {e}")
            return False
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment a counter"""
        if not self.client:
            return None
        try:
            return self.client.incrby(key, amount)
        except Exception as e:
            print(f"Redis increment error: {e}")
            return None
    
    def set_hash(self, name: str, mapping: dict, ttl: Optional[int] = None) -> bool:
        """Set hash in Redis"""
        if not self.client:
            return False
        try:
            # Convert values to JSON if needed
            processed_mapping = {}
            for k, v in mapping.items():
                if isinstance(v, (dict, list)):
                    processed_mapping[k] = json.dumps(v)
                else:
                    processed_mapping[k] = v
            
            result = self.client.hset(name, mapping=processed_mapping)
            if ttl:
                self.client.expire(name, ttl)
            return bool(result)
        except Exception as e:
            print(f"Redis set_hash error: {e}")
            return False
    
    def get_hash(self, name: str) -> Optional[dict]:
        """Get hash from Redis"""
        if not self.client:
            return None
        try:
            data = self.client.hgetall(name)
            if not data:
                return None
            
            # Try to parse JSON values
            result = {}
            for k, v in data.items():
                try:
                    result[k] = json.loads(v)
                except (json.JSONDecodeError, TypeError):
                    result[k] = v
            return result
        except Exception as e:
            print(f"Redis get_hash error: {e}")
            return None
    
    def get_hash_field(self, name: str, key: str) -> Optional[Any]:
        """Get specific field from hash"""
        if not self.client:
            return None
        try:
            value = self.client.hget(name, key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception as e:
            print(f"Redis get_hash_field error: {e}")
            return None
    
    def ping(self) -> bool:
        """Ping Redis server"""
        if not self.client:
            return False
        try:
            return self.client.ping()
        except Exception:
            return False


# Global Redis client instance
redis_client = RedisClient()

