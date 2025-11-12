"""
Script to train ML models
"""
import argparse
import sys
from pathlib import Path
import pandas as pd
from pipeline import MLPipeline

def main():
    parser = argparse.ArgumentParser(description="Train ML models")
    parser.add_argument(
        "--model-type",
        type=str,
        required=True,
        choices=["anomaly_detection", "predictive_maintenance", "all"],
        help="Type of model to train",
    )
    parser.add_argument(
        "--data-path",
        type=str,
        required=True,
        help="Path to training data CSV file",
    )
    parser.add_argument(
        "--contamination",
        type=float,
        default=0.1,
        help="Contamination rate for anomaly detection (default: 0.1)",
    )
    parser.add_argument(
        "--n-estimators",
        type=int,
        default=100,
        help="Number of estimators (default: 100)",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=10,
        help="Max depth for predictive maintenance (default: 10)",
    )
    parser.add_argument(
        "--random-state",
        type=int,
        default=42,
        help="Random state (default: 42)",
    )
    
    args = parser.parse_args()
    
    # Check if data file exists
    data_path = Path(args.data_path)
    if not data_path.exists():
        print(f"Error: Data file not found: {data_path}")
        sys.exit(1)
    
    # Load data
    print(f"Loading data from {data_path}...")
    try:
        data = pd.read_csv(data_path)
        print(f"Loaded {len(data)} samples with {len(data.columns)} columns")
    except Exception as e:
        print(f"Error loading data: {e}")
        sys.exit(1)
    
    # Initialize pipeline
    pipeline = MLPipeline()
    
    # Train models
    if args.model_type in ["anomaly_detection", "all"]:
        print("\n" + "="*50)
        print("Training Anomaly Detection Model")
        print("="*50)
        result = pipeline.train_anomaly_detection(
            data,
            contamination=args.contamination,
            n_estimators=args.n_estimators,
            random_state=args.random_state,
        )
        if result.get("success"):
            print("✓ Anomaly detection model trained successfully")
            print(f"  Anomaly rate: {result['metrics']['anomaly_rate']:.2%}")
        else:
            print(f"✗ Failed to train anomaly detection model: {result.get('error')}")
            sys.exit(1)
    
    if args.model_type in ["predictive_maintenance", "all"]:
        print("\n" + "="*50)
        print("Training Predictive Maintenance Model")
        print("="*50)
        result = pipeline.train_predictive_maintenance(
            data,
            n_estimators=args.n_estimators,
            max_depth=args.max_depth,
            random_state=args.random_state,
        )
        if result.get("success"):
            print("✓ Predictive maintenance model trained successfully")
            print(f"  RMSE: {result['metrics']['rmse']:.4f}")
            print(f"  MAE: {result['metrics']['mae']:.4f}")
        else:
            print(f"✗ Failed to train predictive maintenance model: {result.get('error')}")
            sys.exit(1)
    
    print("\n" + "="*50)
    print("Training completed successfully!")
    print("="*50)
    
    # List models
    models = pipeline.list_models()
    print(f"\nRegistered models: {len(models)}")
    for model in models:
        print(f"  - {model['model_type']}: {model['status']} (v{model['version']})")

if __name__ == "__main__":
    main()

