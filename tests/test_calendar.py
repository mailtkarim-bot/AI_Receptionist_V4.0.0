"""Tests for Google Calendar synchronization."""

import pytest
from unittest.mock import patch, MagicMock
from backend.calendar_sync import create_event, check_conflict


class TestCalendarSync:
    @patch("backend.calendar_sync.get_calendar_service")
    def test_create_event_success(self, mock_get_service):
        mock_service = MagicMock()
        mock_events = MagicMock()
        mock_insert = MagicMock()
        mock_insert.execute.return_value = {"id": "event-123", "htmlLink": "https://calendar.google.com/test"}
        mock_events.insert.return_value = mock_insert
        mock_service.events.return_value = mock_events
        mock_get_service.return_value = mock_service

        result = create_event(
            phone_hash="a" * 64,
            date_str="2026-06-20",
            time_str="14:00",
            duration_min=30,
            service="checkup",
        )

        assert result == "event-123"
        mock_events.insert.assert_called_once()
        call_args = mock_events.insert.call_args[1]
        assert call_args["calendarId"] == "primary"
        assert "APT --" in call_args["body"]["summary"]
        assert "a" * 64 in call_args["body"]["description"]

    @patch("backend.calendar_sync.get_calendar_service")
    def test_check_conflict_detects_overlap(self, mock_get_service):
        mock_service = MagicMock()
        mock_events = MagicMock()
        mock_list = MagicMock()
        mock_list.execute.return_value = {"items": [{"id": "existing-event"}]}
        mock_events.list.return_value = mock_list
        mock_service.events.return_value = mock_events
        mock_get_service.return_value = mock_service

        result = check_conflict(
            date_str="2026-06-20",
            time_str="14:00",
            duration_min=30,
        )
        assert result is True

    @patch("backend.calendar_sync.get_calendar_service")
    def test_check_conflict_no_overlap(self, mock_get_service):
        mock_service = MagicMock()
        mock_events = MagicMock()
        mock_list = MagicMock()
        mock_list.execute.return_value = {"items": []}
        mock_events.list.return_value = mock_list
        mock_service.events.return_value = mock_events
        mock_get_service.return_value = mock_service

        result = check_conflict(
            date_str="2026-06-20",
            time_str="14:00",
            duration_min=30,
        )
        assert result is False

    @patch("backend.calendar_sync.get_calendar_service")
    def test_create_event_invalid_date(self, mock_get_service):
        result = create_event(
            phone_hash="a" * 64,
            date_str="invalid-date",
            time_str="14:00",
        )
        assert result is None

    @patch("backend.calendar_sync.get_calendar_service")
    def test_create_event_api_error(self, mock_get_service):
        mock_service = MagicMock()
        mock_events = MagicMock()
        mock_insert = MagicMock()
        mock_insert.execute.side_effect = Exception("API Error")
        mock_events.insert.return_value = mock_insert
        mock_service.events.return_value = mock_events
        mock_get_service.return_value = mock_service

        result = create_event(
            phone_hash="a" * 64,
            date_str="2026-06-20",
            time_str="14:00",
        )
        assert result is None
