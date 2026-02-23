# 🏗️ SICO GRC Platform - Visual Architecture Diagrams

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SICO GRC PLATFORM                                    │
│                   Saudi Regulatory Compliance System                         │
│                      (Arabic/English Bilingual)                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐         ┌──────────────────────┐         ┌─────────────────┐
│                      │         │                      │         │                 │
│   FRONTEND LAYER     │◄───────►│   BACKEND API LAYER  │◄───────►│   DATA LAYER    │
│   (Next.js 14)       │  HTTP   │   (FastAPI)          │  SQL    │   (PostgreSQL)  │
│   Port 3000          │  REST   │   Port 8000          │  Async  │   Port 5432     │
│                      │         │                      │         │                 │
│  ┌────────────────┐  │         │  ┌────────────────┐  │         │  ┌───────────┐  │
│  │ App Router     │  │         │  │ 8 Modules      │  │         │  │ 20+ Tables│  │
│  │ - Dashboard    │  │         │  │ - auth         │  │         │  │ - Users   │  │
│  │ - Controls     │  │         │  │ - controls     │  │         │  │ - Controls│  │
│  │ - Evidence     │  │         │  │ - evidence     │  │         │  │ - Evidence│  │
│  │                │  │         │  │ - reporting    │  │         │  │ - Logs    │  │
│  │ Bilingual i18n │  │         │  │ - privacy      │  │         │  │ - etc.    │  │
│  │ (ar/en)        │  │         │  │ - incident     │  │         │  │           │  │
│  │                │  │         │  │ - risk         │  │         │  └───────────┘  │
│  │ RTL/LTR Layout │  │         │  │ - ai_gov       │  │         │                 │
│  └────────────────┘  │         │  └────────────────┘  │         └─────────────────┘
│                      │         │                      │                 │
└──────────────────────┘         └──────────────────────┘                 │
         │                                │                                │
         │                                │                                │
         ▼                                ▼                                ▼
┌──────────────────────┐         ┌──────────────────────┐         ┌─────────────────┐
│                      │         │                      │         │                 │
│   CACHE LAYER        │         │   AI/RAG ENGINE      │         │  VECTOR DB      │
│   (Redis)            │         │   (LangChain)        │         │  (Chroma)       │
│   Port 6379          │         │                      │         │  Port 8001      │
│                      │         │  ┌────────────────┐  │         │                 │
│  ┌────────────────┐  │         │  │ Bilingual      │  │         │  ┌───────────┐  │
│  │ Session Cache  │  │         │  │ Retriever      │  │◄───────►│  │ Embeddings│  │
│  │ Query Cache    │  │         │  │                │  │         │  │ multilingual│ │
│  │ Rate Limiting  │  │         │  │ multilingual-  │  │         │  │ -e5-large  │  │
│  │ Token Lists    │  │         │  │ e5-large       │  │         │  │           │  │
│  └────────────────┘  │         │  │                │  │         │  │ Citations │  │
│                      │         │  │ Citation       │  │         │  │ Metadata  │  │
└──────────────────────┘         │  │ Tracking       │  │         │  └───────────┘  │
                                 │  └────────────────┘  │         │                 │
                                 │                      │         └─────────────────┘
                                 └──────────────────────┘
```

---

## Component Interaction Flow

### 1. User Authentication Flow

```
┌──────┐                                                           ┌──────────┐
│ User │                                                           │ Database │
└──┬───┘                                                           └────┬─────┘
   │                                                                    │
   │  1. POST /auth/login                                              │
   ├──────────────────────────────────────────────┐                    │
   │                                               ▼                    │
   │                                    ┌──────────────────┐            │
   │                                    │  Auth Router     │            │
   │                                    │  (FastAPI)       │            │
   │                                    └────────┬─────────┘            │
   │                                             │                      │
   │                                             │ 2. Query user        │
   │                                             ├─────────────────────►│
   │                                             │                      │
   │                                             │ 3. User data         │
   │                                             │◄─────────────────────┤
   │                                             │                      │
   │                         4. Verify password  │                      │
   │                         (bcrypt)            │                      │
   │                         ┌───────────────────┘                      │
   │                         │                                          │
   │                         │ 5. Generate JWT                          │
   │                         │    (HS256, 30min)                        │
   │                         │                                          │
   │                         │ 6. Create refresh token                  │
   │                         │    (7 days)                              │
   │                         │                                          │
   │                         │ 7. Store refresh token                   │
   │                         └─────────────────────────────────────────►│
   │                                             │                      │
   │  8. Return tokens                           │                      │
   │◄────────────────────────────────────────────┤                      │
   │  {access_token, refresh_token}              │                      │
   │                                             │                      │
   │  9. Store in localStorage                   │                      │
   │                                             │                      │
   │  10. Future requests with                   │                      │
   │      Authorization: Bearer {token}          │                      │
   └─────────────────────────────────────────────┘                      │
                                                                        │
