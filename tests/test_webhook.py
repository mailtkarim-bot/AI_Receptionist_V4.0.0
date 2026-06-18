"""Webhook endpoint tests."""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import Base, engine

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "AI Receptionist" in response.json()["service"]

def test_calls_auth_required():
    response = client.get("/calls")
    assert response.status_code == 401

def test_stats_auth_required():
    response = client.get("/stats")
    assert response.status_code == 401