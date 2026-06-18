   
<div align="center">  
   
# 🤖 AI Receptionist Pro  
   
**Freelance AI Voice Agent Toolkit — Enterprise Edition v3.0.0**  
   
[![Version](https://img.shields.io/badge/version-3.0.0--enterprise-blue?style=for-the-badge)](https://github.com/mailtkarim-bot/AI_Receptionist_Pro)  
[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://python.org)  
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi)](https://fastapi.tiangolo.com)  
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql)](https://postgresql.org)  
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)  
[![Render](https://img.shields.io/badge/Deploy-Render-46E3B7?logo=render)](https://render.com)  
   
**24/7 Call Answering · Appointment Booking · SMS Confirmation · JWT-Secured Dashboard**  
   
[📐 Architecture](#-architecture) · [🚀 Quick Start](#-quick-start) · [💰 Business Model](#-business-model) · [🔐 Security](#-security) · [📞 Contact](#-contact)  
   
</div>  
   
---  
   
## TL;DR  
   
AI voice receptionist for clinics and SMEs. **FastAPI** backend + **PostgreSQL** persistence + **Vapi** voice AI + **Twilio** SMS + **Google Calendar** sync + **JWT-secured dashboard**.  
   
Sold as a **$2,500 one-time freelance setup** (not SaaS). Client pays Vapi/Twilio consumption directly. Zero recurring platform fees.  
   
**Built for Dubai & GCC markets** — multilingual EN/FR/AR, timezone-aware, VARA-aligned data practices.  
   
> 🆕 **v3.0.0 Enterprise**: PostgreSQL database, JWT authentication, Alembic migrations, rate limiting, audit logging, SHA-256 PII hashing, and Sentry monitoring.  
   
---  
   
## 🎯 Why I Built This  
   
Running a solo clinic in Dubai? Your receptionist clocks out at 6 PM. Your patients call at 8 PM. Those calls go to voicemail — and 60% never call back.  
   
This toolkit lets a **freelance developer** deploy a production-grade AI receptionist for any clinic in **under 48 hours**:  
- AI answers in natural voice (Arabic, English, French)  
- Books directly into the doctor's Google Calendar  
- Sends SMS confirmation instantly  
- **Secure dashboard** shows every call, every booking, every recovered patient — **login required**  
   
**One setup. $2,500. Client owns their infrastructure.**  
   
---  
   
## 📐 Architecture  
   
```mermaid  
flowchart TB  
    subgraph Caller  
        A[📞 Patient calls]  
    end  
   
    subgraph Voice  
        B[Vapi AI Voice Agent<br/>STT + LLM + TTS<br/>EN/FR/AR auto-detect]  
    end  
   
    subgraph Backend["Backend — FastAPI + PostgreSQL"]  
        C[FastAPI Webhook<br/>HMAC-SHA256 verified]  
        D[(PostgreSQL<br/>Persistent storage)]  
        E[Audit Logger<br/>IP + Timestamp + Action]  
        F[Rate Limiter<br/>30 req/min webhook]  
        G[Google Calendar API<br/>OAuth 2.0 per client]  
        H[Twilio SMS<br/>Confirmation + reminders]  
    end  
   
    subgraph Dashboard["Dashboard — JWT Secured"]  
        I[📊 Real-Time Dashboard<br/>HTML/CSS/JS<br/>Bearer Token Auth]  
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
    D --> I  
    C --> J  
    J --> K  
   
    style B fill:#e1f5fe  
    style C fill:#fff3e0  
    style D fill:#fce4ec  
    style I fill:#e8f5e9  
    style K fill:#f3e5f5  
```  
   
---  
   
## 🚀 What's New in v3.0.0 Enterprise  
   
| Feature | v2.0 (Previous) | v3.0 Enterprise (Now) |  
|---------|-----------------|------------------------|  
| **Data Storage** | JSON file (volatile) | **PostgreSQL** with Alembic migrations |  
| **Dashboard Auth** | Public (anyone with URL) | **JWT Bearer Token** — login required |  
| **Audit Trail** | Console logs only | **Persistent audit_logs** table (IP, action, success) |  
| **PII Handling** | Plain text in logs | **SHA-256 hashed** phone numbers |  
| **Rate Limiting** | None | **30 req/min** webhook, **100 req/min** API |  
| **Database Migrations** | Manual | **Alembic** — versioned schema evolution |  
| **Error Monitoring** | None | **Sentry** integration |  
| **Health Endpoint** | Basic | **/health** with DB connectivity check |  
| **CI/CD** | Lint + test | **Lint + test + PostgreSQL service + coverage** |  
   
---  
   
## ✨ What the Client Gets  
   
### For the Clinic Owner  
| Feature | Benefit |  
|---------|---------|  
| **24/7 call answering** | Zero missed calls after hours, weekends, holidays |  
| **Auto-booking** | Appointments land directly in doctor's Google Calendar |  
| **SMS confirmation** | Patient receives instant text with date, time, clinic address |  
| **Real-time dashboard** | See all calls, bookings, missed calls, transcripts — **secure login** |  
| **Multilingual** | English, French, Arabic — auto-detected |  
| **Emergency transfer** | Urgent calls forwarded to doctor's mobile instantly |  
| **No lock-in** | Client owns their Vapi/Twilio accounts. Stop anytime. |  
   
### For the Developer (You)  
| Feature | Benefit |  
|---------|---------|  
| **PostgreSQL Persistence** | Data survives server restarts. Real database. |  
| **JWT Authentication** | Dashboard protected. No public exposure. |  
| **Alembic Migrations** | Schema changes are versioned and reversible. |  
| **Structured Logging** | JSON logs with `structlog` — parseable by any SIEM. |  
| **Rate Limiting** | Anti-bot protection on webhooks. |  
| **Audit Logging** | Every webhook, every calendar sync, every SMS — logged. |  
| **Sentry Integration** | Production errors captured instantly. |  
   
---  
   
## 💰 Business Model — Freelance Setup (Not SaaS)  
   
This is a **one-time deployment service**, not a monthly subscription.  
   
| Item | Who Pays | Amount |  
|------|----------|--------|  
| **Your setup fee** | Client → You | **$2,500 one-time** |  
| Vapi (voice AI) | Client → Vapi.ai | ~$0.05/minute |  
| Twilio (number + SMS) | Client → Twilio | ~$1/mo number + $0.01-0.05/SMS |  
| Render (hosting) | You or Client | $7-12/mo (Starter + PostgreSQL) |  
| Google Calendar | Client → Google | Free (quota limits) |  
| GitHub Pages (dashboard) | Free | $0 |  
   
> **Why this model?** You sell expertise and configuration. The client pays their own consumption. No SaaS overhead, no support tickets at 2 AM, no billing complexity. You deliver, train, and move to the next client.  
   
---  
   
## 🔐 Security & Compliance  
   
### Security Layers  
   
| Layer | Implementation |  
|-------|----------------|  
| **Webhook Verification** | HMAC-SHA256 signature check on every Vapi request |  
| **Authentication** | JWT Bearer tokens (OAuth2PasswordBearer) |  
| **Rate Limiting** | `slowapi` — 30 req/min webhook, 100 req/min API |  
| **Database** | SQLAlchemy ORM — parameterized queries (SQL injection proof) |  
| **PII Handling** | Phone numbers **SHA-256 hashed** in DB; plaintext only in transit |  
| **Secrets** | Environment variables only — never hardcoded |  
| **HTTPS** | SSL/TLS on all endpoints (Render) |  
| **Audit Trail** | Every action logged with source IP, timestamp, success/failure |  
   
### Compliance  
   
| Standard | Status |  
|----------|--------|  
| **Dubai VARA** | Data minimization, encryption at rest (AES-256), TLS 1.3 in transit |  
| **GDPR** | Right to erasure supported, data minimization, hashed PII |  
| **HIPAA-ready** | *Requires third-party audit before PHI handling* |  
   
> **Disclaimer:** This project is provided for professional portfolio and educational purposes. A third-party security audit is strongly recommended before deployment in regulated healthcare environments. The author assumes no liability for production deployment without proper review.  
   
---  
   
## 🚀 Quick Start  
   
### Prerequisites  
- Python 3.12+  
- PostgreSQL 15+ (local or cloud)  
- Vapi account ([vapi.ai](https://vapi.ai))  
- Twilio account ([twilio.com](https://twilio.com))  
- Google Cloud project (Calendar API enabled)  
- Render account ([render.com](https://render.com))  
   
### 1. Clone & Install  
```bash  
git clone https://github.com/mailtkarim-bot/AI_Receptionist_Pro.git  
cd AI_Receptionist_Pro  
python -m venv venv  
source venv/bin/activate  
pip install -r requirements.txt  
```  
   
### 2. Configure  
```bash  
cp .env.example .env  
# Edit .env with your credentials  
```  
   
### 3. Initialize Database  
```bash  
# Create local PostgreSQL database  
createdb ai_receptionist  
   
# Run migrations  
alembic upgrade head  
```  
   
### 4. Run Locally  
```bash  
uvicorn backend.main:app --reload --port 8000  
```  
   
### 5. Test Webhook  
```bash  
curl -X POST http://localhost:8000/vapi-webhook \  
  -H "Content-Type: application/json" \  
  -H "X-Vapi-Signature: your_hmac_signature" \  
  -d '{  
    "call": {"id": "test-001", "customer": {"number": "+97150XXXXXXX"}},  
    "status": "completed",  
    "analysis": {  
      "booked_appointment": {  
        "date": "2026-06-20",  
        "time": "14:00",  
        "duration_minutes": 30,  
        "service": "checkup"  
      }  
    }  
  }'  
```  
   
### 6. Deploy to Render  
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)  
   
---  
   
## 📁 Project Structure  
   
```  
AI_Receptionist_Pro/  
├── 📄 README.md                 # This file  
├── 📄 COMPLIANCE.md             # VARA/GDPR/HIPAA alignment  
├── 📄 CLIENT_SETUP.md           # Post-delivery handover guide  
├── 📄 LICENSE                   # MIT License  
├── 📄 .env.example              # Environment template (no secrets)  
├── 📄 alembic.ini               # Database migration config  
├── 📄 requirements.txt           # Pinned dependencies  
├── 📄 render.yaml               # Render.com deployment blueprint  
│  
├── 🐍 backend/                  # FastAPI Enterprise Application  
│   ├── main.py                   # Webhook + API + Auth + Health  
│   ├── database.py               # SQLAlchemy engine & session  
│   ├── models_db.py              # PostgreSQL ORM models  
│   ├── config.py                 # Settings & validation  
│   ├── security.py               # HMAC + input sanitization  
│   ├── calendar_sync.py          # Google Calendar OAuth  
│   ├── sms_sender.py             # Twilio SMS service  
│   └── models.py                 # Pydantic schemas (validation)  
│  
├── 🗣️ alembic/                   # Database Migrations  
│   ├── env.py                    # Alembic environment  
│   ├── script.py.mako            # Migration template  
│   └── versions/                 # Auto-generated migrations  
│  
├── 🎨 dashboard/                  # JWT-Secured Client Dashboard  
│   ├── index.html                # Auth wall + analytics UI  
│   ├── app.js                    # API client with Bearer tokens  
│   └── style.css                 # Responsive dark theme  
│  
├── 🗣️ vapi_config/                # AI Voice Configuration  
│   ├── prompt_system.txt         # System prompt (EN/FR/AR)  
│   └── functions.json            # Vapi function definitions  
│  
├── 🧪 tests/                      # Enterprise Test Suite  
│   ├── test_e2e.py               # End-to-end: login → webhook → DB  
│   ├── test_webhook.py           # Auth & HMAC validation  
│   ├── test_security.py          # Rate limiting & sanitization  
│   ├── test_calendar.py          # Calendar sync mocks  
│   └── test_sms.py               # SMS sender mocks  
│  
├── 📚 docs/                       # Technical Documentation  
│   └── ARCHITECTURE.md           # Detailed system design  
│  
└── 🔧 .github/  
    └── workflows/  
        └── ci.yml                # Lint + test + PostgreSQL + coverage  
```  
   
---  
   
## 🧪 Testing  
   
```bash  
# Run full test suite with PostgreSQL  
pytest tests/ -v --cov=backend --cov-report=html  
   
# Run specific module  
pytest tests/test_e2e.py -v  
   
# Run with coverage  
pytest tests/ --cov=backend --cov-report=term-missing  
```  
   
---  
   
## 📦 Tech Stack  
   
| Layer | Technology |  
|-------|------------|  
| **Backend** | FastAPI + Uvicorn + Pydantic v2 |  
| **Database** | PostgreSQL + SQLAlchemy ORM + Alembic |  
| **Auth** | JWT (python-jose) + bcrypt (passlib) |  
| **Rate Limiting** | slowapi |  
| **Logging** | structlog (JSON) |  
| **Monitoring** | Sentry SDK |  
| **Voice AI** | Vapi.ai (STT/LLM/TTS) |  
| **Calendar** | Google Calendar API (OAuth 2.0) |  
| **SMS** | Twilio Programmable Messaging |  
| **Dashboard** | Vanilla HTML/CSS/JS (zero dependencies) |  
| **CI/CD** | GitHub Actions + pytest + PostgreSQL service |  
| **Hosting** | Render (backend) + GitHub Pages (dashboard) |  
   
---  
   
## 🗺️ Roadmap  
   
| Quarter | Milestone |  
|---------|-----------|  
| **Q2 2026** | ✅ PostgreSQL, JWT Auth, Alembic, Rate Limiting, Audit Logs |  
| **Q3 2026** | WhatsApp Business integration, n8n automation workflows |  
| **Q3 2026** | Multi-tenancy (one backend, multiple clinics) |  
| **Q4 2026** | CRM connectors (HubSpot, Salesforce, Zoho) |  
| **Q4 2026** | Voice cloning for branded clinic voices |  
| **Q1 2027** | Analytics dashboard with revenue recovery metrics |  
   
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
   
Interested in a custom AI Receptionist for your clinic or business?  
   
| | |  
|---|---|  
| **Developer** | Steh Rayan — AI Voice Agent & Automation Engineer |  
| **GitHub** | [@mailtkarim-bot](https://github.com/mailtkarim-bot) |  
| **Markets** | Dubai, UAE & GCC · Remote worldwide |  
| **Availability** | Sun–Thu, 9 AM–6 PM GST |  
   
**For freelance inquiries:** $2,500 setup + $100/hour for custom modifications.  
   
---  
   
## 📜 License  
   
Licensed under the [MIT License](LICENSE).  
   
> **Important:** This project is provided as-is for educational and professional portfolio purposes. It requires a third-party security audit before production deployment in healthcare or regulated environments. The author is not liable for misuse or deployment without proper review.  
   
---  
   
<div align="center">  
   
**Built with ❤️ in Dubai**    
*"Never miss a call. Never lose a patient. Never compromise on security."*  
   
</div>  