```

### 2. Control Query Flow

```
┌──────────┐       ┌──────────┐       ┌─────────────┐       ┌──────────┐
│ Frontend │       │ Backend  │       │  Database   │       │ Cache    │
└────┬─────┘       └────┬─────┘       └──────┬──────┘       └────┬─────┘
     │                  │                     │                   │
     │ GET /controls    │                     │                   │
     │ ?framework=ECC   │                     │                   │
     ├─────────────────►│                     │                   │
     │                  │                     │                   │
     │                  │ Check cache         │                   │
     │                  ├────────────────────────────────────────►│
     │                  │                     │                   │
     │                  │◄────────────────────────────────────────┤
     │                  │ Cache miss          │                   │
     │                  │                     │                   │
     │                  │ Query controls      │                   │
     │                  ├────────────────────►│                   │
     │                  │ WHERE framework=ECC │                   │
     │                  │                     │                   │
     │                  │◄────────────────────┤                   │
     │                  │ Controls list       │                   │
     │                  │                     │                   │
     │                  │ Cache result        │                   │
     │                  ├────────────────────────────────────────►│
     │                  │                     │                   │
     │◄─────────────────┤                     │                   │
     │ JSON response    │                     │                   │
     │                  │                     │                   │
     │ Render UI        │                     │                   │
     │ (bilingual)      │                     │                   │
     └──────────────────┴─────────────────────┴───────────────────┘
```

### 3. AI/RAG Query Flow

```
┌────────┐     ┌─────────┐     ┌──────────────┐     ┌──────────┐     ┌──────────┐
│ User   │     │ Backend │     │ RAG Engine   │     │ Chroma   │     │ Database │
└───┬────┘     └────┬────┘     └──────┬───────┘     └────┬─────┘     └────┬─────┘
    │               │                 │                   │                │
    │ "ما هي       │                 │                   │                │
    │ متطلبات      │                 │                   │                │
    │ الحوكمة؟"    │                 │                   │                │
    ├──────────────►│                 │                   │                │
    │ POST /ai/query│                 │                   │                │
    │ language=ar   │                 │                   │                │
    │               │                 │                   │                │
    │               │ Call retriever  │                   │                │
    │               ├────────────────►│                   │                │
    │               │                 │                   │                │
    │               │                 │ Generate embedding│                │
    │               │                 │ (multilingual-e5) │                │
    │               │                 │                   │                │
    │               │                 │ Search vectors    │                │
    │               │                 ├──────────────────►│                │
    │               │                 │ similarity_search │                │
    │               │                 │                   │                │
    │               │                 │◄──────────────────┤                │
    │               │                 │ Top-k results     │                │
    │               │                 │ with scores       │                │
    │               │                 │                   │                │
    │               │                 │ Get full control  │                │
    │               │                 │ data              │                │
    │               │                 ├───────────────────────────────────►│
    │               │                 │                   │                │
    │               │                 │◄───────────────────────────────────┤
    │               │                 │ Control details   │                │
    │               │                 │                   │                │
    │               │◄────────────────┤                   │                │
    │               │ Results with    │                   │                │
    │               │ citations       │                   │                │
    │               │                 │                   │                │
    │◄──────────────┤                 │                   │                │
    │ JSON response │                 │                   │                │
    │ [              │                 │                   │                │
    │   {            │                 │                   │                │
    │     control_id │                 │                   │                │
    │     title_ar   │                 │                   │                │
    │     score: 0.87│                 │                   │                │
    │     source     │                 │                   │                │
    │   }            │                 │                   │                │
    │ ]              │                 │                   │                │
    └────────────────┴─────────────────┴───────────────────┴────────────────┘
