"""Pydantic data models for request/response validation."""

from pydantic import BaseModel, Field
from typing import Optional


class AppointmentData(BaseModel):
    """Extracted appointment information from AI call."""
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="YYYY-MM-DD")
    time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="HH:MM 24h format")
    duration_minutes: int = Field(default=30, ge=15, le=240)
    service: str = Field(default="general", description="Type of service")
    phone: Optional[str] = Field(default=None, description="Patient phone number")


class CallLog(BaseModel):
    """Single call log entry."""
    timestamp: str
    call_id: Optional[str] = None
    phone: Optional[str] = None
    status: str = "unknown"
    transcript: Optional[str] = None
    appointment: Optional[dict] = None
    duration_seconds: Optional[int] = None
    is_emergency: bool = False


class VapiWebhookPayload(BaseModel):
    """Incoming Vapi webhook payload structure."""
    call: Optional[dict] = Field(default=None)
    analysis: Optional[dict] = Field(default=None)
    status: Optional[str] = Field(default=None)
    transcript: Optional[str] = Field(default=None)
    message: Optional[dict] = Field(default=None)


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    service: str
    timestamp: str
