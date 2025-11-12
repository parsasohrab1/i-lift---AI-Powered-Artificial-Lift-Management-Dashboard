"""
Application configuration settings
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "IntelliLift AI Dashboard"
    DEBUG: bool = False
    VERSION: str = "1.0.0"
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
    ]
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/ilift_db"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_SSL_MODE: str = "prefer"  # disable, allow, prefer, require, verify-ca, verify-full
    DATABASE_SSL_ROOT_CERT: str = ""  # Path to SSL certificate
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_CACHE_TTL: int = 3600
    REDIS_SSL: bool = False
    REDIS_SSL_CA_CERTS: str = ""
    REDIS_PASSWORD: str = ""
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC_SENSOR_DATA: str = "sensor-data"
    KAFKA_TOPIC_ALERTS: str = "alerts"
    KAFKA_SSL_CAFILE: str = ""
    KAFKA_SSL_CERTFILE: str = ""
    KAFKA_SSL_KEYFILE: str = ""
    KAFKA_SECURITY_PROTOCOL: str = "PLAINTEXT"  # PLAINTEXT, SSL, SASL_PLAINTEXT, SASL_SSL
    KAFKA_SASL_MECHANISM: str = ""  # PLAIN, SCRAM-SHA-256, SCRAM-SHA-512
    KAFKA_SASL_USERNAME: str = ""
    KAFKA_SASL_PASSWORD: str = ""
    
    # ML/AI
    ML_MODEL_PATH: str = "./models"
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"
    ML_SERVICE_URL: str = "http://localhost:8080"
    FEATURE_STORE_PATH: str = "./feature_store"
    
    # MQTT (Remote IoT)
    MQTT_BROKER_HOST: str = "localhost"
    MQTT_BROKER_PORT: int = 1883
    MQTT_USERNAME: str = ""
    MQTT_PASSWORD: str = ""
    MQTT_SSL: bool = False
    MQTT_SSL_CA_CERTS: str = ""
    MQTT_CLIENT_ID: str = ""
    
    # OPC-UA (Remote SCADA)
    OPCUA_SERVER_URL: str = "opc.tcp://localhost:4840"
    OPCUA_SECURITY_POLICY: str = "None"  # None, Basic128Rsa15, Basic256, Basic256Sha256
    OPCUA_SECURITY_MODE: str = "None"  # None, Sign, SignAndEncrypt
    OPCUA_USERNAME: str = ""
    OPCUA_PASSWORD: str = ""
    OPCUA_CERTIFICATE_PATH: str = ""
    OPCUA_PRIVATE_KEY_PATH: str = ""
    
    # Remote Connection Settings
    USE_SSH_TUNNEL: bool = False
    SSH_HOST: str = ""
    SSH_PORT: int = 22
    SSH_USERNAME: str = ""
    SSH_PASSWORD: str = ""
    SSH_KEY_PATH: str = ""
    SSH_TUNNEL_REMOTE_HOST: str = "localhost"
    SSH_TUNNEL_REMOTE_PORT: int = 5432
    SSH_TUNNEL_LOCAL_PORT: int = 5433
    
    # Data Processing
    DATA_INGESTION_INTERVAL: int = 1  # seconds
    BATCH_SIZE: int = 1000
    
    # Monitoring
    PROMETHEUS_PORT: int = 9090
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