```

---

## Backend Module Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    FASTAPI APPLICATION                           │
│                         (main.py)                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Registers Routers
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  CORE LAYER   │     │ MODULE LAYER  │     │  DATA LAYER   │
├───────────────┤     ├───────────────┤     ├───────────────┤
│               │     │               │     │               │
│ ┌───────────┐ │     │ ┌───────────┐ │     │ ┌───────────┐ │
│ │ database  │ │     │ │   auth    │ │     │ │PostgreSQL │ │
│ │ config    │ │     │ │ controls  │ │     │ │  Tables   │ │
│ │encryption │ │     │ │ evidence  │ │     │ │           │ │
│ │ security  │ │     │ │ reporting │ │     │ │ - users   │ │
│ │   tls     │ │     │ │  privacy  │ │     │ │ - controls│ │
│ │validation │ │     │ │ incident  │ │     │ │ - evidence│ │
│ │  types    │ │     │ │   risk    │ │     │ │ - logs    │ │
│ └───────────┘ │     │ │  ai_gov   │ │     │ │ - consent │ │
│               │     │ └───────────┘ │     │ │ - dsar    │ │
│ Infrastructure│     │               │     │ │ - incident│ │
│   Services    │     │ Each Module:  │     │ │ - risk    │ │
│               │     │ - models.py   │     │ │ - ai_model│ │
│               │     │ - schemas.py  │     │ └───────────┘ │
│               │     │ - router.py   │     │               │
│               │     │               │     │ Async ORM     │
│               │     │ API Endpoints │     │ SQLAlchemy 2.0│
└───────────────┘     └───────────────┘     └───────────────┘
        │                     │                     │
        └─────────────────────┴─────────────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │  SECURITY LAYER   │
                    ├───────────────────┤
                    │ - JWT Auth        │
                    │ - RBAC (5 roles)  │
                    │ - Rate Limiting   │
                    │ - Audit Logging   │
                    │ - Encryption      │
                    │ - Input Validation│
                    └───────────────────┘
```

---

## Frontend Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   NEXT.JS 14 APPLICATION                         │
│                      (App Router)                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │
        ┌─────────────────────┴─────────────────────┐
        │                                           │
        ▼                                           ▼
┌───────────────────┐                    ┌───────────────────┐
│   LAYOUT LAYER    │                    │   PAGE LAYER      │
├───────────────────┤                    ├───────────────────┤
│                   │                    │                   │
│ app/layout.tsx    │                    │ [locale]/         │
│ - Root layout     │                    │ ┌─────────────┐   │
│ - Fonts           │                    │ │ page.tsx    │   │
│   (Inter, Cairo)  │                    │ │  (Home)     │   │
│                   │                    │ └─────────────┘   │
│                   │                    │                   │
│ [locale]/         │                    │ dashboard/        │
│   layout.tsx      │                    │ ┌─────────────┐   │
│ - Locale provider │                    │ │ page.tsx    │   │
│ - Navigation      │                    │ │ (Dashboard) │   │
│ - RTL/LTR         │                    │ └─────────────┘   │
│ - Language toggle │                    │                   │
│                   │                    │ controls/         │
└───────────────────┘                    │ ┌─────────────┐   │
                                         │ │ page.tsx    │   │
                                         │ │ (Controls)  │   │
                                         │ └─────────────┘   │
                                         │                   │
                                         └───────────────────┘
        │                                           │
        └─────────────────────┬─────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────────┐
        │                                             │
        ▼                                             ▼
┌───────────────────┐                    ┌───────────────────┐
│   i18n LAYER      │                    │   API LAYER       │
├───────────────────┤                    ├───────────────────┤
│                   │                    │                   │
│ messages/         │                    │ lib/              │
│ ┌─────────────┐   │                    │ ┌─────────────┐   │
│ │ ar.json     │   │                    │ │api-client.ts│   │
│ │  (Arabic)   │   │                    │ │             │   │
│ └─────────────┘   │                    │ │ Axios       │   │
│                   │                    │ │ instance    │   │
│ ┌─────────────┐   │                    │ │             │   │
│ │ en.json     │   │                    │ │ - Base URL  │   │
│ │  (English)  │   │                    │ │ - Auth      │   │
│ └─────────────┘   │                    │ │ - Error     │   │
│                   │                    │ │   handling  │   │
│ next-intl         │                    │ └─────────────┘   │
│ ┌─────────────┐   │                    │                   │
│ │useTranslations│ │                    │ SWR for caching   │
│ └─────────────┘   │                    │                   │
└───────────────────┘                    └───────────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │   UI LAYER        │
                    ├───────────────────┤
                    │ - Tailwind CSS    │
                    │ - Radix UI        │
                    │ - Lucide Icons    │
                    │ - Recharts        │
                    │ - Custom Comps    │
                    └───────────────────┘
