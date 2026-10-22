"""
FinancePilot AI - ML Prediction API
FastAPI service for ML model inference
"""

import os
import json
import joblib
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import numpy as np

# Configuration
ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), 'artifacts')
MODEL_PATH = os.path.join(ARTIFACTS_DIR, 'model.joblib')
METRICS_PATH = os.path.join(ARTIFACTS_DIR, 'metrics.json')
FEATURE_SCHEMA_PATH = os.path.join(ARTIFACTS_DIR, 'feature_schema.json')
FEATURE_IMPORTANCE_PATH = os.path.join(ARTIFACTS_DIR, 'feature_importance.json')
METADATA_PATH = os.path.join(ARTIFACTS_DIR, 'metadata.json')
DEMO_SAMPLE_PATH = os.path.join(ARTIFACTS_DIR, 'demo_sample.json')
DEMO_LABEL_PATH = os.path.join(ARTIFACTS_DIR, 'demo_label.json')

# Initialize FastAPI
app = FastAPI(
    title="FinancePilot ML API",
    description="Machine Learning inference service for credit default prediction",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Global variables
model = None
feature_schema = None
metrics = None
feature_importance = None
metadata = None
demo_sample = None
demo_label = None


def load_artifacts():
    """Load model and artifacts at startup"""
    global model, feature_schema, metrics, feature_importance, metadata, demo_sample, demo_label

    print("Loading ML artifacts...")

    # Load model
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        print(f"Model loaded from: {MODEL_PATH}")
    else:
        print(f"Warning: Model not found at {MODEL_PATH}")

    # Load feature schema
    if os.path.exists(FEATURE_SCHEMA_PATH):
        with open(FEATURE_SCHEMA_PATH, 'r') as f:
            feature_schema = json.load(f)
        print(f"Feature schema loaded from: {FEATURE_SCHEMA_PATH}")
    else:
        print(f"Warning: Feature schema not found at {FEATURE_SCHEMA_PATH}")

    # Load metrics
    if os.path.exists(METRICS_PATH):
        with open(METRICS_PATH, 'r') as f:
            metrics = json.load(f)
        print(f"Metrics loaded from: {METRICS_PATH}")
    else:
        print(f"Warning: Metrics not found at {METRICS_PATH}")

    # Load feature importance
    if os.path.exists(FEATURE_IMPORTANCE_PATH):
        with open(FEATURE_IMPORTANCE_PATH, 'r') as f:
            feature_importance = json.load(f)
        print(f"Feature importance loaded from: {FEATURE_IMPORTANCE_PATH}")
    else:
        print(f"Warning: Feature importance not found at {FEATURE_IMPORTANCE_PATH}")

    # Load metadata
    if os.path.exists(METADATA_PATH):
        with open(METADATA_PATH, 'r') as f:
            metadata = json.load(f)
        print(f"Metadata loaded from: {METADATA_PATH}")
    else:
        print(f"Warning: Metadata not found at {METADATA_PATH}")

    # Load demo sample
    if os.path.exists(DEMO_SAMPLE_PATH):
        with open(DEMO_SAMPLE_PATH, 'r') as f:
            demo_sample = json.load(f)
        print(f"Demo sample loaded from: {DEMO_SAMPLE_PATH}")
    else:
        print(f"Warning: Demo sample not found at {DEMO_SAMPLE_PATH}")

    # Load demo label
    if os.path.exists(DEMO_LABEL_PATH):
        with open(DEMO_LABEL_PATH, 'r') as f:
            demo_label = json.load(f)
        print(f"Demo label loaded from: {DEMO_LABEL_PATH}")
    else:
        print(f"Warning: Demo label not found at {DEMO_LABEL_PATH}")

    print("Artifact loading completed")


# Load artifacts on startup
@app.on_event("startup")
async def startup_event():
    load_artifacts()


# Pydantic models
class PredictionRequest(BaseModel):
    features: Dict[str, float] = Field(..., description="Feature values for prediction")


class PredictionResponse(BaseModel):
    model_type: str
    prediction: int
    model_estimated_probability_of_default: float
    probability_is_calibrated: bool
    model_version: str
    dataset: str
    limitations: List[str]
    feature_importance: Optional[Dict[str, float]] = None


# Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "artifacts_loaded": all([
            model is not None,
            feature_schema is not None,
            metrics is not None,
        ])
    }


@app.get("/metrics")
async def get_metrics():
    """Get model evaluation metrics"""
    if metrics is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Metrics not available. Model may not be trained yet."
        )
    return metrics


@app.get("/feature-importance")
async def get_feature_importance():
    """Get feature importance"""
    if feature_importance is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Feature importance not available. Model may not be trained yet."
        )
    return feature_importance


@app.get("/schema")
async def get_schema():
    """Get feature schema"""
    if feature_schema is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Feature schema not available. Model may not be trained yet."
        )
    return feature_schema


@app.get("/metadata")
async def get_metadata():
    """Get model metadata"""
    if metadata is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Metadata not available. Model may not be trained yet."
        )
    return metadata


@app.get("/predict-demo", response_model=PredictionResponse)
async def predict_demo():
    """Get prediction for demo sample (held-out test record)"""
    if model is None or demo_sample is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model or demo sample not available. Run training first."
        )

    try:
        # Convert demo sample to feature array
        feature_names = feature_schema['features']
        features_array = [demo_sample.get(name, 0) for name in feature_names]
        features_array = np.array(features_array).reshape(1, -1)

        # Make prediction
        prediction = int(model.predict(features_array)[0])
        probability = float(model.predict_proba(features_array)[0, 1])

        # Build response
        response = {
            "model_type": metadata.get('model_type', 'RandomForestClassifier'),
            "prediction": prediction,
            "model_estimated_probability_of_default": probability,
            "probability_is_calibrated": False,
            "model_version": metadata.get('model_version', 'v1'),
            "dataset": metadata.get('dataset', 'UCI Default of Credit Card Clients'),
            "limitations": metadata.get('limitations', []),
            "feature_importance": feature_importance,
        }

        # Add demo-specific disclaimer
        response['limitations'].append(
            "This is a historical example from the test set, not a live prediction"
        )

        return response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """Make prediction for provided features"""
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not available. Run training first."
        )

    if feature_schema is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Feature schema not available."
        )

    try:
        # Validate features
        feature_names = feature_schema['features']
        missing_features = set(feature_names) - set(request.features.keys())

        if missing_features:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required features: {missing_features}"
            )

        # Check for extra features
        extra_features = set(request.features.keys()) - set(feature_names)
        if extra_features:
            print(f"Warning: Extra features provided (will be ignored): {extra_features}")

        # Convert to feature array
        features_array = [request.features[name] for name in feature_names]
        features_array = np.array(features_array).reshape(1, -1)

        # Validate numerical types
        if not all(isinstance(f, (int, float)) for f in features_array):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="All feature values must be numerical"
            )

        # Check for infinite or NaN values
        if not all(np.isfinite(features_array)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Feature values must be finite (no NaN or infinite values)"
            )

        # Make prediction
        prediction = int(model.predict(features_array)[0])
        probability = float(model.predict_proba(features_array)[0, 1])

        # Build response
        response = {
            "model_type": metadata.get('model_type', 'RandomForestClassifier'),
            "prediction": prediction,
            "model_estimated_probability_of_default": probability,
            "probability_is_calibrated": False,
            "model_version": metadata.get('model_version', 'v1'),
            "dataset": metadata.get('dataset', 'UCI Default of Credit Card Clients'),
            "limitations": metadata.get('limitations', []),
            "feature_importance": feature_importance,
        }

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
