"""Configuration module -- loads and validates environment variables."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)


class Settings:
    """Application settings loaded from environment variables."""

    # Vapi
    VAPI_API_KEY: str = os.getenv("VAPI_API_KEY", "")
    VAPI_WEBHOOK_SECRET: str = os.getenv("VAPI_WEBHOOK_SECRET", "")

    # Twilio
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER", "")

    # Google Calendar
    GOOGLE_CALENDAR_ID: str = os.getenv("GOOGLE_CALENDAR_ID", "primary")
    GOOGLE_CREDENTIALS_FILE: str = os.getenv("GOOGLE_CREDENTIALS_FILE", "google_credentials.json")

    # App
    TIMEZONE: str = os.getenv("TIMEZONE", "America/New_York")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    DASHBOARD_ORIGIN: str = os.getenv("DASHBOARD_ORIGIN", "*")
    EMERGENCY_PHONE_NUMBER: str = os.getenv("EMERGENCY_PHONE_NUMBER", "")

    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    LOG_FILE: Path = BASE_DIR / "calls_log.json"

    @classmethod
    def validate(cls) -> list[str]:
        """Validate required settings. Returns list of missing keys."""
        required = [
            "VAPI_API_KEY",
            "VAPI_WEBHOOK_SECRET",
            "TWILIO_ACCOUNT_SID",
            "TWILIO_AUTH_TOKEN",
            "TWILIO_PHONE_NUMBER",
        ]
        missing = [key for key in required if not getattr(cls, key)]
        return missing


settings = Settings()