```

---

## Database Schema Relationships

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│    User     │────┐    │    Role     │────┐    │ Permission  │
├─────────────┤    │    ├─────────────┤    │    ├─────────────┤
│ id (PK)     │    │    │ id (PK)     │    │    │ id (PK)     │
│ email       │    │    │ name        │    │    │ resource    │
│ password_   │    │    │ description │    │    │ action      │
│   hash      │    │    └─────────────┘    │    └─────────────┘
│ full_name   │    │           │           │           │
│ is_active   │    │           │           │           │
│ roles ───────────┼───────────┘           │           │
└─────────────┘    │                       │           │
       │           │                       │           │
       │           └───────────────────────┼───────────┘
       │                Many-to-Many       │
       │                                   │
       │                                   │
       │           ┌─────────────┐         │
       │           │  AuditLog   │         │
       │           ├─────────────┤         │
       └──────────►│ id (PK)     │         │
                   │ user_id (FK)│         │
                   │ action      │         │
                   │ timestamp   │         │
                   │ ip_address  │         │
                   └─────────────┘         │
                                           │
┌─────────────┐         ┌─────────────┐   │
│   Control   │────┐    │  Evidence   │   │
├─────────────┤    │    ├─────────────┤   │
│ id (PK)     │    │    │ id (PK)     │   │
│ control_id  │    └───►│ control_id  │   │
│ framework   │         │   (FK)      │   │
│ title_en    │         │ title_en    │   │
│ title_ar    │         │ title_ar    │   │
│ status      │         │ file_path   │   │
│ priority    │         │ file_hash   │   │
│ maturity    │         │ validation  │   │
└─────────────┘         │   _status   │   │
       │                │ uploaded_by ├───┘
       │                │   (FK)      │
       │                └─────────────┘
       │
       │                ┌─────────────┐
       │                │   Report    │
       │                ├─────────────┤
       └───────────────►│ id (PK)     │
         Related        │ report_type │
         Controls       │ report_data │
                        │ generated_  │
                        │   by (FK)   │
                        └─────────────┘

┌─────────────┐         ┌─────────────┐
│   Consent   │         │    DSAR     │
├─────────────┤         ├─────────────┤
│ id (PK)     │         │ id (PK)     │
│ data_       │         │ request_    │
│   subject_id│         │   type      │
│ consent_    │         │ data_       │
│   type      │         │   subject_id│
│ consent_    │         │ status      │
│   given     │         │ request_    │
│ consent_    │         │   date      │
│   date      │         │ response_   │
└─────────────┘         │   date      │
                        └─────────────┘

┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│ Security    │         │    Risk     │         │  AIModel    │
│  Incident   │         ├─────────────┤         ├─────────────┤
├─────────────┤         │ id (PK)     │         │ id (PK)     │
│ id (PK)     │         │ risk_id     │         │ model_id    │
│ incident_id │         │ category    │         │ model_name  │
│ severity    │         │ likelihood  │         │ model_type  │
│ category    │         │ impact      │         │ use_case    │
│ status      │         │ risk_score  │         │ development │
│ detection_  │         │ treatment_  │         │   _status   │
│   date      │         │   strategy  │         │ bias_       │
│ resolution_ │         │ status      │         │   testing   │
│   date      │         └─────────────┘         └─────────────┘
└─────────────┘
```

---

## Security Architecture Layers

