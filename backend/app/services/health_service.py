"""
Health check service for monitoring system health
"""
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
import redis
from redis.exceptions import ConnectionError as RedisConnectionError

from app.core.database import get_db, engine
from app.core.config import settings
from app.utils.logger import setup_logging

logger = setup_logging()


class HealthService:
    """Service for checking system health"""
    
    def __init__(self, db: Optional[Session] = None):
        self.db = db
    
    async def check_database(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            start_time = time.time()
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            response_time = (time.time() - start_time) * 1000  # ms
            
            # Check connection pool
            pool = engine.pool
            pool_status = {
                "size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
            }
            
            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "connection_pool": pool_status
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def check_redis(self) -> Dict[str, Any]:
        """Check Redis health"""
        try:
            start_time = time.time()
            redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True
            )
            
            # Test connection
            redis_client.ping()
            response_time = (time.time() - start_time) * 1000  # ms
            
            # Get Redis info
            info = redis_client.info()
            
            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "unknown"),
                "redis_version": info.get("redis_version", "unknown")
            }
        except RedisConnectionError as e:
            logger.error(f"Redis health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": "Redis connection failed"
            }
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def check_kafka(self) -> Dict[str, Any]:
        """Check Kafka health"""
        try:
            from kafka import KafkaProducer, KafkaConsumer
            from kafka.errors import KafkaError
            
            start_time = time.time()
            
            # Try to create a producer
            producer = KafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: str(v).encode('utf-8')
            )
            
            # Get metadata
            metadata = producer.list_topics(timeout=5)
            response_time = (time.time() - start_time) * 1000  # ms
            
            producer.close()
            
            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "topics_count": len(metadata.topics)
            }
        except KafkaError as e:
            logger.error(f"Kafka health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": f"Kafka error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Kafka health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def check_ml_services(self) -> Dict[str, Any]:
        """Check ML services health"""
        try:
            import httpx
            
            start_time = time.time()
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{settings.ML_SERVICE_URL}/health")
                response_time = (time.time() - start_time) * 1000  # ms
                
                if response.status_code == 200:
                    return {
                        "status": "healthy",
                        "response_time_ms": round(response_time, 2),
                        "service_url": settings.ML_SERVICE_URL
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "error": f"ML service returned status {response.status_code}"
                    }
        except Exception as e:
            logger.error(f"ML services health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def check_system_resources(self) -> Dict[str, Any]:
        """Check system resources (CPU, memory, disk)"""
        try:
            import psutil
            
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "status": "healthy",
                "cpu": {
                    "percent": cpu_percent,
                    "count": psutil.cpu_count()
                },
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "used_percent": memory.percent
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "used_percent": round((disk.used / disk.total) * 100, 2)
                }
            }
        except ImportError:
            return {
                "status": "unknown",
                "error": "psutil not installed"
            }
        except Exception as e:
            logger.error(f"System resources check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def get_overall_health(
        self,
        db: Session,
        include_details: bool = False
    ) -> Dict[str, Any]:
        """Get overall system health"""
        checks = {
            "database": await self.check_database(),
            "redis": await self.check_redis(),
            "kafka": await self.check_kafka(),
        }
        
        # Optional checks
        if include_details:
            checks["ml_services"] = await self.check_ml_services()
            checks["system_resources"] = await self.check_system_resources()
        
        # Determine overall status
        all_healthy = all(
            check.get("status") == "healthy"
            for check in checks.values()
        )
        
        overall_status = "healthy" if all_healthy else "degraded"
        
        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": checks
        }
    
    async def get_health_summary(self, db: Session) -> Dict[str, Any]:
        """Get health summary for dashboard"""
        try:
            # Quick health checks
            db_health = await self.check_database()
            redis_health = await self.check_redis()
            
            # Get system stats
            try:
                import psutil
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory = psutil.virtual_memory()
            except:
                cpu_percent = None
                memory = None
            
            return {
                "overall_status": "healthy" if (
                    db_health.get("status") == "healthy" and
                    redis_health.get("status") == "healthy"
                ) else "degraded",
                "database": {
                    "status": db_health.get("status"),
                    "response_time_ms": db_health.get("response_time_ms")
                },
                "redis": {
                    "status": redis_health.get("status"),
                    "response_time_ms": redis_health.get("response_time_ms")
                },
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent if memory else None
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting health summary: {e}")
            return {
                "overall_status": "unknown",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


# Global health service instance
health_service = HealthService()

