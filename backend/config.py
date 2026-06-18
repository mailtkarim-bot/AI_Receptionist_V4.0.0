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

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/ai_receptionist"
    )

    # Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production-32-chars-long!!")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    # App
    TIMEZONE: str = os.getenv("TIMEZONE", "Asia/Dubai")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    DASHBOARD_ORIGIN: str = os.getenv("DASHBOARD_ORIGIN", "*")
    EMERGENCY_PHONE_NUMBER: str = os.getenv("EMERGENCY_PHONE_NUMBER", "")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent

    @classmethod
    def validate(cls) -> list[str]:
        """Validate required settings. Returns list of missing keys."""
        required = [
            "VAPI_API_KEY",
            "VAPI_WEBHOOK_SECRET",
            "TWILIO_ACCOUNT_SID",
            "TWILIO_AUTH_TOKEN",
            "TWILIO_PHONE_NUMBER",
            "SECRET_KEY",
        ]
        missing = [key for key in required if not getattr(cls, key)]
        return missing


settings = Settings()