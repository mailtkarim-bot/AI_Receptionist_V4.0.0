"""Tests for Twilio SMS sender."""

import pytest
from unittest.mock import patch, MagicMock
from backend.sms_sender import send_confirmation, send_reminder, get_twilio_client, _validate_e164


class TestSMSSender:
    @patch("backend.sms_sender.get_twilio_client")
    def test_send_confirmation_success(self, mock_get_client):
        mock_client = MagicMock()
        mock_messages = MagicMock()
        mock_create = MagicMock()
        mock_create.return_value = MagicMock(sid="SM1234567890")
        mock_messages.create = mock_create
        mock_client.messages = mock_messages
        mock_get_client.return_value = mock_client

        result = send_confirmation(
            to="+1234567890",
            message="Your appointment is confirmed for 2026-06-20 at 14:00.",
        )

        assert result == "SM1234567890"
        mock_create.assert_called_once()
        call_kwargs = mock_create.call_args[1]
        assert call_kwargs["to"] == "+1234567890"
        assert "confirmed" in call_kwargs["body"]

    @patch("backend.sms_sender.get_twilio_client")
    def test_send_confirmation_failure(self, mock_get_client):
        from twilio.base.exceptions import TwilioRestException
        mock_get_client.side_effect = TwilioRestException(
            status=400,
            uri="/Messages",
            msg="Invalid phone number",
        )

        result = send_confirmation(to="+1234567890", message="Test")
        assert result is None

    @patch("backend.sms_sender.send_confirmation")
    def test_send_reminder(self, mock_send):
        mock_send.return_value = "SM9998887777"

        result = send_reminder(
            to="+1234567890",
            date="2026-06-20",
            time="14:00",
            business_name="Test Clinic",
        )

        assert result == "SM9998887777"
        mock_send.assert_called_once()
        call_args = mock_send.call_args[1]
        assert "Reminder" in call_args["message"]
        assert "Test Clinic" in call_args["message"]

    def test_get_twilio_client_missing_credentials(self, monkeypatch):
        from backend import config
        monkeypatch.setattr(config.settings, "TWILIO_ACCOUNT_SID", "")
        monkeypatch.setattr(config.settings, "TWILIO_AUTH_TOKEN", "")

        with pytest.raises(ValueError, match="Twilio credentials not configured"):
            get_twilio_client()

    def test_validate_e164_invalid(self):
        with pytest.raises(ValueError, match="Invalid E.164 phone format"):
            _validate_e164("123456")

    def test_validate_e164_valid(self):
        assert _validate_e164("+971501234567") == "+971501234567"
