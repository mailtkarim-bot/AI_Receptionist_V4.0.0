"""End-to-end integration tests."""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import Base, engine
from backend.models_db import CallRecord

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_dashboard_without_auth_fails():
    response = client.get("/calls")
    assert response.status_code == 401

def test_login_and_access_dashboard():
    response = client.post("/token", data={"username": "admin", "password": "changeme123"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    response = client.get("/calls", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_webhook_without_auth_fails():
    response = client.post("/vapi-webhook", json={"test": "data"})
    assert response.status_code == 401