"""SQLAlchemy ORM models — PII minimisé, timezone-aware."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Text, Index, UniqueConstraint
from backend.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class CallRecord(Base):
    """Persistent call log stored in PostgreSQL."""

    __tablename__ = "call_records"

    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(String(255), unique=True, nullable=False, index=True)
    # PII SUPPRIMÉ : seul le hash est conservé. Le numéro en clair est supprimé.
    phone_hash = Column(String(64), nullable=False, index=True)
    status = Column(String(50), default="unknown")
    transcript = Column(Text, nullable=True)
    appointment = Column(JSON, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    is_emergency = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    __table_args__ = (
        Index("ix_call_records_created_at", "created_at"),
        Index("ix_call_records_status", "status"),
        UniqueConstraint("call_id", name="uq_call_records_call_id"),
    )


class AppointmentRecord(Base):
    """Extracted appointments for quick querying."""

    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    call_record_id = Column(Integer, nullable=False, index=True)
    # PII SUPPRIMÉ : patient_phone en clair supprimé. Utiliser phone_hash de CallRecord.
    patient_phone_hash = Column(String(64), nullable=False, index=True)
    appointment_date = Column(String(10), nullable=False)
    appointment_time = Column(String(5), nullable=False)
    duration_minutes = Column(Integer, default=30)
    service = Column(String(100), default="general")
    calendar_event_id = Column(String(255), nullable=True)
    sms_sent = Column(Boolean, default=False)
    reminder_sent = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)


class AuditLog(Base):
    """Security audit trail."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(50), nullable=False)
    source_ip = Column(String(45), nullable=True)
    payload_summary = Column(String(500), nullable=True)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)


class SMSQueue(Base):
    """Queued SMS messages for quiet hours delivery.

    NOTE: phone is stored plaintext temporarily for SMS delivery.
    Cleared after send via purge job (max 30 days retention).
    """

    __tablename__ = "sms_queue"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    sent = Column(Boolean, default=False)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)


class RefreshToken(Base):
    """Rotating refresh tokens for JWT cookie-based auth."""

    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(String(50), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)
