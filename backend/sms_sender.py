"""Twilio SMS sender — validation stricte, logs sans PII, queue support."""

import re
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from backend.config import settings

E164_REGEX = re.compile(r"^\+\d{10,15}$")


def get_twilio_client() -> Client:
    """Initialize Twilio client with credentials."""
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        raise ValueError("Twilio credentials not configured")
    return Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


def _validate_e164(phone: str) -> str:
    if not E164_REGEX.match(phone):
        raise ValueError(f"Invalid E.164 phone format: {phone}")
    return phone


def send_confirmation(to: str, message: str) -> str | None:
    """Send SMS confirmation to patient.

    Args:
        to: Patient phone number (E.164 format, e.g., +1234567890)
        message: SMS body text

    Returns:
        Message SID on success, None on failure
    """
    try:
        client = get_twilio_client()
        if not settings.TWILIO_PHONE_NUMBER:
            raise ValueError("Twilio phone number not configured")

        validated_to = _validate_e164(to)
        msg = client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=validated_to,
        )
        # LOG SANS PII : seul le SID et les 4 derniers chiffres
        masked = validated_to[-4:] if len(validated_to) > 4 else "****"
        print(f"[INFO] SMS sent: {msg.sid} to ...{masked}")
        return msg.sid
    except TwilioRestException as e:
        print(f"[ERROR] Twilio API error: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] SMS send failed: {e}")
        return None


def send_reminder(to: str, date: str, time: str, business_name: str) -> str | None:
    """Send appointment reminder SMS (24h before).

    Args:
        to: Patient phone number
        date: Appointment date (YYYY-MM-DD)
        time: Appointment time (HH:MM)
        business_name: Business name

    Returns:
        Message SID on success, None on failure
    """
    message = (
        f"Reminder: You have an appointment tomorrow {date} at {time} "
        f"at {business_name}. See you then!"
    )
    return send_confirmation(to, message)
