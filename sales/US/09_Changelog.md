# Changelog — AI Receptionist Client Setup
> **Internal document — To be filled by the developer for each client**  
> **Version :** 2.0 US Edition — Aligned with Kit v5.1  
> **Goal :** Full traceability, guaranteed quality, professional delivery

---

## [DATE] — Client : [CLIENT_NAME]

### 📋 Client Information (fill before starting)

- [ ] **Client name / business :** ___________________
- [ ] **Client email :** ___________________
- [ ] **Client phone :** ___________________
- [ ] **Address :** ___________________
- [ ] **Google Calendar email :** ___________________
- [ ] **Mobile number (emergencies) :** ___________________
- [ ] **Opening hours :** ___________________
- [ ] **Services offered :** ___________________
- [ ] **Languages :** ___________________
- [ ] **Closure days :** ___________________
- [ ] **Setup price :** $2,500
- [ ] **Payment structure :** 30/40/30
- [ ] **30% deposit received :** $750 ✅ / ⬜
- [ ] **Signature date :** ___________________

---

### 🔧 Phase 1 : Configuration (Day 1-2)

#### Vapi — AI Voice Assistant
- [ ] Vapi account created in client's name (email : ___________________)
- [ ] Custom prompt written and validated
- [ ] Voice selected and tested
- [ ] Languages configured (EN / ES / FR / AR)
- [ ] Vapi functions configured :
  - [ ] `book_appointment` — Appointment booking
  - [ ] `check_availability` — Availability check
  - [ ] `transfer_call` — Call transfer
  - [ ] `send_sms` — SMS sending
  - [ ] `handle_emergency` — Emergency handling
- [ ] Twilio phone number purchased : `+...`
- [ ] Vapi webhook configured (backend URL)
- [ ] Internal voice tests completed (5 calls)

#### Backend — FastAPI Server
- [ ] GitHub repo created / cloned
- [ ] Python environment configured (requirements.txt)
- [ ] FastAPI app structured
- [ ] Endpoints created :
  - [ ] POST `/webhook` — Receive Vapi calls
  - [ ] POST `/calendar` — Create Google Calendar events
  - [ ] POST `/sms` — Send Twilio SMS
  - [ ] GET `/dashboard` — Real-time data
  - [ ] GET `/health` — Health check
- [ ] HMAC security implemented (webhook signature)
- [ ] Structured logs configured
- [ ] Secure environment variables (.env)

#### Google Calendar
- [ ] Google Calendar shared with service account
- [ ] OAuth 2.0 configured (credentials.json)
- [ ] Event creation test successful
- [ ] SMS reminders configured (1h + 30min)
- [ ] Title and description standardized

---

### 🎨 Phase 2 : Dashboard & Frontend (Day 2-3)

- [ ] Dashboard HTML/CSS created
- [ ] Client logo and colors integrated
- [ ] Backend API connection working
- [ ] Auto-refresh 30 seconds implemented
- [ ] Filters (number, status, date) functional
- [ ] Responsive design (PC, mobile, tablet)
- [ ] GitHub Pages / Render hosting configured
- [ ] Dashboard URL : `https://...`

---

### 📱 Phase 3 : Twilio SMS (Day 3)

- [ ] Twilio account created in client's name
- [ ] Sending number configured
- [ ] Confirmation SMS template written :
  > *"Your appointment is confirmed for [date] at [time]. [Business name]. To reschedule, call us."*
- [ ] Reminder SMS template written (optional)
- [ ] SMS sending test successful
- [ ] SMS received on test phone

---

### 🧪 Phase 4 : Testing & Validation (Day 3-4)

#### Scenario 1 : Standard appointment booking
- [ ] Test call completed
- [ ] AI offered correct time slots
- [ ] Appointment created in Google Calendar
- [ ] Confirmation SMS received
- [ ] Dashboard displays call with status "completed"
- [ ] Transcription accurate

