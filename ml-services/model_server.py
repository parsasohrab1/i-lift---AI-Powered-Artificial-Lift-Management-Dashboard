"""
ML Model Server
Serves ML models via REST API
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import uvicorn
from pipeline import MLPipeline

app = FastAPI(title="ML Model Server", version="1.0.0")

# Initialize pipeline
pipeline = MLPipeline()


class PredictionRequest(BaseModel):
    """Prediction request model"""
    well_id: str
    features: Dict[str, float]
    model_type: str


class TrainingRequest(BaseModel):
    """Training request model"""
    model_type: str
    data_path: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "ML Model Server",
        "version": "1.0.0",
        "models": pipeline.list_models(),
    }


@app.get("/models")
async def list_models():
    """List all available models"""
    return {
        "models": pipeline.list_models(),
    }


@app.get("/models/{model_type}")
async def get_model_info(model_type: str):
    """Get model information"""
    model_info = pipeline.get_model_info(model_type)
    if not model_info:
        raise HTTPException(status_code=404, detail=f"Model {model_type} not found")
    return model_info


@app.post("/predict")
async def predict(request: PredictionRequest):
    """Make a prediction"""
    try:
        if request.model_type == "anomaly_detection":
            result = pipeline.predict_anomaly(request.features)
        elif request.model_type == "predictive_maintenance":
            result = pipeline.predict_failure(request.features)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown model type: {request.model_type}"
            )
        
        return {
            "well_id": request.well_id,
            "model_type": request.model_type,
            "prediction": result,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/train")
async def train_model(request: TrainingRequest):
    """Train a model"""
    try:
        import pandas as pd
        
        # Load data
        if request.data_path:
            data = pd.read_csv(request.data_path)
        else:
            # Use default data path
            data_path = pipeline.data_dir / "training_data.csv"
            if not data_path.exists():
                raise HTTPException(
                    status_code=404,
                    detail="Training data not found. Please provide data_path."
                )
            data = pd.read_csv(data_path)
        
        # Get parameters
        params = request.parameters or {}
        
        if request.model_type == "anomaly_detection":
            result = pipeline.train_anomaly_detection(
                data,
                contamination=params.get("contamination", 0.1),
                n_estimators=params.get("n_estimators", 100),
                random_state=params.get("random_state", 42),
            )
        elif request.model_type == "predictive_maintenance":
            result = pipeline.train_predictive_maintenance(
                data,
                target_column=params.get("target_column", "failure_probability"),
                n_estimators=params.get("n_estimators", 100),
                max_depth=params.get("max_depth", 10),
                random_state=params.get("random_state", 42),
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown model type: {request.model_type}"
            )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Training failed"))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/evaluate/{model_type}")
async def evaluate_model(model_type: str, test_data_path: str):
    """Evaluate a model"""
    try:
        import pandas as pd
        import numpy as np
        
        # Load test data
        data = pd.read_csv(test_data_path)
        
        # Prepare features
        feature_columns = [
            'motor_temperature',
            'intake_pressure',
            'discharge_pressure',
            'vibration',
            'current',
            'flow_rate',
        ]
        
        available_features = [col for col in feature_columns if col in data.columns]
        X_test = data[available_features].values
        
        # Prepare target for predictive maintenance
        if model_type == "predictive_maintenance":
            if "failure_probability" in data.columns:
                y_test = data["failure_probability"].values
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Test data must include 'failure_probability' column"
                )
        else:
            y_test = np.zeros(len(X_test))  # Dummy for anomaly detection
        
        result = pipeline.evaluate_model(model_type, X_test, y_test)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

