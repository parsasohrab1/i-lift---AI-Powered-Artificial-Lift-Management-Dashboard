"""
Script to start data processing pipeline
"""
import sys
import time
import signal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.processing.pipeline import DataProcessingPipeline
from app.core.config import settings


def signal_handler(sig, frame):
    """Handle shutdown signal"""
    print("\nShutting down pipeline...")
    if pipeline:
        pipeline.stop()
    sys.exit(0)


def main():
    """Start processing pipeline"""
    global pipeline
    
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and start pipeline
    pipeline = DataProcessingPipeline(
        batch_size=100,
        window_size=60,
    )
    
    try:
        pipeline.start()
        print("Data processing pipeline started. Press Ctrl+C to stop.")
        
        # Monitor stats
        while True:
            stats = pipeline.get_stats()
            print(f"\nPipeline Stats:")
            print(f"  Total Processed: {stats['total_processed']}")
            print(f"  Total Errors: {stats['total_errors']}")
            print(f"  Processing Rate: {stats['processing_rate']:.2f} msg/s")
            print(f"  Database Writer Buffer: {stats['database_writer']['buffer_size']}")
            print(f"  Database Total Written: {stats['database_writer']['total_written']}")
            
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\nStopping pipeline...")
    finally:
        pipeline.stop()
        print("Pipeline stopped.")


if __name__ == "__main__":
    pipeline = None
    main()

