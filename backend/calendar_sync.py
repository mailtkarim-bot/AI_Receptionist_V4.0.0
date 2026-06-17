"""Google Calendar sync -- create events from AI appointments."""

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
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


def create_event(
    phone: str,
    date_str: str,
    time_str: str,
    duration_min: int = 30,
    service: str = "general",
):
    """Create a Google Calendar event for the appointment.
    
    Args:
        phone: Patient phone number
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
        print(f"[ERROR] Calendar service init failed: {e}")
        return None
    
    try:
        start_dt = datetime.fromisoformat(f"{date_str}T{time_str}")
        end_dt = start_dt + timedelta(minutes=duration_min)
    except ValueError:
        print(f"[ERROR] Invalid date/time format: {date_str} {time_str}")
        return None
    
    business_name = os.getenv("BUSINESS_NAME", "AI Receptionist")
    
    event = {
        "summary": f"APT -- {phone} -- {service}",
        "description": (
            f"Patient: {phone}\n"
            f"Service: {service}\n"
            f"Booked by: AI Receptionist\n"
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
                {"method": "sms", "minutes": 60},
                {"method": "popup", "minutes": 30},
            ],
        },
        "colorId": "2",  # Green color in Google Calendar
    }
    
    try:
        calendar_id = settings.GOOGLE_CALENDAR_ID
        created = service_api.events().insert(
            calendarId=calendar_id, body=event
        ).execute()
        print(f"[INFO] Calendar event created: {created.get('htmlLink')}")
        return created.get("id")
    except HttpError as e:
        print(f"[ERROR] Calendar API error: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] Calendar event creation failed: {e}")
        return None
