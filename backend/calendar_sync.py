"""Google Calendar sync — PII minimisée, conflict detection."""

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timezone, timedelta
import os

from backend.config import settings

SCOPES = ["https://www.googleapis.com/auth/calendar"]


def get_calendar_service():
    """Initialize Google Calendar API service."""
    creds_path = settings.BASE_DIR / settings.GOOGLE_CREDENTIALS_FILE
    if not creds_path.exists():
        raise FileNotFoundError(f"Google credentials not found: {creds_path}")

    creds = service_account.Credentials.from_service_account_file(
        str(creds_path), scopes=SCOPES
    )
    return build("calendar", "v3", credentials=creds)


def check_conflict(date_str: str, time_str: str, duration_min: int = 30) -> bool:
    """Check if the requested time slot conflicts with an existing event.

    Returns True if a conflict exists, False otherwise.
    """
    try:
        service_api = get_calendar_service()
    except Exception as e:
        raise RuntimeError(f"Calendar service init failed: {e}")

    try:
        start_dt = datetime.strptime(f"{date_str}T{time_str}", "%Y-%m-%dT%H:%M").replace(tzinfo=timezone.utc)
        end_dt = start_dt + timedelta(minutes=duration_min)
    except ValueError:
        raise ValueError(f"Invalid date/time format: {date_str} {time_str}")

    try:
        events_result = service_api.events().list(
            calendarId=settings.GOOGLE_CALENDAR_ID,
            timeMin=start_dt.isoformat(),
            timeMax=end_dt.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        ).execute()
        events = events_result.get("items", [])
        return len(events) > 0
    except HttpError as e:
        raise RuntimeError(f"Calendar API conflict check failed: {e}")


def create_event(
    phone_hash: str,
    date_str: str,
    time_str: str,
    duration_min: int = 30,
    service: str = "general",
):
    """Create a Google Calendar event for the appointment.

    Args:
        phone_hash: SHA-256 hash of patient phone (never plaintext)
        date_str: Appointment date (YYYY-MM-DD)
        time_str: Appointment time (HH:MM)
        duration_min: Duration in minutes (default 30)
        service: Type of service

    Returns:
        Created event ID or None on failure
    """
    try:
        service_api = get_calendar_service()
    except Exception as e:
        raise RuntimeError(f"Calendar service init failed: {e}")

    try:
        start_dt = datetime.strptime(f"{date_str}T{time_str}", "%Y-%m-%dT%H:%M").replace(tzinfo=timezone.utc)
        end_dt = start_dt + timedelta(minutes=duration_min)
    except ValueError:
        raise ValueError(f"Invalid date/time format: {date_str} {time_str}")

    business_name = os.getenv("BUSINESS_NAME", "AI Receptionist")

    # PII MASQUÉE : le phone_hash remplace le numéro en clair
    event = {
        "summary": f"APT -- {phone_hash[:16]}... -- {service}",
        "description": (
            f"Patient ID: {phone_hash[:16]}...
"
            f"Service: {service}
"
            f"Booked by: AI Receptionist
"
            f"Date: {date_str} {time_str}"
        ),
        "start": {
            "dateTime": start_dt.isoformat(),
            "timeZone": settings.TIMEZONE,
        },
        "end": {
            "dateTime": end_dt.isoformat(),
            "timeZone": settings.TIMEZONE,
        },
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "popup", "minutes": 30},
            ],
        },
        "colorId": "2",  # Green color in Google Calendar
    }

    try:
        calendar_id = settings.GOOGLE_CALENDAR_ID
        created = service_api.events().insert(calendarId=calendar_id, body=event).execute()
        return created.get("id")
    except HttpError as e:
        raise RuntimeError(f"Calendar API error: {e}")
