"""AI Receptionist Webhook — FastAPI ENTERPRISE-GRADE backend v4.0.0."""

import hashlib
import os
import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from fastapi import FastAPI, Request, HTTPException, Depends, status, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy.orm import Session
from sqlalchemy import text
import structlog
import sentry_sdk

from backend.config import settings, MissingConfigError
from backend.database import get_db, engine
from backend.models_db import CallRecord, AppointmentRecord, AuditLog, SMSQueue, RefreshToken
from backend.security import validate_webhook_request
from backend.scheduler import start_scheduler

# Sentry init
if settings.SENTRY_DSN:
    sentry_sdk.init(dsn=settings.SENTRY_DSN, traces_sample_rate=0.2)

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)
logger = structlog.get_logger()

# Rate limiter — NOTE: slowapi in-memory is insufficient for multi-worker.
# For production multi-instance, migrate to RedisBackend.
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="AI Receptionist Enterprise",
    version="4.0.0",
    description="Enterprise-grade AI voice agent with PostgreSQL, JWT auth, audit logging, GDPR, quiet hours, and emergency transfer",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security headers middleware
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'"
    return response

# CORS — STRICT
origins = [settings.DASHBOARD_ORIGIN] if settings.DASHBOARD_ORIGIN else []
if settings.ENVIRONMENT == "development" and not origins:
    origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Auth
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Hash computed ONCE at startup from env var
ADMIN_PASSWORD_HASH = pwd_context.hash(os.environ["ADMIN_PASSWORD"])


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str):
    if username == "admin" and verify_password(password, ADMIN_PASSWORD_HASH):
        return {"username": username}
    return None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


def create_refresh_token(db: Session, user_id: str) -> tuple[str, datetime]:
    """Generate a rotating refresh token stored in DB."""
    token = secrets.token_urlsafe(32)
    expires = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    db_token = RefreshToken(token=token, user_id=user_id, expires_at=expires)
    db.add(db_token)
    db.commit()
    return token, expires


