"""End-to-end integration tests."""

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

    # Verify cookies are set
    assert "set-cookie" in response.headers
    assert "ai_token" in response.headers["set-cookie"]
    assert "ai_refresh" in response.headers["set-cookie"]

    response = client.get("/calls", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_refresh_token_rotation():
    # Login
    r1 = client.post("/token", data={"username": "admin", "password": "changeme123"})
    assert r1.status_code == 200

    # Refresh
    r2 = client.post("/refresh")
    assert r2.status_code == 200
    assert "access_token" in r2.json()
    assert "ai_token" in r2.headers.get("set-cookie", "")


def test_logout_clears_cookies():
    client.post("/token", data={"username": "admin", "password": "changeme123"})
    response = client.post("/logout")
    assert response.status_code == 200
    set_cookie = response.headers.get("set-cookie", "")
    assert "ai_token" in set_cookie or "Max-Age=0" in set_cookie


def test_gdpr_erase():
    # Login
    login = client.post("/token", data={"username": "admin", "password": "changeme123"})
    token = login.json()["access_token"]

    # Create a record via webhook
    import hmac, hashlib
    from backend import config
    secret = "test_secret"
    config.settings.VAPI_WEBHOOK_SECRET = secret
    body = '{"call": {"id": "erase-001", "customer": {"number": "+1234567890"}}, "status": "completed"}'
    sig = hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()
    client.post("/vapi-webhook", headers={"X-Vapi-Signature": sig, "Content-Type": "application/json"}, data=body)

    # Erase
    phone_hash = hashlib.sha256("+1234567890".encode()).hexdigest()
    r = client.delete(f"/patients/{phone_hash}", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["success"] is True
    assert "Anonymized" in r.json()["message"]


def test_webhook_without_auth_fails():
    response = client.post("/vapi-webhook", json={"test": "data"})
    assert response.status_code == 401
