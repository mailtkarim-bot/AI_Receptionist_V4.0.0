"""SQLAlchemy ORM models for persistent storage."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Text, Index
from backend.database import Base


class CallRecord(Base):
    """Persistent call log stored in PostgreSQL."""

    __tablename__ = "call_records"

    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(String(255), unique=True, nullable=True)
    phone = Column(String(50), nullable=True, index=True)
    phone_hash = Column(String(64), nullable=True)
    status = Column(String(50), default="unknown")
    transcript = Column(Text, nullable=True)
    appointment = Column(JSON, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    is_emergency = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_call_records_created_at", "created_at"),
        Index("ix_call_records_status", "status"),
    )


class AppointmentRecord(Base):
    """Extracted appointments for quick querying."""

    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    call_record_id = Column(Integer, nullable=True)
    patient_phone = Column(String(50), nullable=True)
    appointment_date = Column(String(10), nullable=True)
    appointment_time = Column(String(5), nullable=True)
    duration_minutes = Column(Integer, default=30)
    service = Column(String(100), default="general")
    calendar_event_id = Column(String(255), nullable=True)
    sms_sent = Column(Boolean, default=False)
    reminder_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    """Security audit trail."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(50), nullable=False)
    source_ip = Column(String(45), nullable=True)
    payload_summary = Column(String(500), nullable=True)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)