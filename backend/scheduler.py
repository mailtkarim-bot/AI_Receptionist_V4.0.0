"""Background scheduler — purge, SMS queue, refresh token cleanup."""

import logging
from datetime import datetime, timezone, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from backend.database import SessionLocal
from backend.models_db import CallRecord, AppointmentRecord, AuditLog, SMSQueue, RefreshToken
from backend.sms_sender import send_confirmation
from backend.config import settings

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()


def purge_old_records():
    """Delete old records per retention policy."""
    db = SessionLocal()
    try:
        cutoff_calls = datetime.now(timezone.utc) - timedelta(days=settings.RETENTION_CALLS_DAYS)
        cutoff_audit = datetime.now(timezone.utc) - timedelta(days=settings.RETENTION_AUDIT_DAYS)
        cutoff_queue = datetime.now(timezone.utc) - timedelta(days=settings.RETENTION_SMS_QUEUE_DAYS)
        cutoff_refresh = datetime.now(timezone.utc) - timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        deleted_calls = db.query(CallRecord).filter(CallRecord.created_at < cutoff_calls).delete(synchronize_session=False)
        deleted_appts = db.query(AppointmentRecord).filter(AppointmentRecord.created_at < cutoff_calls).delete(synchronize_session=False)
        deleted_audit = db.query(AuditLog).filter(AuditLog.created_at < cutoff_audit).delete(synchronize_session=False)
        deleted_queue = db.query(SMSQueue).filter(SMSQueue.created_at < cutoff_queue).delete(synchronize_session=False)
        deleted_refresh = db.query(RefreshToken).filter(
            (RefreshToken.expires_at < cutoff_refresh) | (RefreshToken.revoked == True)
        ).delete(synchronize_session=False)

        db.commit()
        logger.info(
            f"Purge completed: calls={deleted_calls}, appointments={deleted_appts}, "
            f"audit={deleted_audit}, sms_queue={deleted_queue}, refresh_tokens={deleted_refresh}"
        )
    except Exception as e:
        logger.error(f"Purge failed: {e}")
        db.rollback()
    finally:
        db.close()


def process_sms_queue():
    """Send queued SMS messages (typically after quiet hours)."""
    db = SessionLocal()
    try:
        pending = db.query(SMSQueue).filter(SMSQueue.sent == False).all()
        sent_count = 0
        for item in pending:
            try:
                sid = send_confirmation(to=item.phone, message=item.message)
                if sid:
                    item.sent = True
                    item.sent_at = datetime.now(timezone.utc)
                    sent_count += 1
            except Exception as e:
                logger.error(f"SMS queue send failed for id={item.id}: {e}")
        db.commit()
        logger.info(f"Processed {sent_count}/{len(pending)} queued SMS")
    except Exception as e:
        logger.error(f"SMS queue processing failed: {e}")
        db.rollback()
    finally:
        db.close()


def start_scheduler():
    """Start background jobs."""
    # Daily purge at 03:00
    scheduler.add_job(
        purge_old_records,
        CronTrigger(hour=3, minute=0),
        id="purge",
        replace_existing=True,
    )
    # Morning SMS queue at 08:00
    scheduler.add_job(
        process_sms_queue,
        CronTrigger(hour=8, minute=0),
        id="sms_morning",
        replace_existing=True,
    )
    # Additional SMS processing every hour during business hours
    scheduler.add_job(
        process_sms_queue,
        CronTrigger(hour="9-20", minute=0),
        id="sms_day",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started with purge, SMS queue, and refresh token cleanup")
