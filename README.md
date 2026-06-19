<div align="center">

# AI Voice Agent — Smart Appointment Booking for SMEs

**Freelance AI Voice Agent Toolkit — Universal Edition v4.0.0**

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Vapi](https://img.shields.io/badge/Vapi-AI%20Voice-FF6F00?style=for-the-badge)
![Twilio](https://img.shields.io/badge/Twilio-F22F46?style=for-the-badge&logo=twilio&logoColor=white)

**24/7 Call Answering · Appointment Booking · SMS Confirmation · JWT-Secured Dashboard · Emergency Transfer · GDPR Compliant**

📐 Architecture · 🚀 Quick Start · 💰 Business Model · 🔐 Security · 📞 Contact

</div>

---

## TL;DR

AI voice receptionist for **any business that takes phone appointments**. **FastAPI** backend + **PostgreSQL** persistence + **Vapi** voice AI + **Twilio** SMS/Voice + **Google Calendar** sync + **JWT-secured dashboard** with **httpOnly cookies**.

Sold as a **$2,500 one-time freelance setup** (not SaaS). Client pays Vapi/Twilio consumption directly. Zero recurring platform fees.

**Built for global markets** — multilingual EN/FR/AR, timezone-aware, GDPR Right to Erasure, quiet-hours SMS, calendar conflict detection, and emergency call transfer.

> 🆕 **v4.0.0 Enterprise**: GDPR erase endpoint, quiet-hours SMS queue, calendar conflict detection, emergency Twilio voice transfer, refresh token rotation, automatic data purge, security headers, HMAC webhook replay protection, and SHA-256 PII hashing with zero plaintext persistence.

---

## 🎯 Why I Built This

Running a small business? Your team clocks out at 6 PM. Your customers call at 8 PM. Those calls go to voicemail — and **60% never call back**.

This toolkit lets a **freelance developer** deploy a production-grade AI receptionist for **any SME** in **under 48 hours**:

- AI answers in natural voice (Arabic, English, French)
- Books directly into the owner's Google Calendar — **with conflict detection**
- Sends SMS confirmation instantly — **or queues for quiet hours**
- **Transfers urgent calls** to the owner's mobile via Twilio Voice
- **Secure dashboard** shows every call, every booking, every recovered lead — **login required with rotating refresh tokens**
- **One-click GDPR erasure** — anonymize any customer on request

**One setup. $2,500. Client owns their infrastructure.**

### Sectors Supported (Out of the Box)

| Sector | Use Case |
|--------|----------|
| 🏥 **Clinics & Medical** | Book consultations, transfer emergencies, send reminders |
| 🍽️ **Restaurants** | Table reservations, party size, dietary restrictions |
| ✂️ **Salons & Spas** | Booking slots, service selection, stylist preference |
| 🔧 **Garages & Auto** | Maintenance appointments, vehicle check-in, urgent repairs |
| 🏠 **Real Estate Agencies** | Property visit bookings, lead qualification, address sharing |
| ⚖️ **Law Firms** | Appointment booking, case-type triage, urgent criminal transfer |
| 🏨 **Hotels & Hospitality** | Room bookings, concierge requests, late check-ins |
| 🐕 **Veterinary Clinics** | Pet appointments, emergency transfers, vaccination reminders |

> The **backend code is 100% identical** across all sectors. Only the **prompt**, **SMS wording**, and **Google Calendar event titles** change.

---

## 📐 Architecture

```mermaid
flowchart TB
    subgraph Caller
        A[📞 Customer calls]
    end

    subgraph Voice
        B[Vapi AI Voice Agent<br/>STT + LLM + TTS<br/>EN/FR/AR auto-detect]
    end

    subgraph Backend["Backend — FastAPI + PostgreSQL"]
        C[FastAPI Webhook<br/>HMAC-SHA256 + Replay Protection]
        D[(PostgreSQL<br/>Persistent storage)]
        E[Audit Logger<br/>IP + Timestamp + Action + Payload]
        F[Rate Limiter<br/>30 req/min webhook]
        G[Google Calendar API<br/>OAuth 2.0 + Conflict Detection]
        H[Twilio SMS<br/>Confirmation + Reminders + Queue]
        H2[Twilio Voice<br/>Emergency Transfer]
        SCH[APScheduler<br/>Quiet Hours + Purge + Retry]
    end

    subgraph Dashboard["Dashboard — JWT + httpOnly Cookies"]
        I[📊 Real-Time Dashboard<br/>HTML/CSS/JS<br/>Auto-refresh Token]
    end

    subgraph Monitoring
        J[Sentry Error Tracking]
        K[n8n Alert Webhook<br/>Telegram / Slack]
    end

    A --> B
    B -->|End-of-call webhook| C
    C --> F
    F --> D
    C --> E
    C --> G
    C --> H
    C --> H2
    C --> SCH
    SCH --> H
    D --> I
    C --> J
    J --> K

    style B fill:#e1f5fe
    style C fill:#fff3e0
    style D fill:#fce4ec
    style I fill:#e8f5e9
    style K fill:#f3e5f5
    style SCH fill:#fff8e1
    style H2 fill:#ffebee
```

---

## 🚀 What's New in v4.0.0 Enterprise

| Feature | v3.0 (Previous) | v4.0 Enterprise (Now) |
|---------|----------------|----------------------|
| **GDPR Right to Erasure** | Mentioned only | **`DELETE /customers/{phone_hash}`** — anonymizes all records instantly |
| **Quiet Hours SMS** | Sent immediately 24/7 | **Queued 21h–08h**, delivered at 08h00 via APScheduler |
| **Calendar Conflict Detection** | Blind insert | **`check_conflict()`** prevents double-booking before insert |
| **Emergency Transfer** | Flag stored only | **Twilio Voice `<Dial>`** + SMS alert to owner |
| **Refresh Token Rotation** | 60-min expiry, no refresh | **7-day rotating refresh tokens** in DB, auto-refresh dashboard |
| **Automatic Data Purge** | None | **Daily cron** — calls 2y, audit 1y, SMS queue 30d, revoked tokens |
| **Security Headers** | None | **HSTS + CSP + X-Frame-Options + X-Content-Type-Options** |
| **Webhook Replay Protection** | None | **Timestamp window 5min + idempotence by `call_id`** |
| **PII Storage** | Phone plaintext in DB | **SHA-256 hashed ONLY** — zero plaintext persistence |
| **Health Check** | Hardcoded "connected" | **Real DB `SELECT 1`** — returns 503 if PostgreSQL down |
| **Cookie Security** | localStorage token | **httpOnly + Secure + SameSite=Strict** cookies |
| **Input Validation** | Raw dict | **Pydantic `VapiWebhookPayload`** validation on every webhook |
| **CORS** | Wildcard `*` fallback | **Strict origin whitelist** — no fallback |
| **Password Security** | Hardcoded fallback | **Zero fallback** — crash at startup if missing |
| **Deployment** | Uvicorn single worker | **Gunicorn + 2 Uvicorn workers** — production-ready |

---

## ✨ What the Client Gets

### For the Business Owner

| Feature | Benefit |
|---------|---------|
| **24/7 call answering** | Zero missed calls after hours, weekends, holidays |
| **Auto-booking** | Appointments land directly in owner's Google Calendar |
| **Calendar conflict guard** | No double-booking — AI checks availability first |
| **SMS confirmation** | Customer receives instant text; quiet hours queued for morning |
| **Emergency transfer** | Urgent calls forwarded to owner's mobile **instantly via voice** |
| **Real-time dashboard** | See all calls, bookings, missed calls, transcripts — **secure login** |
| **Multilingual** | English, French, Arabic — auto-detected |
| **No lock-in** | Client owns their Vapi/Twilio accounts. Stop anytime. |
| **GDPR ready** | One-click customer data anonymization on request |

### For the Developer (You)

| Feature | Benefit |
|---------|---------|
| **PostgreSQL Persistence** | Data survives server restarts. Real database. |
| **JWT + Refresh Token Rotation** | Dashboard protected with 7-day sessions. No re-login hell. |
| **Alembic Migrations** | Schema changes are versioned and reversible. |
| **Structured Logging** | JSON logs with `structlog` — parseable by any SIEM. |
| **Rate Limiting** | Anti-bot protection on webhooks. |
| **Audit Logging** | Every webhook, every calendar sync, every SMS — logged with IP. |
| **Sentry Integration** | Production errors captured instantly. |
| **HMAC Webhook Verification** | Every Vapi request cryptographically signed. |
| **Security Headers** | HSTS, CSP, X-Frame-Options — OWASP-compliant. |
| **Auto-Purge** | Database never bloats. Compliance retention enforced. |

---

## 💰 Business Model — Freelance Setup (Not SaaS)

This is a **one-time deployment service**, not a monthly subscription.

| Item | Who Pays | Amount |
|------|----------|--------|
| **Your setup fee** | Client → You | **$2,500 one-time** |
| Vapi (voice AI) | Client → Vapi.ai | ~$0.05/minute |
| Twilio (number + SMS + Voice) | Client → Twilio | ~$1/mo number + $0.01-0.05/SMS + voice calls |
| Render (hosting) | You or Client | $7-12/mo (Starter + PostgreSQL) |
| Google Calendar | Client → Google | Free (quota limits) |
| GitHub Pages (dashboard) | Free | $0 |

> **Why this model?** You sell expertise and configuration. The client pays their own consumption. No SaaS overhead, no support tickets at 2 AM, no billing complexity. You deliver, train, and move to the next client.

### Pricing Tiers (SME Generic)

| Offer | Price | What's Included | Delivery |
|-------|-------|----------------|----------|
| **Setup Basic** | $1,500 | 1 Twilio number, 1 Google Calendar, SMS confirmation, dashboard, 1 language (EN/FR/AR) | 48h |
| **Setup Pro** | $2,500 | Basic + quiet hours + conflict detection + emergency transfer + GDPR erase + 2 languages | 72h |
| **Setup Enterprise** | $4,000 | Pro + multi-calendars (3) + custom prompt + branded voice + WhatsApp-ready | 1 week |

**Optional recurring revenue (monthly):**
- Support/maintenance: $150-300/mo
- Prompt modifications: $50/h
- Additional languages: $200/language

---

## 🔐 Security & Compliance

### Security Layers

| Layer | Implementation |
|-------|---------------|
| **Webhook Verification** | HMAC-SHA256 signature + 5-min timestamp window + `call_id` idempotence |
| **Authentication** | JWT access token (15 min) + rotating refresh token (7 days) in httpOnly cookies |
| **Rate Limiting** | `slowapi` — 30 req/min webhook, 100 req/min API, 10 req/min login |
| **Database** | SQLAlchemy ORM — parameterized queries (SQL injection proof) |
| **PII Handling** | Phone numbers **SHA-256 hashed** in DB; **plaintext NEVER persisted**; SMS queue purged in 30d |
| **Secrets** | Environment variables only — **zero fallback values**; crash at startup if missing |
| **HTTPS** | SSL/TLS on all endpoints (Render) + HSTS header |
| **Audit Trail** | Every action logged with source IP, timestamp, success/failure, payload summary |
| **Security Headers** | `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `CSP: default-src 'self'` |
| **Emergency Isolation** | Emergency logic isolated; voice transfer via Twilio `<Dial>` |

### Compliance

| Standard | Status |
|----------|--------|
| **GDPR** | **Right to erasure endpoint** (`/customers/{phone_hash}`), data minimization, hashed PII, 2-year retention |
| **Dubai VARA** | Data minimization, TLS 1.3, hashed PII, retention policy, audit trail |
| **HIPAA-ready** | *Requires third-party audit before PHI handling* |
| **OWASP Top 10** | Mitigated: Injection, Broken Auth, Sensitive Data Exposure, Security Misconfiguration, Insufficient Logging |
| **PCI-DSS** | *No card data handled. Twilio processes telecom.* |

> **Disclaimer:** This project is provided for professional portfolio and educational purposes. A **third-party security audit is mandatory** before production deployment in regulated environments. The author is not liable for misuse or deployment without proper review. All code includes prominent warnings that projects are educational and require professional audit before real deployment.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL 15+ (local or cloud)
- Vapi account (vapi.ai)
- Twilio account (twilio.com) with Voice + SMS enabled
- Google Cloud project (Calendar API enabled)
- Render account (render.com)

### 1. Clone & Install

```bash
git clone https://github.com/mailtkarim-bot/AI_Receptionist_V4.0.0.git
cd AI_Receptionist_V4.0.0
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env with STRONG credentials — NO FALLBACKS exist in code
# Generate SECRET_KEY: openssl rand -hex 32
# Generate ADMIN_PASSWORD: openssl rand -base64 24
```

### 3. Initialize Database

```bash
# Create local PostgreSQL database
createdb ai_receptionist

# Generate migration for new tables (SMSQueue, RefreshToken)
alembic revision --autogenerate -m "v4_add_sms_queue_refresh_tokens"

# Run migrations
alembic upgrade head
```

### 4. Run Locally

```bash
uvicorn backend.main:app --reload --port 8000
```

### 5. Test Webhook

```bash
# Generate HMAC signature
SECRET="your_vapi_webhook_secret"
BODY='{"call":{"id":"test-001","customer":{"number":"+97150XXXXXXX"}},"status":"completed","analysis":{"booked_appointment":{"date":"2026-06-20","time":"14:00","duration_minutes":30,"service":"checkup"}}}'
SIG=$(echo -n "$BODY" | openssl dgst -sha256 -hmac "$SECRET" | sed 's/^.* //')

curl -X POST http://localhost:8000/vapi-webhook   -H "Content-Type: application/json"   -H "X-Vapi-Signature: $SIG"   -d "$BODY"
```

### 6. Test GDPR Erase

```bash
# Login first
curl -X POST http://localhost:8000/token   -d "username=admin&password=$ADMIN_PASSWORD"   -c cookies.txt

# Erase customer (replace with actual SHA-256 hash)
PHONE_HASH=$(echo -n "+97150XXXXXXX" | sha256sum | awk '{print $1}')
curl -X DELETE "http://localhost:8000/customers/$PHONE_HASH"   -b cookies.txt
```

### 7. Deploy to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

---

## 📁 Project Structure

```
AI_Receptionist_V4.0.0/
├── 📄 README.md                 # This file
├── 📄 COMPLIANCE.md             # VARA/GDPR/HIPAA alignment
├── 📄 CLIENT_SETUP.md           # Post-delivery handover guide (universal)
├── 📄 SECTORS.md                # Sector adaptation guide
├── 📄 LICENSE                   # MIT License
├── 📄 .env.example              # Environment template (NO secrets, NO fallbacks)
├── 📄 alembic.ini               # Database migration config
├── 📄 requirements.txt           # Pinned dependencies
├── 📄 render.yaml               # Render.com deployment blueprint
│
├── 🐍 backend/                  # FastAPI Enterprise Application
│   ├── __init__.py
│   ├── main.py                   # Webhook + API + Auth + Health + GDPR Erase + Refresh
│   ├── database.py               # SQLAlchemy engine & session
│   ├── models_db.py              # PostgreSQL ORM (CallRecord, AppointmentRecord, AuditLog, SMSQueue, RefreshToken)
│   ├── config.py                 # Settings & strict validation (zero fallback)
│   ├── security.py               # HMAC + replay protection + body size limit
│   ├── calendar_sync.py          # Google Calendar OAuth + conflict detection
│   ├── sms_sender.py             # Twilio SMS service + E.164 validation + masked logs
│   ├── scheduler.py              # APScheduler: purge + quiet hours + retry
│   └── models.py                 # Pydantic schemas (validation + EraseRequest)
│
├── 🗣️ alembic/                   # Database Migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│
├── 🎨 dashboard/                  # JWT-Secured Client Dashboard
│   ├── index.html                # Auth wall + analytics UI
│   ├── app.js                    # API client with httpOnly cookies + auto-refresh
│   └── style.css                 # Responsive dark theme
│
├── 🗣️ vapi_config/                # AI Voice Configuration
│   ├── prompt_system.txt         # Generic universal prompt
│   ├── prompt_restaurant.txt     # Restaurant reservation prompt
│   ├── prompt_garage.txt         # Auto garage prompt
│   ├── prompt_salon.txt          # Beauty salon prompt
│   ├── prompt_agency.txt         # Real estate agency prompt
│   ├── prompt_lawyer.txt         # Law firm prompt
│   └── functions.json            # Vapi function definitions
│
├── 🧪 tests/                      # Enterprise Test Suite
│   ├── __init__.py
│   ├── test_e2e.py
│   ├── test_webhook.py
│   ├── test_security.py
│   ├── test_calendar.py
│   ├── test_sms.py
│   └── test_scheduler.py
│
├── 📚 docs/
│   └── ARCHITECTURE.md
│
└── 🔧 .github/
    └── workflows/
        └── ci.yml
```

---

## 🧪 Testing

```bash
# Run full test suite with PostgreSQL
pytest tests/ -v --cov=backend --cov-report=html

# Run specific module
pytest tests/test_e2e.py -v

# Run with coverage threshold (fails under 85%)
pytest tests/ --cov=backend --cov-report=term-missing --cov-fail-under=85
```

---

## 🎭 Sector Adaptation (5 Minutes Per Client)

The backend is **100% sector-agnostic**. To adapt for a new client:

1. **Copy the repo** (identical code)
2. **Replace the prompt** in `vapi_config/prompt_system.txt` with the sector-specific prompt
3. **Update SMS wording** in the `.env` (or `sms_templates.py`)
4. **Set the business name** and emergency phone in `.env`
5. **Deploy** — same backend, same dashboard, same security

See `SECTORS.md` for the full adaptation matrix and `customize.sh` for automated replacement.

---

## 📦 Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | FastAPI + Uvicorn + Pydantic v2 + Gunicorn |
| **Database** | PostgreSQL + SQLAlchemy ORM + Alembic |
| **Auth** | JWT (python-jose) + bcrypt (passlib) + rotating refresh tokens |
| **Rate Limiting** | slowapi |
| **Scheduling** | APScheduler (quiet hours, purge, retry) |
| **Logging** | structlog (JSON) |
| **Monitoring** | Sentry SDK |
| **Voice AI** | Vapi.ai (STT/LLM/TTS) |
| **Calendar** | Google Calendar API (OAuth 2.0) |
| **SMS** | Twilio Programmable Messaging |
| **Voice** | Twilio Programmable Voice (emergency transfer) |
| **Dashboard** | Vanilla HTML/CSS/JS (zero dependencies) |
| **CI/CD** | GitHub Actions + pytest + PostgreSQL service + pip-audit |
| **Hosting** | Render (backend) + GitHub Pages (dashboard) |

---

## 🗺️ Roadmap

| Quarter | Milestone |
|---------|-----------|
| **Q2 2026** | ✅ v4.0.0: GDPR erase, quiet hours, conflict detection, emergency transfer, refresh tokens, auto-purge, security headers |
| **Q3 2026** | WhatsApp Business integration, n8n automation workflows |
| **Q3 2026** | Multi-tenancy (one backend, multiple businesses) |
| **Q4 2026** | CRM connectors (HubSpot, Salesforce, Zoho) |
| **Q4 2026** | Voice cloning for branded business voices |
| **Q1 2027** | Analytics dashboard with revenue recovery metrics |
| **Q2 2027** | AWS KMS integration for end-to-end PII encryption |

---

## 🏢 Need Something Bigger?

This toolkit is perfect for **solo businesses and small SMEs** who want to own their infrastructure.

If you're a **chain, franchise, or corporate group** looking for:

- Multi-tenant SaaS platform
- 3-tier subscription management (Basic / Pro / Enterprise)
- WhatsApp, Email, and Web3 USDC payments
- Redis-backed security, Docker orchestration, React dashboard
- White-label solution with your own branding

**→ Check out AI Receptionist Enterprise**

The same voice AI power, engineered for scale.

---

## 🤝 Contributing

This is a professional portfolio project. Forks, issues, and feedback are welcome.

**Commit convention:**

- `feat:` — New feature
- `fix:` — Bug fix
- `sec:` — Security improvement
- `docs:` — Documentation
- `test:` — Tests
- `chore:` — Maintenance

---

## 📞 Contact

Interested in a custom AI Voice Agent for your business?

| | |
|---|---|
| **Developer** | Steh Rayan — AI Voice Agent & Automation Engineer |
| **GitHub** | @mailtkarim-bot |
| **Markets** | Dubai, UAE & GCC · Remote worldwide |
| **Availability** | Sun–Thu, 9 AM–6 PM GST |

**For freelance inquiries:** $2,500 setup + $100/hour for custom modifications.

---

## 📜 License

Licensed under the MIT License.

> **Important:** This project is provided as-is for educational and professional portfolio purposes. It requires a **third-party security audit** before production deployment in regulated environments. The author is not liable for misuse or deployment without proper review. All code includes prominent warnings that projects are educational and require professional audit before real deployment.

---

**Built with ❤️ in Dubai**

_"Never miss a call. Never lose a customer. Never compromise on security."_