```
┌───────────────────────────────────────────────────────────────────┐
│                    7 LAYERS OF SECURITY                            │
└───────────────────────────────────────────────────────────────────┘

Layer 7: AUDIT LOGGING
┌─────────────────────────────────────────────────────────────────┐
│ - 7-year retention (NCA requirement)                             │
│ - User actions, system events                                    │
│ - Immutable logs in PostgreSQL                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
Layer 6: DATA ENCRYPTION
┌─────────────────────────────────────────────────────────────────┐
│ - Field-level encryption (Fernet AES-256)                        │
│ - Azure Key Vault integration                                    │
│ - PII protection (PDPL Article 29)                               │
└─────────────────────────────────────────────────────────────────┘
                              │
Layer 5: INPUT VALIDATION
┌─────────────────────────────────────────────────────────────────┐
│ - Pydantic schemas                                               │
│ - SQL injection prevention                                       │
│ - XSS attack prevention                                          │
└─────────────────────────────────────────────────────────────────┘
                              │
Layer 4: AUTHORIZATION (RBAC)
┌─────────────────────────────────────────────────────────────────┐
│ - 5 roles: Admin, Compliance Officer, Auditor, Analyst, Viewer  │
│ - Granular permissions per resource                              │
│ - Least privilege principle                                      │
└─────────────────────────────────────────────────────────────────┘
                              │
Layer 3: AUTHENTICATION
┌─────────────────────────────────────────────────────────────────┐
│ - JWT tokens (HS256, 30-min expiry)                             │
│ - bcrypt password hashing                                        │
│ - Account lockout (5 attempts = 30 min)                          │
│ - Token whitelist/blacklist                                      │
└─────────────────────────────────────────────────────────────────┘
                              │
Layer 2: APPLICATION SECURITY
┌─────────────────────────────────────────────────────────────────┐
│ - OWASP Security Headers                                         │
│   • X-Content-Type-Options: nosniff                              │
│   • X-Frame-Options: DENY                                        │
│   • Content-Security-Policy                                      │
│   • Strict-Transport-Security                                    │
│ - CORS whitelist                                                 │
│ - Rate limiting (60/min, 1000/hour)                              │
└─────────────────────────────────────────────────────────────────┘
                              │
Layer 1: NETWORK SECURITY
┌─────────────────────────────────────────────────────────────────┐
│ - TLS 1.3 encryption                                             │
│ - HTTPS enforcement (production)                                 │
│ - Certificate management                                         │
│ - Secure database connections                                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow: Evidence Upload

```
┌──────┐   1. Upload File   ┌──────────┐   2. Validate   ┌──────────┐
│ User │──────────────────►│ Frontend │────────────────►│ Backend  │
└──────┘                    └──────────┘                 └────┬─────┘
                                                              │
                                        3. Check JWT          │
                                        ┌─────────────────────┘
                                        │
                                        │ 4. Verify RBAC
                                        │    (Analyst or above)
                                        │
                                        ▼
                            ┌────────────────────────┐
                            │  Evidence Router       │
                            │  /api/v1/evidence     │
                            └───────────┬────────────┘
                                        │
                            5. Generate │ SHA-256 hash
                                        │
                                        │ 6. Store file
                                        ▼
                            ┌────────────────────────┐
                            │  File System           │
                            │  /uploads/evidence/    │
                            └────────────────────────┘
                                        │
                            7. Create   │ evidence record
                                        ▼
                            ┌────────────────────────┐
                            │  PostgreSQL            │
                            │  evidence table        │
                            │  - control_id (FK)     │
                            │  - file_path           │
                            │  - file_hash           │
                            │  - uploaded_by (FK)    │
                            │  - validation_status   │
                            └────────────────────────┘
                                        │
                            8. Log      │ action
                                        ▼
                            ┌────────────────────────┐
                            │  AuditLog table        │
                            │  - user_id             │
                            │  - action: "upload"    │
                            │  - resource: evidence  │
                            │  - timestamp           │
                            │  - ip_address          │
                            └────────────────────────┘
                                        │
                            9. Return   │ success
                                        ▼
                            ┌────────────────────────┐
                            │  Response              │
                            │  {                     │
                            │    id: uuid,           │
                            │    status: "pending"   │
                            │  }                     │
                            └────────────────────────┘
