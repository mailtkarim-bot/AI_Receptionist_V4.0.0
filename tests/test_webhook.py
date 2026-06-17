"""Tests for webhook endpoint and API."""

import json
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


class TestWebhookEndpoint:
    """Test suite for /vapi-webhook endpoint."""

    def test_webhook_no_signature_dev_mode(self, monkeypatch):
        """Should accept webhook in dev mode (no secret)."""
        from backend import config
        monkeypatch.setattr(config.settings, "VAPI_WEBHOOK_SECRET", "")
        
        payload = {
            "call": {"id": "test-001", "customer": {"number": "+1234567890"}},
            "status": "completed",
            "analysis": {"booked_appointment": {"date": "2026-06-20", "time": "14:00"}},
        }
        
        response = client.post("/vapi-webhook", json=payload)
        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_webhook_invalid_signature(self, monkeypatch):
        """Should reject webhook with invalid signature."""
        from backend import config
        monkeypatch.setattr(config.settings, "VAPI_WEBHOOK_SECRET", "secret")
        
        response = client.post(
            "/vapi-webhook",
            json={"test": "data"},
            headers={"X-Vapi-Signature": "invalid"},
        )
        assert response.status_code == 401

    def test_health_endpoint(self):
        """Should return health status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "ai-receptionist"

    def test_calls_endpoint(self):
        """Should return calls list."""
        response = client.get("/calls")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_stats_endpoint(self):
        """Should return daily statistics."""
        response = client.get("/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "booked" in data
        assert "missed" in data

    def test_root_endpoint(self):
        """Should return API info."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["service"] == "AI Receptionist Enterprise"

    def test_calls_filter_by_status(self, monkeypatch):
        """Should filter calls by status."""
        # Mock some logs
        mock_logs = [
            {"timestamp": "2026-06-17T10:00:00", "status": "completed", "phone": "+111"},
            {"timestamp": "2026-06-17T10:05:00", "status": "no-answer", "phone": "+222"},
        ]
        monkeypatch.setattr("backend.main._load_logs", lambda: mock_logs)
        
        response = client.get("/calls?status=completed")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "completed"

    def test_calls_filter_by_phone(self, monkeypatch):
        """Should filter calls by phone number."""
        mock_logs = [
            {"timestamp": "2026-06-17T10:00:00", "status": "completed", "phone": "+1234567890"},
            {"timestamp": "2026-06-17T10:05:00", "status": "completed", "phone": "+9998887777"},
        ]
        monkeypatch.setattr("backend.main._load_logs", lambda: mock_logs)
        
        response = client.get("/calls?phone=12345")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "12345" in data[0]["phone"]
