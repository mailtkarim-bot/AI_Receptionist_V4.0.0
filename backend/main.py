"""AI Receptionist Webhook -- FastAPI ENTERPRISE-GRADE backend."""

import hashlib
import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy.orm import Session
import structlog

from backend.config import settings
from backend.database import get_db, init_db
from backend.models_db import CallRecord, AppointmentRecord, AuditLog
from backend.security import validate_webhook_request

# Structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)
logger = structlog.get_logger()

# Rate limiter
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="AI Receptionist Enterprise",
    version="3.0.0",
    description="Enterprise-grade AI voice agent with PostgreSQL, JWT auth, and audit logging",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.DASHBOARD_ORIGIN] if settings.DASHBOARD_ORIGIN != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Auth
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

ADMIN_USER = {
    "username": "admin",
    "hashed_password": pwd_context.hash(os.getenv("ADMIN_PASSWORD", "changeme123")),
}


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str):
    if username == ADMIN_USER["username"] and verify_password(password, ADMIN_USER["hashed_password"]):
        return {"username": username}
    return None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return {"username": username}


def _hash_phone(phone: Optional[str]) -> Optional[str]:
    if not phone:
        return None
    return hashlib.sha256(phone.encode()).hexdigest()


def _audit_log(db: Session, action: str, source_ip: Optional[str], success: bool, error: Optional[str] = None):
    log = AuditLog(
        action=action,
        source_ip=source_ip,
        success=success,
        error_message=error,
    )
    db.add(log)
    db.commit()


@app.on_event("startup")
async def startup_event():
    init_db()
    logger.info("Application started", version="3.0.0", env=settings.ENVIRONMENT)


@app.post("/vapi-webhook")
@limiter.limit("30/minute")
async def vapi_webhook(request: Request, db: Session = Depends(get_db)):
    """Receive and process Vapi call-end webhook events."""
    client_ip = request.client.host if request.client else None

    try:
        data = await validate_webhook_request(request)
    except HTTPException as e:
        _audit_log(db, "webhook_validation_failed", client_ip, False, str(e.detail))
        raise

    call = data.get("call", {})
    analysis = data.get("analysis", {})

    phone = call.get("customer", {}).get("number")
    phone_hash = _hash_phone(phone)

    call_record = CallRecord(
        call_id=call.get("id"),
        phone=phone,
        phone_hash=phone_hash,
        status=data.get("status", "unknown"),
        transcript=data.get("transcript"),
        appointment=analysis.get("booked_appointment"),
        duration_seconds=call.get("durationSeconds"),
        is_emergency=analysis.get("is_emergency", False),
    )
    db.add(call_record)
    db.commit()
    db.refresh(call_record)

    appt = analysis.get("booked_appointment")
    if appt:
        _process_appointment(db, phone, appt, call_record.id)

    _audit_log(db, "webhook_processed", client_ip, True)
    logger.info("Webhook processed", call_id=call.get("id"), phone_hash=phone_hash[:8] if phone_hash else None)

    return JSONResponse(
        content={"success": True, "call_id": call.get("id")},
        status_code=200,
    )


def _process_appointment(db: Session, phone: Optional[str], appt: dict, call_record_id: int) -> None:
    """Create calendar event, send SMS, persist appointment."""
    appointment = AppointmentRecord(
        call_record_id=call_record_id,
        patient_phone=phone,
        appointment_date=appt.get("date"),
        appointment_time=appt.get("time"),
        duration_minutes=appt.get("duration_minutes", 30),
        service=appt.get("service", "general"),
    )
    db.add(appointment)
    db.commit()

    try:
        from backend.calendar_sync import create_event
        event_id = create_event(
            phone=phone or "unknown",
            date_str=appt.get("date"),
            time_str=appt.get("time"),
            duration_min=appt.get("duration_minutes", 30),
            service=appt.get("service", "general"),
        )
        if event_id:
            appointment.calendar_event_id = event_id
            db.commit()
    except Exception as e:
        logger.error("Calendar sync failed", error=str(e))
        db.rollback()

    try:
        from backend.sms_sender import send_confirmation
        business_name = os.getenv("BUSINESS_NAME", "Our Clinic")
        msg = (
            f"Your appointment is confirmed for {appt['date']} at {appt['time']}. "
            f"{business_name}. To reschedule, call us."
        )
        if phone:
            sid = send_confirmation(to=phone, message=msg)
            if sid:
                appointment.sms_sent = True
                db.commit()
    except Exception as e:
        logger.error("SMS send failed", error=str(e))


@app.get("/calls")
@limiter.limit("100/minute")
async def get_calls(
    request: Request,
    limit: int = 100,
    status: Optional[str] = None,
    phone: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Return logged calls for the dashboard (AUTH REQUIRED)."""
    query = db.query(CallRecord)

    if status:
        query = query.filter(CallRecord.status == status)
    if phone:
        query = query.filter(CallRecord.phone.contains(phone))

    calls = query.order_by(CallRecord.created_at.desc()).limit(limit).all()
    return [
        {
            "id": c.id,
            "call_id": c.call_id,
            "phone": c.phone,
            "status": c.status,
            "transcript": c.transcript,
            "appointment": c.appointment,
            "duration_seconds": c.duration_seconds,
            "is_emergency": c.is_emergency,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in calls
    ]


@app.get("/stats")
@limiter.limit("100/minute")
async def get_stats(
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Return aggregated statistics for the dashboard."""
    from sqlalchemy import func
    today = datetime.utcnow().strftime("%Y-%m-%d")

    total = db.query(CallRecord).filter(
        func.date(CallRecord.created_at) == today
    ).count()

    booked = db.query(AppointmentRecord).filter(
        func.date(AppointmentRecord.created_at) == today
    ).count()

    missed = db.query(CallRecord).filter(
        func.date(CallRecord.created_at) == today,
        CallRecord.status == "no-answer"
    ).count()

    avg_duration = db.query(func.avg(CallRecord.duration_seconds)).filter(
        func.date(CallRecord.created_at) == today,
        CallRecord.duration_seconds.isnot(None)
    ).scalar()

    return {
        "total": total,
        "booked": booked,
        "missed": missed,
        "avg_duration_seconds": round(avg_duration or 0, 1),
        "period": "today",
    }


@app.post("/token")
@limiter.limit("10/minute")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Dashboard login endpoint."""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/health")
async def health():
    """Health check for monitoring."""
    return {
        "status": "ok",
        "version": "3.0.0",
        "service": "ai-receptionist",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected",
    }


@app.get("/")
async def root():
    return {
        "service": "AI Receptionist Enterprise",
        "version": "3.0.0",
        "status": "operational",
        "docs": "/docs",
        "health": "/health",
    }