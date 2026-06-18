"""Tests for background scheduler jobs."""

import pytest
from datetime import datetime, timezone, timedelta
from backend.database import Base, engine, SessionLocal
from backend.models_db import CallRecord, AppointmentRecord, AuditLog, SMSQueue, RefreshToken
from backend.scheduler import purge_old_records, process_sms_queue


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


class TestPurgeOldRecords:
    def test_purge_deletes_old_calls(self):
        db = SessionLocal()
        old_call = CallRecord(
            call_id="old-call-001",
            phone_hash="a" * 64,
            status="completed",
            created_at=datetime.now(timezone.utc) - timedelta(days=800),
        )
        db.add(old_call)
        db.commit()
        db.close()

        purge_old_records()

        db = SessionLocal()
        assert db.query(CallRecord).filter(CallRecord.call_id == "old-call-001").first() is None
        db.close()

    def test_purge_keeps_recent_calls(self):
        db = SessionLocal()
        recent_call = CallRecord(
            call_id="recent-call-001",
            phone_hash="b" * 64,
            status="completed",
            created_at=datetime.now(timezone.utc) - timedelta(days=30),
        )
        db.add(recent_call)
        db.commit()
        db.close()

        purge_old_records()

        db = SessionLocal()
        assert db.query(CallRecord).filter(CallRecord.call_id == "recent-call-001").first() is not None
        db.close()

    def test_purge_deletes_revoked_refresh_tokens(self):
        db = SessionLocal()
        old_token = RefreshToken(
            token="revoked-token",
            user_id="admin",
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
            revoked=True,
            created_at=datetime.now(timezone.utc) - timedelta(days=10),
        )
        db.add(old_token)
        db.commit()
        db.close()

        purge_old_records()

        db = SessionLocal()
        assert db.query(RefreshToken).filter(RefreshToken.token == "revoked-token").first() is None
        db.close()


class TestProcessSMSQueue:
    @patch("backend.scheduler.send_confirmation")
    def test_process_sms_queue_sends_pending(self, mock_send):
        mock_send.return_value = "SM12345"

        db = SessionLocal()
        queued = SMSQueue(phone="+1234567890", message="Test message", sent=False)
        db.add(queued)
        db.commit()
        db.close()

        process_sms_queue()

        db = SessionLocal()
        item = db.query(SMSQueue).filter(SMSQueue.phone == "+1234567890").first()
        assert item.sent is True
        assert item.sent_at is not None
        db.close()

    def test_process_sms_queue_skips_already_sent(self):
        db = SessionLocal()
        queued = SMSQueue(phone="+1234567890", message="Test", sent=True, sent_at=datetime.now(timezone.utc))
        db.add(queued)
        db.commit()
        db.close()

        process_sms_queue()

        # Should not raise and should not attempt to send again
        db = SessionLocal()
        item = db.query(SMSQueue).filter(SMSQueue.phone == "+1234567890").first()
        assert item.sent is True
        db.close()
