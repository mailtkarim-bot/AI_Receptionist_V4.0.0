"""Tests for Google Calendar synchronization."""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from backend.calendar_sync import create_event


class TestCalendarSync:
    """Test suite for Google Calendar integration."""

    @patch("backend.calendar_sync.get_calendar_service")
    def test_create_event_success(self, mock_get_service):
        """Should create calendar event successfully."""
        mock_service = MagicMock()
        mock_events = MagicMock()
        mock_insert = MagicMock()
        mock_insert.execute.return_value = {"id": "event-123", "htmlLink": "https://calendar.google.com/test"}
        mock_events.insert.return_value = mock_insert
        mock_service.events.return_value = mock_events
        mock_get_service.return_value = mock_service
        
        result = create_event(
            phone="+1234567890",
            date_str="2026-06-20",
            time_str="14:00",
            duration_min=30,
            service="checkup",
        )
        
        assert result == "event-123"
        mock_events.insert.assert_called_once()
        call_args = mock_events.insert.call_args[1]
        assert call_args["calendarId"] == "primary"
        assert call_args["body"]["summary"] == "APT -- +1234567890 -- checkup"

    @patch("backend.calendar_sync.get_calendar_service")
    def test_create_event_invalid_date(self, mock_get_service):
        """Should handle invalid date format gracefully."""
        result = create_event(
            phone="+1234567890",
            date_str="invalid-date",
            time_str="14:00",
        )
        assert result is None

    @patch("backend.calendar_sync.get_calendar_service")
    def test_create_event_api_error(self, mock_get_service):
        """Should handle Google API errors gracefully."""
        mock_service = MagicMock()
        mock_events = MagicMock()
        mock_insert = MagicMock()
        mock_insert.execute.side_effect = Exception("API Error")
        mock_events.insert.return_value = mock_insert
        mock_service.events.return_value = mock_events
        mock_get_service.return_value = mock_service
        
        result = create_event(
            phone="+1234567890",
            date_str="2026-06-20",
            time_str="14:00",
        )
        assert result is None

    @patch("backend.calendar_sync.get_calendar_service")
    def test_create_event_reminders_set(self, mock_get_service):
        """Should set SMS and popup reminders."""
        mock_service = MagicMock()
        mock_events = MagicMock()
        mock_insert = MagicMock()
        mock_insert.execute.return_value = {"id": "event-456"}
        mock_events.insert.return_value = mock_insert
        mock_service.events.return_value = mock_events
        mock_get_service.return_value = mock_service
        
        create_event(phone="+1234567890", date_str="2026-06-20", time_str="14:00")
        
        body = mock_events.insert.call_args[1]["body"]
        reminders = body["reminders"]["overrides"]
        assert any(r["method"] == "sms" and r["minutes"] == 60 for r in reminders)
        assert any(r["method"] == "popup" and r["minutes"] == 30 for r in reminders)
