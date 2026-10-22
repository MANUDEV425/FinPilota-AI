"""
Basic tests for ML API
"""

import pytest
import os
import json
from fastapi.testclient import TestClient

# Import the app
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from api import app

client = TestClient(app)


def test_health_check():
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"


def test_metrics():
    """Test metrics endpoint"""
    response = client.get("/metrics")
    # May return 503 if model not trained
    assert response.status_code in [200, 503]


def test_feature_importance():
    """Test feature importance endpoint"""
    response = client.get("/feature-importance")
    # May return 503 if model not trained
    assert response.status_code in [200, 503]


def test_predict_demo():
    """Test demo prediction endpoint"""
    response = client.get("/predict-demo")
    # May return 503 if model not trained
    assert response.status_code in [200, 503]


def test_predict_invalid():
    """Test prediction with invalid input"""
    response = client.post("/predict", json={})
    # Should return 400 or 503
    assert response.status_code in [400, 503]


if __name__ == "__main__":
    print("Running basic ML API tests...")
    test_health_check()
    print("✓ Health check passed")
    test_metrics()
    print("✓ Metrics endpoint test passed")
    test_feature_importance()
    print("✓ Feature importance test passed")
    test_predict_demo()
    print("✓ Demo prediction test passed")
    test_predict_invalid()
    print("✓ Invalid prediction test passed")
    print("\nAll tests completed!")
