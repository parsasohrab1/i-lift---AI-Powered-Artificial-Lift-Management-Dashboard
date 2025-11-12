"""
Script to start alert monitoring service
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.alert_detection_service import AlertDetectionService
from app.core.database import get_db
from app.utils.logger import setup_logging

logger = setup_logging()


async def main():
    """Main function to start alert monitoring"""
    logger.info("Starting alert monitoring service...")
    
    db = next(get_db())
    service = AlertDetectionService(db=db)
    
    try:
        # Start monitoring
        await service.monitor_sensor_data(interval_seconds=60)
    except KeyboardInterrupt:
        logger.info("Stopping alert monitoring service...")
        service.stop_monitoring()
    except Exception as e:
        logger.error(f"Error in alert monitoring: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())