def revoke_refresh_token(db: Session, token: str) -> None:
    """Revoke a refresh token (logout)."""
    db_token = db.query(RefreshToken).filter(RefreshToken.token == token).first()
    if db_token:
        db_token.revoked = True
        db.commit()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    ai_token: Optional[str] = Cookie(None)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    auth_token = token if token else ai_token
    if not auth_token:
        raise credentials_exception
    try:
        payload = jwt.decode(auth_token, settings.SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return {"username": username}


def _hash_phone(phone: Optional[str]) -> str:
    if not phone:
        return hashlib.sha256("unknown".encode()).hexdigest()
    return hashlib.sha256(phone.encode()).hexdigest()


def _audit_log(db: Session, action: str, source_ip: Optional[str], success: bool, error: Optional[str] = None, payload_summary: Optional[str] = None):
    log = AuditLog(
        action=action,
        source_ip=source_ip,
        success=success,
        error_message=error,
        payload_summary=payload_summary,
    )
    db.add(log)
    db.commit()


def _is_quiet_hours() -> bool:
    """Check if current time is within quiet hours (no SMS)."""
    now = datetime.now(ZoneInfo(settings.TIMEZONE))
    hour = now.hour
    return hour >= settings.QUIET_HOURS_START or hour < settings.QUIET_HOURS_END


@app.on_event("startup")
async def startup_event():
    start_scheduler()
    logger.info("Application started", version="4.0.0", env=settings.ENVIRONMENT)


@app.post("/vapi-webhook")
@limiter.limit("30/minute")
async def vapi_webhook(request: Request, db: Session = Depends(get_db)):
    client_ip = request.headers.get("X-Forwarded-For", request.client.host if request.client else None)

    try:
        data = await validate_webhook_request(request)
    except HTTPException as e:
        _audit_log(db, "webhook_validation_failed", client_ip, False, str(e.detail))
        raise

    call = data.get("call", {})
    analysis = data.get("analysis", {})
    call_id = call.get("id")

    if not call_id:
        _audit_log(db, "webhook_missing_call_id", client_ip, False, "Missing call.id")
        raise HTTPException(status_code=422, detail="Missing call.id")

    # IDEMPOTENCE: check if call_id already exists
    existing = db.query(CallRecord).filter(CallRecord.call_id == call_id).first()
    if existing:
        _audit_log(db, "webhook_duplicate_ignored", client_ip, True, payload_summary=f"call_id={call_id}")
        return JSONResponse(content={"success": True, "call_id": call_id, "duplicate": True}, status_code=200)

    phone = call.get("customer", {}).get("number")
    phone_hash = _hash_phone(phone)

    call_record = CallRecord(
        call_id=call_id,
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

    # EMERGENCY HANDLING
    if analysis.get("is_emergency", False):
        try:
            _handle_emergency(phone, call_id, client_ip)
        except Exception as e:
            logger.error("Emergency handling failed", error=str(e), call_id=call_id)
            sentry_sdk.capture_exception(e)

    appt = analysis.get("booked_appointment")
    if appt:
        try:
            _process_appointment(db, phone, phone_hash, appt, call_record.id, client_ip)
        except Exception as e:
            logger.error("Appointment processing failed", error=str(e), call_id=call_id)
            sentry_sdk.capture_exception(e)

    _audit_log(db, "webhook_processed", client_ip, True, payload_summary=f"call_id={call_id}")
    logger.info("Webhook processed", call_id=call_id, phone_hash_prefix=phone_hash[:16])

    return JSONResponse(content={"success": True, "call_id": call_id}, status_code=200)


def _handle_emergency(phone: Optional[str], call_id: str, client_ip: Optional[str]) -> None:
    """Transfer emergency call to doctor via Twilio Voice + SMS alert."""
    if not settings.EMERGENCY_PHONE_NUMBER or not phone:
        logger.warning("Emergency detected but no phone or emergency number configured", call_id=call_id)
        return

    try:
        from twilio.rest import Client
        from twilio.twiml.voice_response import VoiceResponse

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        # 1. Voice transfer: connect patient to emergency doctor
        twiml = VoiceResponse()
        twiml.dial(settings.EMERGENCY_PHONE_NUMBER)
        client.calls.create(
            to=phone,
            from_=settings.TWILIO_PHONE_NUMBER,
            twiml=str(twiml),
        )
        logger.info("Emergency voice transfer initiated", call_id=call_id, to=settings.EMERGENCY_PHONE_NUMBER)

        # 2. SMS backup alert to doctor
        from backend.sms_sender import send_confirmation
        masked_patient = phone[-4:] if len(phone) > 4 else "****"
        alert_msg = (
            f"URGENCY: Emergency call from patient ...{masked_patient}. "
            f"Call ID: {call_id}. Patient is being transferred to you now."
        )
        send_confirmation(to=settings.EMERGENCY_PHONE_NUMBER, message=alert_msg)

    except Exception as e:
        logger.error("Emergency transfer failed", error=str(e), call_id=call_id)
        raise


def _process_appointment(db: Session, phone_plain: Optional[str], phone_hash: str, appt: dict, call_record_id: int, client_ip: Optional[str]) -> None:
    """Transaction atomique: appointment + calendrier + SMS."""
    from backend.models import AppointmentData
    try:
        validated = AppointmentData(**appt)
    except Exception as e:
        _audit_log(db, "appointment_validation_failed", client_ip, False, str(e))
        return

    appointment = AppointmentRecord(
        call_record_id=call_record_id,
        patient_phone_hash=phone_hash,
        appointment_date=validated.date,
        appointment_time=validated.time,
        duration_minutes=validated.duration_minutes,
        service=validated.service,
    )
    db.add(appointment)

    # Calendar conflict check + creation
    calendar_event_id = None
    try:
        from backend.calendar_sync import check_conflict, create_event
        has_conflict = check_conflict(
            date_str=validated.date,
            time_str=validated.time,
            duration_min=validated.duration_minutes,
        )
        if has_conflict:
            logger.warning("Calendar conflict detected", call_record_id=call_record_id, date=validated.date, time=validated.time)
            _audit_log(db, "calendar_conflict_detected", client_ip, True, payload_summary=f"date={validated.date} time={validated.time}")
            appointment.calendar_event_id = "CONFLICT"
        else:
            calendar_event_id = create_event(
                phone_hash=phone_hash,
                date_str=validated.date,
                time_str=validated.time,
                duration_min=validated.duration_minutes,
                service=validated.service,
            )
            if calendar_event_id:
                appointment.calendar_event_id = calendar_event_id
    except Exception as e:
        logger.error("Calendar sync failed", error=str(e))
        sentry_sdk.capture_exception(e)

    # SMS handling with quiet hours
    if phone_plain:
        try:
            from backend.sms_sender import send_confirmation
            business_name = os.getenv("BUSINESS_NAME", "Our Clinic")
            msg = (
                f"Your appointment is confirmed for {validated.date} at {validated.time}. "
                f"{business_name}. To reschedule, call us."
            )

            if _is_quiet_hours():
                # Queue SMS for morning delivery
                queued = SMSQueue(phone=phone_plain, message=msg)
                db.add(queued)
                _audit_log(db, "sms_queued_quiet_hours", client_ip, True, payload_summary=f"phone_hash={phone_hash[:16]}")
                logger.info("SMS queued for quiet hours", call_record_id=call_record_id)
            else:
                sid = send_confirmation(to=phone_plain, message=msg)
                if sid:
                    appointment.sms_sent = True
        except Exception as e:
            logger.error("SMS handling failed", error=str(e))
            sentry_sdk.capture_exception(e)

    db.commit()


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
        phone_hash = _hash_phone(phone)
        query = query.filter(CallRecord.phone_hash == phone_hash)

    calls = query.order_by(CallRecord.created_at.desc()).limit(min(limit, 500)).all()
    return [
        {
            "id": c.id,
            "call_id": c.call_id,
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
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

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
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Dashboard login endpoint — sets httpOnly cookies for access + refresh tokens."""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user["username"]})
    refresh_token, refresh_expires = create_refresh_token(db, user["username"])

    response.set_cookie(
        key="ai_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        key="ai_refresh",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/refresh")
async def refresh_token(response: Response, request: Request, db: Session = Depends(get_db)):
    """Rotate refresh token and issue new access token."""
    refresh_cookie = request.cookies.get("ai_refresh")
    if not refresh_cookie:
        raise HTTPException(status_code=401, detail="No refresh token provided")

    db_token = db.query(RefreshToken).filter(
        RefreshToken.token == refresh_cookie,
        RefreshToken.revoked == False,
        RefreshToken.expires_at > datetime.now(timezone.utc)
    ).first()

    if not db_token:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    # Rotate: revoke old, create new
    db_token.revoked = True
    db.commit()

    new_access = create_access_token(data={"sub": db_token.user_id})
    new_refresh, new_expires = create_refresh_token(db, db_token.user_id)

    response.set_cookie(
        key="ai_token",
        value=new_access,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        key="ai_refresh",
        value=new_refresh,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )
    return {"access_token": new_access, "token_type": "bearer"}


@app.post("/logout")
async def logout(response: Response, request: Request, db: Session = Depends(get_db)):
    """Clear authentication cookies and revoke refresh token."""
    refresh_cookie = request.cookies.get("ai_refresh")
    if refresh_cookie:
        revoke_refresh_token(db, refresh_cookie)
    response.delete_cookie(key="ai_token")
    response.delete_cookie(key="ai_refresh")
    return {"message": "Logged out"}


@app.delete("/patients/{phone_hash}")
@limiter.limit("10/minute")
async def erase_patient(
    request: Request,
    phone_hash: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """GDPR Right to Erasure — anonymize all records for a given phone hash.

    Instead of deleting (which destroys business metrics), we anonymize:
    - Replace phone_hash with ANONYMIZED placeholder
    - Clear transcripts and appointment details
    - Preserve date/time/duration for statistical analysis
    """
    client_ip = request.headers.get("X-Forwarded-For", request.client.host if request.client else None)

    anonymized_hash = hashlib.sha256("ANONYMIZED".encode()).hexdigest()

    # Update call records
    call_records = db.query(CallRecord).filter(CallRecord.phone_hash == phone_hash).all()
    for record in call_records:
        record.phone_hash = anonymized_hash
        record.transcript = None
        record.appointment = None

    # Update appointments
    appointments = db.query(AppointmentRecord).filter(AppointmentRecord.patient_phone_hash == phone_hash).all()
    for appt in appointments:
        appt.patient_phone_hash = anonymized_hash

    db.commit()
    count_calls = len(call_records)
    count_appts = len(appointments)

    _audit_log(
        db, "gdpr_erase", client_ip, True,
        payload_summary=f"phone_hash={phone_hash[:16]}... calls={count_calls} appts={count_appts}"
    )
    logger.info("GDPR erase executed", phone_hash_prefix=phone_hash[:16], calls=count_calls, appointments=count_appts)

    return {
        "success": True,
        "message": f"Anonymized {count_calls} call records and {count_appts} appointments",
        "phone_hash_prefix": phone_hash[:16],
    }


@app.get("/health")
async def health(db: Session = Depends(get_db)):
    """Health check with REAL database connectivity verification."""
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"disconnected: {e}"
        raise HTTPException(status_code=503, detail={"status": "error", "database": db_status})

    return {
        "status": "ok" if db_status == "connected" else "error",
        "version": "4.0.0",
        "service": "ai-receptionist",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": db_status,
    }


@app.get("/")
async def root():
    return {
        "service": "AI Receptionist Enterprise",
        "version": "4.0.0",
        "status": "operational",
        "health": "/health",
    }
