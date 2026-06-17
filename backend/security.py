"""Security utilities -- HMAC webhook verification."""

import hmac
import hashlib
import json
from fastapi import HTTPException, Request
from backend.config import settings


def verify_vapi_signature(request_body: bytes, signature: str) -> bool:
    """Verify HMAC-SHA256 signature from Vapi webhook.
    
    Args:
        request_body: Raw request body bytes
        signature: X-Vapi-Signature header value
        
    Returns:
        True if signature is valid, False otherwise
    """
    if not settings.VAPI_WEBHOOK_SECRET:
        # In development, skip verification if no secret configured
        return True
        
    expected = hmac.new(
        settings.VAPI_WEBHOOK_SECRET.encode(),
        request_body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected, signature)


async def validate_webhook_request(request: Request) -> dict:
    """Validate incoming webhook request with HMAC signature.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        Parsed JSON body as dict
        
    Raises:
        HTTPException: 401 if signature is invalid
    """
    body = await request.body()
    signature = request.headers.get("X-Vapi-Signature", "")
    
    if not verify_vapi_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
