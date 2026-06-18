"""Security utilities — HMAC webhook verification + replay protection."""

import hmac
import hashlib
import json
import re
import time
from fastapi import HTTPException, Request
from backend.config import settings

# Window de tolérance pour les timestamps (5 minutes)
REPLAY_WINDOW_SECONDS = 300
MAX_BODY_SIZE = 1024 * 1024  # 1 MB


def sanitize_phone(phone: str | None) -> str | None:
    if not phone:
        return None
    cleaned = re.sub(r'[^\d+]', '', phone)
    if cleaned.startswith('+'):
        return '+' + re.sub(r'\D', '', cleaned[1:])
    return cleaned


def verify_vapi_signature(request_body: bytes, signature: str) -> bool:
    if not settings.VAPI_WEBHOOK_SECRET:
        raise RuntimeError("VAPI_WEBHOOK_SECRET is not configured — webhook verification disabled")
    expected = hmac.new(
        settings.VAPI_WEBHOOK_SECRET.encode(),
        request_body,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


async def validate_webhook_request(request: Request) -> dict:
    body = await request.body()
    if len(body) > MAX_BODY_SIZE:
        raise HTTPException(status_code=413, detail="Payload too large")

    signature = request.headers.get("X-Vapi-Signature", "")
    if not verify_vapi_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    # Replay protection via timestamp (si Vapi l'envoie)
    timestamp_header = request.headers.get("X-Vapi-Timestamp", "")
    if timestamp_header:
        try:
            ts = int(timestamp_header)
            now = int(time.time())
            if abs(now - ts) > REPLAY_WINDOW_SECONDS:
                raise HTTPException(status_code=401, detail="Webhook timestamp expired")
        except ValueError:
            raise HTTPException(status_code=401, detail="Invalid webhook timestamp")

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # Validation Pydantic structure
    from backend.models import VapiWebhookPayload
    try:
        VapiWebhookPayload(**payload)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid payload structure: {e}")

    return payload
