"""Tests for HMAC webhook security verification."""

import hmac
import hashlib
import pytest
from fastapi import HTTPException
from backend.security import verify_vapi_signature, validate_webhook_request, MAX_BODY_SIZE


class TestVerifyVapiSignature:
    def test_valid_signature(self):
        secret = "test_secret_key"
        body = b'{"test": "data"}'
        expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        assert verify_vapi_signature(body, expected) is True

    def test_invalid_signature(self):
        body = b'{"test": "data"}'
        assert verify_vapi_signature(body, "invalid_signature") is False

    def test_empty_secret_raises(self, monkeypatch):
        from backend import config
        monkeypatch.setattr(config.settings, "VAPI_WEBHOOK_SECRET", "")
        body = b'{"test": "data"}'
        with pytest.raises(RuntimeError, match="webhook verification disabled"):
            verify_vapi_signature(body, "any_signature")

    def test_tampered_body(self):
        secret = "test_secret_key"
        original_body = b'{"test": "data"}'
        tampered_body = b'{"test": "tampered"}'
        expected = hmac.new(secret.encode(), original_body, hashlib.sha256).hexdigest()
        assert verify_vapi_signature(tampered_body, expected) is False


class TestValidateWebhookRequest:
    @pytest.mark.asyncio
    async def test_valid_request(self, monkeypatch):
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

    @pytest.mark.asyncio
    async def test_payload_too_large_raises_413(self, monkeypatch):
        from backend import config
        monkeypatch.setattr(config.settings, "VAPI_WEBHOOK_SECRET", "secret")

        class MockRequest:
            async def body(self):
                return b'x' * (MAX_BODY_SIZE + 1)
            @property
            def headers(self):
                return {"X-Vapi-Signature": "dummy"}

        with pytest.raises(HTTPException) as exc_info:
            await validate_webhook_request(MockRequest())
        assert exc_info.value.status_code == 413
