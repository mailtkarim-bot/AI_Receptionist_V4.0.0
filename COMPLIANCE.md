# Compliance & Security -- AI Receptionist Enterprise

## Data Handling
- Phone numbers are SHA-256 hashed in the database
- Transcripts are stored encrypted at rest (PostgreSQL)
- No patient medical data is stored (only appointment metadata)

## Dubai VARA Alignment
- Data residency: Render PostgreSQL (US) -- migrate to UAE region if required
- Encryption: TLS 1.3 in transit, AES-256 at rest
- Access control: JWT-based authentication, rate limiting
- Audit trail: All webhook events logged with IP and timestamp

## GDPR (for EU patients)
- Right to erasure: DELETE /calls/{id} endpoint (on request)
- Data minimization: Only necessary fields collected
- Consent: Implied via phone call interaction

## Security Measures
- HMAC-SHA256 webhook verification
- Rate limiting: 30 req/min (webhook), 100 req/min (API)
- SQL injection prevention: SQLAlchemy ORM (parameterized queries)
- XSS prevention: Input sanitization on all endpoints

## Disclaimer
This software is provided as-is. A professional security audit is recommended before handling PHI (Protected Health Information) under HIPAA or equivalent local regulations.