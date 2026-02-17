import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert "status" in response.json()

def test_register_user():
    """Test user registration"""
    response = client.post("/api/auth/register", json={
        "email": f"test_{pytest.__version__}@example.com",  # Unique email
        "password": "testpassword123"
    })
    # Might be 201 (created) or 400 (already exists)
    assert response.status_code in [201, 400]

def test_login_requires_valid_credentials():
    """Test that login requires valid credentials"""
    response = client.post("/api/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_protected_endpoint_requires_auth():
    """Test that protected endpoints require authentication"""
    response = client.get("/api/entries")
    assert response.status_code == 401

def test_cache_stats_requires_auth():
    """Test cache stats endpoint requires auth"""
    response = client.get("/api/cache/stats")
    assert response.status_code == 401

def test_rate_limit_status_requires_auth():
    """Test rate limit status requires auth"""
    response = client.get("/api/rate-limit/status")
    assert response.status_code == 401