#### Scenario 2 : Information request
- [ ] Test call completed
- [ ] AI gave correct information (hours, rates, address)
- [ ] AI offered to book an appointment
- [ ] Dashboard displays call with status "completed"

#### Scenario 3 : Emergency + transfer
- [ ] Test call completed with emergency keyword
- [ ] AI recognized the emergency
- [ ] AI gave correct procedure
- [ ] Transfer to mobile number tested (if configured)
- [ ] Dashboard displays call with status "transferred"

#### Scenario 4 : After-hours call
- [ ] Test call completed at 8:00 PM
- [ ] AI answered and offered appointments
- [ ] Appointment created in Google Calendar
- [ ] SMS received

#### Scenario 5 : Secondary language
- [ ] Test call in Spanish / French / Arabic
- [ ] AI switched language correctly
- [ ] Conversation fluent and understandable

#### Technical tests
- [ ] 10 simulated calls completed
- [ ] Success rate : _____% (target : ≥ 90%)
- [ ] HMAC webhook validated (no security flaw)
- [ ] Complete and readable logs
- [ ] No 500 errors in the last 24 hours

---

### 🚀 Phase 5 : Deployment (Day 4-5)

- [ ] Backend deployed on Render : `https://...`
- [ ] Dashboard hosted on GitHub Pages / Render : `https://...`
- [ ] Environment variables configured in production
- [ ] Vapi webhook points to production URL
- [ ] Health check successful (endpoint `/health` returns 200)
- [ ] SSL/HTTPS enabled on all URLs
- [ ] No sensitive data hardcoded in the code
- [ ] .gitignore configured (no .env or credentials in plain text)

---

### 📦 Phase 6 : Delivery (Day 5)

- [ ] **Client Guide** sent by email (document 09)
- [ ] **Dashboard link** tested and working from client's phone
- [ ] **Vapi/Twilio accounts** handed to client (credentials + passwords)
- [ ] **Google Calendar** verified — appointments appear correctly
- [ ] **30% deposit invoice** sent (if not already done)
- [ ] **40% delivery invoice** sent
- [ ] **Zoom training call** completed (30 min)
  - [ ] Live demo of the AI number
  - [ ] Dashboard explanation
  - [ ] Google Calendar explanation
  - [ ] Recurring costs explanation
  - [ ] Client questions answered
  - [ ] Receptionist questions answered
- [ ] **Zoom recording** sent to client (if recorded)

---

### 📅 Phase 7 : Support (Day 5-35)

- [ ] **Day 5-7 :** Daily log check (5 min/day)
- [ ] **Day 7 :** Check-in email to client : "Is everything working well ?"
- [ ] **Day 14 :** Check-in email : "Need any adjustments ?"
- [ ] **Day 21 :** Check-in email : "Monthly statistics"
- [ ] **Day 30 :** Validation email : "Are you satisfied ?"
- [ ] **Day 35 :** Final 30% invoice sent
- [ ] **Prompt modification** (1x included) : completed / not requested
- [ ] **Bugs reported** : _____ / fixed : _____
- [ ] **Client satisfaction rate** : _____% (target : ≥ 90%)

---

### 📝 Notes & Lessons Learned

**What worked well :**
- 

**What was difficult :**
- 

**What I would do differently next time :**
- 

**Client feedback :**
- 

**Receptionist feedback :**
- 

---

### ✅ Final Checklist — Before Closing the File

- [ ] All accounts are in the client's name
- [ ] The client has credentials for all accounts
- [ ] The client knows how to refill Vapi and Twilio
- [ ] The client has pinned the dashboard to their phone
- [ ] The receptionist has been trained and is comfortable
- [ ] The client is satisfied (success rate ≥ 90%)
- [ ] The final invoice is paid
- [ ] The file is archived with this changelog
- [ ] The client knows how to contact me for post-30d support

---

*Changelog AI Receptionist v2.0 US Edition — Internal developer*  
*"Quality before speed. Traceability before improvisation."*
