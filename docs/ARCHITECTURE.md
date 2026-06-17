# Architecture Documentation — AI Receptionist Enterprise

> **Version:** 2.1  
> **Last updated:** June 2026  
> **Author:** [Your Name]

---

## 1. High-Level Architecture

```
┌─────────────┐     Voice Call      ┌─────────────┐     Webhook POST     ┌─────────────────┐
│   Caller    │ ──────────────────> │  Vapi AI    │ ───────────────────> │  FastAPI        │
│  (Patient)  │                     │  Voice Agent│  HMAC-signed         │  Backend        │
└─────────────┘                     └─────────────┘                      │  (Render Cloud) │
                                                                         └────────┬────────┘
                                                                                  │
                                    ┌─────────────────────────────────────────────┼─────────────┐
                                    │                                             │             │
                                    ▼                                             ▼             ▼
                            ┌─────────────┐                              ┌─────────────┐  ┌─────────────┐
                            │  Google     │                              │   Twilio    │  │  JSON Log   │
                            │  Calendar   │                              │   SMS API   │  │  (Storage)  │
                            └─────────────┘                              └─────────────┘  └─────────────┘
                                    │                                             │             │
                                    │                                             │             │
                                    ▼                                             ▼             ▼
                            ┌─────────────┐                              ┌─────────────┐  ┌─────────────┐
                            │  Calendar   │                              │  Patient    │  │  Dashboard  │
                            │  Events     │                              │  SMS Inbox  │  │  (GitHub    │
                            │  + Reminders│                              │             │  │   Pages)    │
                            └─────────────┘                              └─────────────┘  └─────────────┘
```

---

## 2. Component Breakdown

### 2.1 Voice Layer — Vapi.ai

**Role:** Natural language understanding, voice synthesis, function calling.

**Configuration:**
- System prompt (`vapi_config/prompt_system.txt`)
- Function definitions (`vapi_config/functions.json`)
- Voice model: Latest Conversational AI
- Languages: Auto-detect (EN/ES/FR/AR)

**Data Flow:**
1. Caller dials Twilio number
2. Twilio forwards to Vapi
3. Vapi processes voice → text → intent
4. Vapi calls functions (book_appointment, transfer_call)
5. Vapi sends webhook to backend on call end

### 2.2 Backend — FastAPI

**Role:** Webhook receiver, data processing, third-party integrations.

**Modules:**

| Module | File | Responsibility |
|--------|------|----------------|
| Config | `config.py` | Environment variables, validation |
| Models | `models.py` | Pydantic data validation |
| Security | `security.py` | HMAC webhook verification |
| Webhook | `main.py` | API endpoints, request handling |
| Calendar | `calendar_sync.py` | Google Calendar API integration |
| SMS | `sms_sender.py` | Twilio SMS API integration |

**Endpoints:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/vapi-webhook` | POST | Receives call-end events from Vapi |
| `/calls` | GET | Returns call logs for dashboard |
| `/stats` | GET | Returns aggregated daily statistics |
| `/health` | GET | Health check for monitoring |
| `/` | GET | API info and documentation links |

**Security:**
- HMAC-SHA256 webhook signature verification
- Environment variable isolation (no secrets in code)
- CORS restricted to dashboard origin
- Input validation via Pydantic models

### 2.3 Data Storage

**JSON Log File (`calls_log.json`)**
- Append-only structure
- Each entry: timestamp, call_id, phone, status, transcript, appointment, duration
- Persistent on Render disk (free tier: ephemeral, pro: persistent)
- **Note:** For production scale, migrate to PostgreSQL or SQLite

### 2.4 Dashboard — HTML/CSS/JS

**Role:** Real-time visualization for the client.

**Features:**
- Auto-refresh every 30 seconds
- Search by phone number
- Filter by status (completed, missed, transferred)
- Responsive design (mobile-first)
- Zero external dependencies (vanilla JS)

**Hosting:** GitHub Pages (free, SSL, CDN)

---

## 3. Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                            │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: Network                                           │
│  • HTTPS only (Render + GitHub Pages)                       │
│  • CORS restricted to dashboard origin                      │
│                                                             │
│  Layer 2: Authentication                                    │
│  • HMAC-SHA256 webhook signatures                         │
│  • OAuth 2.0 for Google Calendar                          │
│  • Twilio API keys (server-side only)                     │
│                                                             │
│  Layer 3: Data Protection                                   │
│  • No PII in logs (phone numbers hashed optionally)       │
│  • Environment variables isolated                           │
│  • .env excluded from Git                                 │
│                                                             │
│  Layer 4: Input Validation                                  │
│  • Pydantic models for all payloads                       │
│  • Strict type checking                                     │
│  • Rate limiting ready (add middleware)                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Deployment Architecture

### Render (Primary)
```yaml
services:
  - type: web
    runtime: python
    plan: free  # or starter ($5/month)
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn main:app --host 0.0.0.0 --port 10000"
```

**Environment Variables:**
- All secrets configured via Render dashboard (never in code)
- Auto-deploy on Git push
- Health check endpoint for monitoring

### GitHub Pages (Dashboard)
```
Source: /dashboard folder
Branch: gh-pages (auto-generated by CI)
URL: https://your-username.github.io/AI_Receptionist_Enterprise/
```

---

## 5. Scalability Considerations

| Current | Bottleneck | Solution |
|---------|-----------|----------|
| JSON file storage | Concurrent writes, file size | Migrate to SQLite/PostgreSQL |
| Single Render instance | Traffic spikes | Add load balancer, upgrade plan |
| Synchronous SMS | Slow response | Queue with Redis/Celery |
| No caching | Repeated API calls | Add Redis cache for calendar |

---

## 6. Monitoring & Observability

**Health Check:**
```bash
curl https://your-app.onrender.com/health
# Expected: {"status": "ok", "version": "2.1.0", ...}
```

**Logs:**
- Structured JSON logs in `calls_log.json`
- Render dashboard for server logs
- Vapi dashboard for call analytics

**Alerts (Future):**
- Webhook failures > 5% in 1 hour
- SMS delivery failures > 10%
- Calendar sync errors > 3 in 1 hour

---

*Architecture Document v2.1 — AI Receptionist Enterprise*
