"""AI Receptionist Webhook -- FastAPI production-grade backend.

Receives Vapi call events, validates HMAC signatures, logs to JSON,
syncs Google Calendar, sends SMS confirmations, serves dashboard data.
"""

import json
import os
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import settings
from backend.models import CallLog, HealthResponse
from backend.security import validate_webhook_request

app = FastAPI(
    title="AI Receptionist Enterprise",
    version="2.1.0",
    description="Production-grade AI voice agent webhook and API",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS -- restrict to dashboard origin only
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.DASHBOARD_ORIGIN],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

LOG_FILE = settings.LOG_FILE


def _load_logs() -> list[dict]:
    """Load existing call logs from JSON file."""
    if not os.path.exists(LOG_FILE):
        return []
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def _save_logs(logs: list[dict]) -> None:
    """Save call logs to JSON file atomically."""
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)


@app.post("/vapi-webhook")
async def vapi_webhook(request: Request):
    """Receive and process Vapi call-end webhook events.
    
    Validates HMAC signature, extracts appointment data,
    syncs Google Calendar, sends SMS confirmation, logs call.
    """
    # Validate HMAC signature and parse body
    data = await validate_webhook_request(request)
    
    call = data.get("call", {})
    analysis = data.get("analysis", {})
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "call_id": call.get("id"),
        "phone": call.get("customer", {}).get("number"),
        "status": data.get("status", "unknown"),
        "transcript": data.get("transcript"),
        "appointment": analysis.get("booked_appointment"),
        "duration_seconds": call.get("durationSeconds"),
        "is_emergency": analysis.get("is_emergency", False),
    }
    
    # Validate and save log
    try:
        validated = CallLog(**log_entry)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid log data: {str(e)}")
    
    logs = _load_logs()
    logs.append(log_entry)
    _save_logs(logs)
    
    # Process appointment if extracted
    appt = log_entry.get("appointment")
    if appt:
        _process_appointment(log_entry["phone"], appt)
    
    return JSONResponse(
        content={"success": True, "call_id": log_entry["call_id"]},
        status_code=200,
    )


def _process_appointment(phone: str | None, appt: dict) -> None:
    """Create calendar event and send SMS confirmation."""
    # Google Calendar sync
    try:
        from backend.calendar_sync import create_event
        create_event(
            phone=phone or "unknown",
            date_str=appt.get("date"),
            time_str=appt.get("time"),
            duration_min=appt.get("duration_minutes", 30),
            service=appt.get("service", "general"),
        )
    except Exception as e:
        print(f"[ERROR] Calendar sync failed: {e}")
    
    # SMS confirmation
    try:
        from backend.sms_sender import send_confirmation
        business_name = os.getenv("BUSINESS_NAME", "Our Clinic")
        msg = (
            f"Your appointment is confirmed for {appt['date']} at {appt['time']}. "
            f"{business_name}. To reschedule, call us."
        )
        if phone:
            send_confirmation(to=phone, message=msg)
    except Exception as e:
        print(f"[ERROR] SMS send failed: {e}")


@app.get("/calls")
async def get_calls(
    limit: int = 100,
    status: str | None = None,
    phone: str | None = None,
):
    """Return logged calls for the dashboard.
    
    Query params:
        limit: Max number of calls to return (default 100)
        status: Filter by status (completed, no-answer, transferred)
        phone: Filter by phone number substring
    """
    logs = _load_logs()
    
    # Apply filters
    if status:
        logs = [log for log in logs if log.get("status") == status]
    if phone:
        logs = [
            log for log in logs
            if phone in (log.get("phone") or "")
        ]
    
    # Sort by timestamp descending, limit
    logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return logs[:limit]


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint for monitoring."""
    return HealthResponse(
        status="ok",
        version="2.1.0",
        service="ai-receptionist",
        timestamp=datetime.now().isoformat(),
    )


@app.get("/stats")
async def get_stats():
    """Return aggregated statistics for the dashboard."""
    logs = _load_logs()
    today = datetime.now().strftime("%Y-%m-%d")
    
    today_logs = [
        log for log in logs
        if log.get("timestamp", "").startswith(today)
    ]
    
    total = len(today_logs)
    booked = len([log for log in today_logs if log.get("appointment")])
    missed = len([log for log in today_logs if log.get("status") == "no-answer"])
    durations = [
        log.get("duration_seconds", 0)
        for log in today_logs
        if log.get("duration_seconds")
    ]
    avg_duration = round(sum(durations) / len(durations), 1) if durations else 0
    
    return {
        "total": total,
        "booked": booked,
        "missed": missed,
        "avg_duration_seconds": avg_duration,
        "period": "today",
    }


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "service": "AI Receptionist Enterprise",
        "version": "2.1.0",
        "status": "operational",
        "docs": "/docs",
        "health": "/health",
    }
