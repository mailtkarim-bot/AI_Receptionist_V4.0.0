"""Tests for HMAC webhook security verification."""

import hmac
import hashlib
import pytest
from fastapi import HTTPException
from backend.security import verify_vapi_signature, validate_webhook_request


class TestVerifyVapiSignature:
    """Test suite for HMAC signature verification."""

    def test_valid_signature(self):
        """Should return True for valid HMAC signature."""
        secret = "test_secret_key"
        body = b'{"test": "data"}'
        expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        
        assert verify_vapi_signature(body, expected) is True

    def test_invalid_signature(self):
        """Should return False for invalid HMAC signature."""
        body = b'{"test": "data"}'
        assert verify_vapi_signature(body, "invalid_signature") is False

    def test_empty_secret_dev_mode(self, monkeypatch):
        """Should return True when secret is empty (dev mode)."""
        from backend import config
        monkeypatch.setattr(config.settings, "VAPI_WEBHOOK_SECRET", "")
        body = b'{"test": "data"}'
        assert verify_vapi_signature(body, "any_signature") is True

    def test_tampered_body(self):
        """Should detect tampered request body."""
        secret = "test_secret_key"
        original_body = b'{"test": "data"}'
        tampered_body = b'{"test": "tampered"}'
        expected = hmac.new(secret.encode(), original_body, hashlib.sha256).hexdigest()
        
        assert verify_vapi_signature(tampered_body, expected) is False


class TestValidateWebhookRequest:
    """Test suite for webhook request validation."""

    @pytest.mark.asyncio
    async def test_valid_request(self, monkeypatch):
        """Should parse valid request with correct signature."""
        from backend import config
        secret = "test_secret"
        monkeypatch.setattr(config.settings, "VAPI_WEBHOOK_SECRET", secret)
        
        body = b'{"call": {"id": "test-123"}}'
        signature = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        
        class MockRequest:
            async def body(self):
                return body
            @property
            def headers(self):
                return {"X-Vapi-Signature": signature}
        
        result = await validate_webhook_request(MockRequest())
        assert result["call"]["id"] == "test-123"

    @pytest.mark.asyncio
    async def test_invalid_signature_raises_401(self, monkeypatch):
        """Should raise 401 for invalid signature."""
        from backend import config
        monkeypatch.setattr(config.settings, "VAPI_WEBHOOK_SECRET", "secret")
        
        class MockRequest:
            async def body(self):
                return b'{}'
            @property
            def headers(self):
                return {"X-Vapi-Signature": "invalid"}
        
        with pytest.raises(HTTPException) as exc_info:
            await validate_webhook_request(MockRequest())
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_invalid_json_raises_400(self, monkeypatch):
        """Should raise 400 for invalid JSON."""
        from backend import config
        monkeypatch.setattr(config.settings, "VAPI_WEBHOOK_SECRET", "")
        
        class MockRequest:
            async def body(self):
                return b'not json'
            @property
            def headers(self):
                return {}
        
        with pytest.raises(HTTPException) as exc_info:
            await validate_webhook_request(MockRequest())
        assert exc_info.value.status_code == 400
