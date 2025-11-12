"""
Script to start OPC-UA data ingestion
"""
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.ingestion.ingestion_service import IngestionService
from app.core.config import settings


async def main():
    """Start OPC-UA ingestion"""
    service = IngestionService()
    service.initialize()
    
    # OPC-UA server endpoint
    endpoint_url = "opc.tcp://localhost:4840/freeopcua/server/"
    
    # Node IDs to monitor (example)
    node_ids = [
        "ns=2;s=Well_01.MotorTemperature",
        "ns=2;s=Well_01.IntakePressure",
        "ns=2;s=Well_01.DischargePressure",
    ]
    
    try:
        # Start OPC-UA ingestion
        await service.start_opcua_ingestion(
            endpoint_url=endpoint_url,
            node_ids=node_ids,
            sampling_interval=1000,  # 1 second
        )
        
        print("OPC-UA ingestion started. Press Ctrl+C to stop.")
        
        # Keep running
        while True:
            stats = service.get_stats()
            print(f"\nStats: {stats}")
            await asyncio.sleep(10)
            
    except KeyboardInterrupt:
        print("\nStopping OPC-UA ingestion...")
        await service.stop_opcua_ingestion()
        service.shutdown()
        print("Stopped.")
    except Exception as e:
        print(f"Error: {e}")
        service.shutdown()


if __name__ == "__main__":
    asyncio.run(main())

