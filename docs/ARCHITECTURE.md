# Architecture

See README.md for the full architecture diagram and description.

## v4.0.0 Security & Compliance Additions

- **GDPR Erase**: `DELETE /patients/{phone_hash}` anonymizes all records.
- **Quiet Hours SMS**: SMS queued during 21h-08h, delivered at 08h00 via APScheduler.
- **Calendar Conflict Detection**: `check_conflict()` prevents double-booking.
- **Emergency Transfer**: Twilio Voice dial + SMS alert to doctor.
- **Refresh Token Rotation**: Cookie-based auth with 7-day refresh tokens.
- **Automatic Purge**: Daily cleanup of old records per retention policy.
