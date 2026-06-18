"""Security utilities -- HMAC webhook verification + input sanitization."""

import hmac
import hashlib
import json
import re
from fastapi import HTTPException, Request
from backend.config import settings


def sanitize_phone(phone: str | None) -> str | None:
    """Remove all non-digit characters except leading +."""
    if not phone:
        return None
    cleaned = re.sub(r'[^\d+]', '', phone)
    if cleaned.startswith('+'):
        return '+' + re.sub(r'\D', '', cleaned[1:])
    return cleaned


def verify_vapi_signature(request_body: bytes, signature: str) -> bool:
    """Verify HMAC-SHA256 signature from Vapi webhook."""
    if not settings.VAPI_WEBHOOK_SECRET:
        return True

    expected = hmac.new(
        settings.VAPI_WEBHOOK_SECRET.encode(),
        request_body,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature)


async def validate_webhook_request(request: Request) -> dict:
    """Validate incoming webhook request with HMAC signature."""
    body = await request.body()
    signature = request.headers.get("X-Vapi-Signature", "")

    if not verify_vapi_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    try:
        return json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")