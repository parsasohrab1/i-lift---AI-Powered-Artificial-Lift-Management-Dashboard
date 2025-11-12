"""
Script to start MQTT data ingestion
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.ingestion.ingestion_service import IngestionService
from app.core.config import settings

def main():
    """Start MQTT ingestion"""
    service = IngestionService()
    service.initialize()
    
    # Start MQTT ingestion
    service.start_mqtt_ingestion(
        broker_host="localhost",
        broker_port=1883,
        topics=[
            "sensors/+/+",  # sensors/well_id/sensor_type
            "wells/+/data",  # wells/well_id/data
        ]
    )
    
    print("MQTT ingestion started. Press Ctrl+C to stop.")
    
    try:
        while True:
            stats = service.get_stats()
            print(f"\nStats: {stats}")
            time.sleep(10)
    except KeyboardInterrupt:
        print("\nStopping MQTT ingestion...")
        service.stop_mqtt_ingestion()
        service.shutdown()
        print("Stopped.")

if __name__ == "__main__":
    main()

