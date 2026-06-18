"""Webhook endpoint tests."""

import pytest
import hmac
import hashlib
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
    assert data["database"] == "connected"


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


def test_webhook_without_signature_fails():
    response = client.post("/vapi-webhook", json={"test": "data"})
    assert response.status_code == 401


def test_webhook_idempotence():
    from backend import config
    secret = "test_secret"
    config.settings.VAPI_WEBHOOK_SECRET = secret

    body = '{"call": {"id": "dup-test-001", "customer": {"number": "+1234567890"}}, "status": "completed"}'
    sig = hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()

    headers = {"X-Vapi-Signature": sig, "Content-Type": "application/json"}

    r1 = client.post("/vapi-webhook", headers=headers, data=body)
    assert r1.status_code == 200
    assert r1.json()["duplicate"] is not True

    r2 = client.post("/vapi-webhook", headers=headers, data=body)
    assert r2.status_code == 200
    assert r2.json()["duplicate"] is True


def test_webhook_emergency_handling(monkeypatch):
    from backend import config
    secret = "test_secret"
    config.settings.VAPI_WEBHOOK_SECRET = secret
    monkeypatch.setattr(config.settings, "EMERGENCY_PHONE_NUMBER", "+9999999999")
    monkeypatch.setattr(config.settings, "TWILIO_PHONE_NUMBER", "+1111111111")
    monkeypatch.setattr(config.settings, "TWILIO_ACCOUNT_SID", "AC_test")
    monkeypatch.setattr(config.settings, "TWILIO_AUTH_TOKEN", "test_token")

    body = '{"call": {"id": "emergency-001", "customer": {"number": "+1234567890"}}, "status": "completed", "analysis": {"is_emergency": true}}'
    sig = hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()

    headers = {"X-Vapi-Signature": sig, "Content-Type": "application/json"}
    r = client.post("/vapi-webhook", headers=headers, data=body)
    assert r.status_code == 200
