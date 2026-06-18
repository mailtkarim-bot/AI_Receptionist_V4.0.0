"""Configuration module — ZERO fallback for secrets."""

import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)


class MissingConfigError(Exception):
    pass


class Settings:
    VAPI_API_KEY: str = os.getenv("VAPI_API_KEY", "")
    VAPI_WEBHOOK_SECRET: str = os.getenv("VAPI_WEBHOOK_SECRET", "")
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER", "")
    GOOGLE_CALENDAR_ID: str = os.getenv("GOOGLE_CALENDAR_ID", "primary")
    GOOGLE_CREDENTIALS_FILE: str = os.getenv("GOOGLE_CREDENTIALS_FILE", "google_credentials.json")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    TIMEZONE: str = os.getenv("TIMEZONE", "Asia/Dubai")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    DASHBOARD_ORIGIN: str = os.getenv("DASHBOARD_ORIGIN", "")
    EMERGENCY_PHONE_NUMBER: str = os.getenv("EMERGENCY_PHONE_NUMBER", "")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")
    BASE_DIR: Path = Path(__file__).parent.parent

    # Quiet hours configuration
    QUIET_HOURS_START: int = int(os.getenv("QUIET_HOURS_START", "21"))
    QUIET_HOURS_END: int = int(os.getenv("QUIET_HOURS_END", "8"))

    # Data retention (days)
    RETENTION_CALLS_DAYS: int = int(os.getenv("RETENTION_CALLS_DAYS", "730"))
    RETENTION_AUDIT_DAYS: int = int(os.getenv("RETENTION_AUDIT_DAYS", "365"))
    RETENTION_SMS_QUEUE_DAYS: int = int(os.getenv("RETENTION_SMS_QUEUE_DAYS", "30"))

    def __init__(self):
        required = [
            "VAPI_API_KEY", "VAPI_WEBHOOK_SECRET", "TWILIO_ACCOUNT_SID",
            "TWILIO_AUTH_TOKEN", "TWILIO_PHONE_NUMBER", "DATABASE_URL",
            "SECRET_KEY", "ADMIN_PASSWORD",
        ]
        missing = [k for k in required if not getattr(self, k)]
        if missing:
            raise MissingConfigError(f"MISSING CRITICAL ENV VARS: {', '.join(missing)}")
        if len(self.SECRET_KEY) < 32:
            raise MissingConfigError("SECRET_KEY must be >= 32 characters")
        if self.ACCESS_TOKEN_EXPIRE_MINUTES < 5:
            raise MissingConfigError("ACCESS_TOKEN_EXPIRE_MINUTES must be >= 5")


settings = Settings()
