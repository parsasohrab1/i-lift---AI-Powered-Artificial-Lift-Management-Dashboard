#!/usr/bin/env python3
"""
Script to test remote connections for all services
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.core.database import check_db_connection, engine
from app.core.redis_client import redis_client
from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
from kafka.errors import KafkaError
import redis
import psycopg2
from urllib.parse import urlparse


def test_database_connection():
    """Test database connection"""
    print("\n" + "="*50)
    print("Testing Database Connection...")
    print("="*50)
    
    try:
        # Parse database URL
        db_url = settings.DATABASE_URL
        parsed = urlparse(db_url)
        
        print(f"Host: {parsed.hostname}")
        print(f"Port: {parsed.port}")
        print(f"Database: {parsed.path[1:]}")
        print(f"User: {parsed.username}")
        print(f"SSL Mode: {settings.DATABASE_SSL_MODE}")
        
        # Test connection
        if check_db_connection():
            print("✅ Database connection: SUCCESS")
            
            # Get database version
            with engine.connect() as conn:
                result = conn.execute("SELECT version();")
                version = result.scalar()
                print(f"   Database Version: {version.split(',')[0]}")
            return True
        else:
            print("❌ Database connection: FAILED")
            return False
            
    except Exception as e:
        print(f"❌ Database connection error: {str(e)}")
        return False


def test_redis_connection():
    """Test Redis connection"""
    print("\n" + "="*50)
    print("Testing Redis Connection...")
    print("="*50)
    
    try:
        redis_url = settings.REDIS_URL
        parsed = urlparse(redis_url)
        
        print(f"Host: {parsed.hostname}")
        print(f"Port: {parsed.port}")
        print(f"Database: {parsed.path[1:] if parsed.path else '0'}")
        print(f"SSL: {settings.REDIS_SSL}")
        
        # Test connection
        if redis_client.ping():
            print("✅ Redis connection: SUCCESS")
            
            # Test set/get
            test_key = "connection_test"
            test_value = "test_value"
            redis_client.set(test_key, test_value, ttl=10)
            retrieved = redis_client.get(test_key)
            
            if retrieved == test_value:
                print("   Set/Get operations: SUCCESS")
            else:
                print("   Set/Get operations: FAILED")
            
            # Cleanup
            redis_client.delete(test_key)
            
            return True
        else:
            print("❌ Redis connection: FAILED")
            return False
            
    except Exception as e:
        print(f"❌ Redis connection error: {str(e)}")
        return False


def test_kafka_connection():
    """Test Kafka connection"""
    print("\n" + "="*50)
    print("Testing Kafka Connection...")
    print("="*50)
    
    try:
        bootstrap_servers = settings.KAFKA_BOOTSTRAP_SERVERS.split(',')
        
        print(f"Bootstrap Servers: {bootstrap_servers}")
        print(f"Security Protocol: {settings.KAFKA_SECURITY_PROTOCOL}")
        print(f"SASL Mechanism: {settings.KAFKA_SASL_MECHANISM}")
        
        # Create admin client to test connection
        admin_config = {
            'bootstrap_servers': bootstrap_servers,
        }
        
        # Add SSL configuration if needed
        if settings.KAFKA_SECURITY_PROTOCOL in ['SSL', 'SASL_SSL']:
            if settings.KAFKA_SSL_CAFILE:
                admin_config['ssl_cafile'] = settings.KAFKA_SSL_CAFILE
            if settings.KAFKA_SSL_CERTFILE:
                admin_config['ssl_certfile'] = settings.KAFKA_SSL_CERTFILE
            if settings.KAFKA_SSL_KEYFILE:
                admin_config['ssl_keyfile'] = settings.KAFKA_SSL_KEYFILE
        
        # Add SASL configuration if needed
        if settings.KAFKA_SECURITY_PROTOCOL in ['SASL_PLAINTEXT', 'SASL_SSL']:
            if settings.KAFKA_SASL_MECHANISM:
                admin_config['sasl_mechanism'] = settings.KAFKA_SASL_MECHANISM
            if settings.KAFKA_SASL_USERNAME:
                admin_config['sasl_plain_username'] = settings.KAFKA_SASL_USERNAME
            if settings.KAFKA_SASL_PASSWORD:
                admin_config['sasl_plain_password'] = settings.KAFKA_SASL_PASSWORD
        
        admin_config['security_protocol'] = settings.KAFKA_SECURITY_PROTOCOL
        
        admin_client = KafkaAdminClient(**admin_config)
        
        # List topics to test connection
        topics = admin_client.list_topics()
        print(f"✅ Kafka connection: SUCCESS")
        print(f"   Available topics: {len(topics)} topics")
        
        admin_client.close()
        return True
        
    except KafkaError as e:
        print(f"❌ Kafka connection error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Kafka connection error: {str(e)}")
        return False


def test_mqtt_connection():
    """Test MQTT connection"""
    print("\n" + "="*50)
    print("Testing MQTT Connection...")
    print("="*50)
    
    try:
        import paho.mqtt.client as mqtt
        import time
        
        print(f"Host: {settings.MQTT_BROKER_HOST}")
        print(f"Port: {settings.MQTT_BROKER_PORT}")
        print(f"SSL: {settings.MQTT_SSL}")
        print(f"Username: {settings.MQTT_USERNAME if settings.MQTT_USERNAME else 'None'}")
        
        client = mqtt.Client(client_id="test_connection")
        
        if settings.MQTT_USERNAME and settings.MQTT_PASSWORD:
            client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
        
        if settings.MQTT_SSL:
            if settings.MQTT_SSL_CA_CERTS:
                client.tls_set(ca_certs=settings.MQTT_SSL_CA_CERTS)
            else:
                client.tls_set()
        
        connected = False
        
        def on_connect(client, userdata, flags, rc):
            nonlocal connected
            if rc == 0:
                connected = True
        
        client.on_connect = on_connect
        client.connect(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT, 60)
        client.loop_start()
        
        # Wait for connection
        timeout = 5
        elapsed = 0
        while not connected and elapsed < timeout:
            time.sleep(0.1)
            elapsed += 0.1
        
        client.loop_stop()
        client.disconnect()
        
        if connected:
            print("✅ MQTT connection: SUCCESS")
            return True
        else:
            print("❌ MQTT connection: FAILED (Timeout)")
            return False
            
    except Exception as e:
        print(f"❌ MQTT connection error: {str(e)}")
        return False


def test_opcua_connection():
    """Test OPC-UA connection"""
    print("\n" + "="*50)
    print("Testing OPC-UA Connection...")
    print("="*50)
    
    try:
        from asyncua import Client
        
        print(f"Server URL: {settings.OPCUA_SERVER_URL}")
        print(f"Security Policy: {settings.OPCUA_SECURITY_POLICY}")
        print(f"Security Mode: {settings.OPCUA_SECURITY_MODE}")
        
        # This is a simplified test - OPC-UA requires async context
        print("⚠️  OPC-UA connection test requires async context")
        print("   Please test OPC-UA connection using the ingestion service")
        return None
        
    except ImportError:
        print("⚠️  OPC-UA library not installed (asyncua)")
        print("   Install with: pip install asyncua")
        return None
    except Exception as e:
        print(f"❌ OPC-UA connection error: {str(e)}")
        return False


def main():
    """Run all connection tests"""
    print("="*50)
    print("Remote Connection Test Script")
    print("="*50)
    
    results = {}
    
    # Test Database
    results['database'] = test_database_connection()
    
    # Test Redis
    results['redis'] = test_redis_connection()
    
    # Test Kafka
    results['kafka'] = test_kafka_connection()
    
    # Test MQTT
    results['mqtt'] = test_mqtt_connection()
    
    # Test OPC-UA
    results['opcua'] = test_opcua_connection()
    
    # Summary
    print("\n" + "="*50)
    print("Connection Test Summary")
    print("="*50)
    
    for service, result in results.items():
        if result is True:
            print(f"✅ {service.upper()}: SUCCESS")
        elif result is False:
            print(f"❌ {service.upper()}: FAILED")
        else:
            print(f"⚠️  {service.upper()}: SKIPPED")
    
    # Exit code
    failed = [k for k, v in results.items() if v is False]
    if failed:
        print(f"\n❌ {len(failed)} service(s) failed: {', '.join(failed)}")
        sys.exit(1)
    else:
        print("\n✅ All connections successful!")
        sys.exit(0)


if __name__ == "__main__":
    main()