```

---

## Deployment Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    DOCKER COMPOSE ENVIRONMENT                     │
└──────────────────────────────────────────────────────────────────┘

                    ┌────────────────────┐
                    │ Docker Compose     │
                    │ (docker-compose.yml)│
                    └──────────┬─────────┘
                               │
                               │ Orchestrates 5 Services
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│   frontend    │      │    backend    │      │   postgres    │
│               │      │               │      │               │
│ Next.js 14    │      │ FastAPI       │      │ PostgreSQL 15 │
│ Port: 3000    │      │ Port: 8000    │      │ Port: 5432    │
│               │      │               │      │               │
│ Volume:       │      │ Volume:       │      │ Volume:       │
│ - app code    │      │ - app code    │      │ - data/       │
│ - node_modules│      │ - data/       │      │               │
└───────────────┘      └───────────────┘      └───────────────┘
        │                      │                      │
        └──────────────────────┴──────────────────────┘
                               │
                    Shared Network: sico_network
                               │
        ┌──────────────────────┴──────────────────────┐
        │                                             │
        ▼                                             ▼
┌───────────────┐                            ┌───────────────┐
│    redis      │                            │    chroma     │
│               │                            │               │
│ Redis 7       │                            │ Chroma DB     │
│ Port: 6379    │                            │ Port: 8001    │
│               │                            │               │
│ Volume:       │                            │ Volume:       │
│ - data/       │                            │ - chroma/     │
└───────────────┘                            └───────────────┘
```

---

## Compliance Framework Mapping

```
┌────────────────────────────────────────────────────────────────────┐
│                      COMPLIANCE FRAMEWORKS                          │
│                         (92% Overall)                               │
└────────────────────────────────────────────────────────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│   NCA ECC     │         │   NCA CCC     │         │    PDPL       │
│   (95%)       │         │   (92%)       │         │    (90%)      │
├───────────────┤         ├───────────────┤         ├───────────────┤
│               │         │               │         │               │
│ ✅ ECC-GV     │         │ ✅ CCC-GOV    │         │ ✅ Art 6-9    │
│   Governance  │         │   Governance  │         │   Consent     │
│               │         │               │         │               │
│ ✅ ECC-IS     │         │ ✅ CCC-SEC    │         │ ✅ Art 12-17  │
│   InfoSec     │         │   Security    │         │   DSAR        │
│   - IS-3 Auth │         │   - SEC-01    │         │               │
│   - IS-5 Logs │         │     Encryption│         │ ✅ Art 27     │
│               │         │   - SEC-04    │         │   Breach      │
│ ✅ ECC-RM     │         │     Logging   │         │   Notification│
│   Risk Mgmt   │         │               │         │               │
│               │         │ ✅ CCC-IAM    │         │ ✅ Art 29     │
│ ✅ ECC-TP     │         │   Identity &  │         │   Security    │
│   Third Party │         │   Access      │         │   Measures    │
│               │         │               │         │               │
└───────────────┘         └───────────────┘         └───────────────┘
        │                         │                         │
        └─────────────────────────┼─────────────────────────┘
                                  │
        ┌─────────────────────────┴─────────────────────────┐
        │                                                   │
        ▼                                                   ▼
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│  SDAIA AI     │         │  ISO 27001    │         │  NIST CSF 2.0 │
│   (85%)       │         │   (93%)       │         │    (90%)      │
├───────────────┤         ├───────────────┤         ├───────────────┤
│               │         │               │         │               │
│ ✅ Model      │         │ ✅ A.5        │         │ ✅ IDENTIFY   │
│   Registry    │         │   Info Sec    │         │   Asset Mgmt  │
│               │         │   Policies    │         │               │
│ ✅ Bias       │         │               │         │ ✅ PROTECT    │
│   Testing     │         │ ✅ A.9        │         │   Access      │
│               │         │   Access      │         │   Control     │
│ ✅ Ethics     │         │   Control     │         │               │
│   Docs        │         │               │         │ ✅ DETECT     │
│               │         │ ✅ A.12       │         │   Monitoring  │
│ ✅ Governance │         │   Operations  │         │               │
│   Framework   │         │   Security    │         │ ✅ RESPOND    │
│               │         │               │         │   Incident    │
│               │         │ ✅ A.16       │         │   Response    │
│               │         │   Incident    │         │               │
│               │         │   Management  │         │ ✅ RECOVER    │
│               │         │               │         │   Backup &    │
│               │         │ ✅ A.18       │         │   Recovery    │
│               │         │   Compliance  │         │               │
└───────────────┘         └───────────────┘         └───────────────┘
```

---

**Visual Architecture Guide Version**: 1.0  
**Last Updated**: 2026-02-08  
**Platform Status**: Production Ready (92% Compliance) ✅
