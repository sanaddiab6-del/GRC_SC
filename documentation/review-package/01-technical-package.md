# Sanadcom GRC Platform — Technical Review Package

**Prepared for:** Technical / Developer Reviewer  
**Prepared by:** Sanadcom Engineering Team  
**Classification:** Confidential — Shared Under NDA  
**Date:** May 2026  
**Revision:** 1.0

---

## 1. System Architecture

### 1.1 High-Level Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                             │
│                                                                  │
│  ┌─────────────────┐   ┌─────────────┐   ┌────────────────────┐ │
│  │  SvelteKit Web  │   │  CLI (CLICA)│   │ External Systems   │ │
│  │  Application    │   │  + MCP/LLM  │   │ (Kafka/API/Webhook)│ │
│  │  (Port 3000)    │   │             │   │                    │ │
│  └────────┬────────┘   └──────┬──────┘   └─────────┬──────────┘ │
└───────────┼──────────────────┼────────────────────┼────────────┘
            │                  │                    │
     ┌──────▼──────────────────▼────────────────────▼──────┐
     │              CADDY REVERSE PROXY                     │
     │       Auto-HTTPS / TLS Termination / HTTP/2          │
     │              Route: / → Frontend                     │
     │              Route: /api → Backend                   │
     └──────────────────────┬───────────────────────────────┘
                            │
            ┌───────────────┴────────────────┐
            │                                │
   ┌────────▼──────────┐          ┌──────────▼──────────┐
   │  SvelteKit Frontend│          │  Django + DRF API   │
   │  SSR / SPA         │◄────────►│  Backend (Port 8000) │
   │  Paraglide i18n    │  REST    │  22 Django Apps      │
   │  22 Languages/RTL  │  API     │  OpenAPI 3.0 Docs    │
   └────────────────────┘          └──────────┬──────────┘
                                              │
                    ┌─────────────────────────┼────────────────────┐
                    │                         │                    │
           ┌────────▼──────┐        ┌─────────▼──────┐   ┌────────▼───────┐
           │  Huey Task    │        │   PostgreSQL 16  │   │  S3 / Local   │
           │  Queue Worker │        │   (Primary DB)   │   │  File Storage │
           │  (2 workers)  │        │   50+ Models     │   │  (Evidence)   │
           └───────────────┘        └─────────────────┘   └───────────────┘
                    │
           ┌────────▼──────────────────────────────────┐
           │            EXTERNAL INTEGRATIONS           │
           │  Kafka Dispatcher │ Jira │ Prowler │ Prefect│
           └───────────────────────────────────────────┘
```

### 1.2 Data Flow — Compliance Assessment Lifecycle

```
[User] → [Frontend Form] → [API: POST /compliance-assessments/]
    → [Django View] → [Serializer Validation (DRF)]
    → [RBAC Permission Check (folder-scoped)]
    → [Database Write (PostgreSQL)]
    → [Audit Log Entry (django-auditlog)]
    → [Huey Task: deadline-reminder-scheduled]
    → [API Response 201 + JSON]
    → [Frontend State Update]
    → [PDF Report via WeasyPrint (on-demand)]
```

### 1.3 Authentication Flow

```
[Login Request]
    │
    ├─ Standard Login → Knox Token (TTL: 60min, max: 10hr) + CSRF Cookie
    ├─ API Access    → JWT Access (15min) + JWT Refresh (7 days, rotating)
    ├─ SSO (SAML)    → Allauth SAML2 → Knox session bridge
    ├─ SSO (OIDC)    → Allauth OIDC → Knox session bridge
    └─ Automation    → Personal Access Token (PAT) → M2M API calls

[Authorization Check on every request]
    └─ RBACPermissions → folder membership → role lookup → permission grant/deny
```

### 1.4 Multi-Tenancy Model

```
[Global Folder (root)]
    └── [Business Unit A Folder]
    │       └── [Project Folder A1]
    │       └── [Project Folder A2]
    └── [Business Unit B Folder]
            └── [Project Folder B1]

Every object (Assessment, Evidence, Control, etc.) belongs to exactly one Folder.
Permissions are assigned via RoleAssignment(User, Role, Folder).
Users only see objects in folders where they have an active RoleAssignment.
```

---

## 2. Technology Stack

### 2.1 Core Stack

| Layer | Technology | Version | Rationale |
|-------|-----------|---------|-----------|
| **Backend Framework** | Django + Django REST Framework | 6.0.3 / 3.16.1 | Mature ORM, admin, security defaults, DRF for API |
| **Frontend Framework** | SvelteKit + Svelte 5 | 2.52 / 5.53 | Superior runtime performance vs React; SSR/SSG; smaller bundles |
| **Build Tooling** | Vite + TypeScript | 5.4 / 5.8 | Fast HMR, tree-shaking, strong typing |
| **UI Styling** | Tailwind CSS v4 + Skeleton UI | 4.1 | Utility-first, consistent design system |
| **Database** | PostgreSQL | 16 | ACID, JSONB, full-text search, replication |
| **Task Queue** | Huey (SQLite-backed) | 2.5.5 | Lightweight; Redis migration planned for scale |
| **Reverse Proxy** | Caddy | 2.10 | Auto-HTTPS, HTTP/2, minimal config |
| **I18n** | Paraglide-JS | 2.1 | Compile-time translation, zero runtime overhead, 22 languages |

### 2.2 Authentication & Security Stack

| Component | Technology | Details |
|-----------|-----------|---------|
| Session auth | Knox | Stateful tokens, configurable TTL, revocable |
| API auth | SimpleJWT | 15-min access, 7-day refresh, rotation + blacklist |
| SSO | django-allauth (SAML 2.0 + OIDC) | Federation with enterprise IdPs |
| MFA | TOTP + FIDO2/WebAuthn | Authenticator apps + hardware keys |
| Authorization | Custom RBAC | Folder-scoped, per-object, role-based permissions |
| Audit | django-auditlog | All model changes with user/timestamp context |
| XSS | sanitize-html (frontend) + Django auto-escape | Defense in depth |
| CSRF | Cookie-based, SameSite=Strict | Django CSRF middleware |
| File validation | python-magic | Content-type detection on upload |

### 2.3 Infrastructure & DevOps Stack

| Component | Technology | Notes |
|-----------|-----------|-------|
| Containerization | Docker + Docker Compose | Multi-service stack |
| Orchestration | Kubernetes (Helm Charts) | `ciso-assistant` + `ciso-assistant-next` charts |
| Event Streaming | Apache Kafka (Dispatcher) | Compliance data ingestion from external tools |
| Workflow Automation | Prefect 3.4.5+ / n8n | Scheduled compliance workflows |
| Monitoring | Prometheus | Metrics endpoint at `/metrics` |
| API Documentation | drf-spectacular (OpenAPI 3.0) | Swagger UI + ReDoc |
| PDF Reports | WeasyPrint 68.0 | Server-side PDF generation |
| E2E Testing | Playwright 1.55 | Browser automation tests |
| Backend Testing | pytest-django | 21 test modules, async client |
| Frontend Testing | Vitest | Unit/component tests |
| Code Quality | ruff (Python) + eslint/prettier (JS) | Lint + format enforcement |

---

## 3. Threat Model & Security Self-Assessment

### 3.1 Attack Surface Overview

| Surface | Exposure | Controls |
|---------|----------|---------|
| Web UI (Port 443 via Caddy) | Public-facing | TLS, CSRF, XSS sanitization, auth required |
| REST API (/api/*) | Public-facing | JWT/Knox auth, RBAC, DRF throttling |
| Django Admin (/admin/) | Internal | Superuser only, IP restrict recommended |
| PostgreSQL | Internal only | Not exposed externally; Docker network |
| Huey workers | Internal only | No direct exposure |
| S3 storage | Cloud-scoped | IAM-restricted bucket policies |
| Kafka dispatcher | Internal | Topic-authenticated |

### 3.2 OWASP Top 10 Mapping

| OWASP Risk | Status | Implementation |
|------------|--------|----------------|
| **A01 Broken Access Control** | ✅ Mitigated | Folder-scoped RBAC; per-object permission checks on every endpoint; `RBACPermissions` class enforced on all ViewSets |
| **A02 Cryptographic Failures** | ✅ Mitigated | TLS via Caddy auto-HTTPS; passwords hashed with Argon2 (Django default); JWT signed with RS256 |
| **A03 Injection** | ✅ Mitigated | Django ORM parameterized queries; no raw SQL; DRF serializer validation at API boundary |
| **A04 Insecure Design** | ✅ Mitigated | Decoupled auth/authz; multi-layered token system; validation workflows prevent unauthorized state changes |
| **A05 Security Misconfiguration** | ⚠️ Partial | `DEBUG=False` in production Docker images; secret management via env vars (migration to Vault planned); admin path should be renamed |
| **A06 Vulnerable Components** | ⚠️ Monitor | 40+ Python + 50+ npm packages; Dependabot/Snyk scanning planned; last Bandit scan passed |
| **A07 Auth Failures** | ✅ Mitigated | Knox token TTL; JWT rotation + blacklist; MFA available; account lockout configurable |
| **A08 Integrity Failures** | ✅ Mitigated | django-auditlog on all model changes; evidence versioning with `EvidenceRevision`; validation flows |
| **A09 Logging Failures** | ✅ Mitigated | structlog for structured logs; django-auditlog; Prometheus metrics; audit trail per user action |
| **A10 SSRF** | ✅ Mitigated | Webhook and external integration URLs validated; no arbitrary URL fetch from user input |

### 3.3 Data Classification

| Data Type | Classification | Storage | Protection |
|-----------|---------------|---------|-----------|
| User credentials | Confidential | PostgreSQL | Argon2 hash, never stored plaintext |
| Assessment data | Confidential | PostgreSQL | Folder-scoped access control |
| Evidence files | Confidential | Local/S3 | Access-controlled download URLs |
| Audit logs | Restricted | PostgreSQL | Read-only for non-admins |
| Framework libraries | Internal | PostgreSQL | Integrity-verified on load |
| API tokens | Secret | PostgreSQL | Hashed with SHA-256 (Knox) |

---

## 4. Known Limitations & Areas of Concern

We present these candidly to build trust and focus the review:

### 4.1 Not Yet Production-Ready (Active Work)

| Limitation | Severity | Mitigation Plan |
|-----------|----------|----------------|
| **CI/CD pipeline absent** — GitHub Actions workflows exist as stubs but are not active. Manual testing required before merges. | High | Restoring full pipeline is Milestone 6 priority |
| **Secret management via env vars** — Database passwords and `DJANGO_SECRET_KEY` are set in docker-compose environment blocks rather than a secrets vault. | High | Migration to Docker secrets / HashiCorp Vault planned |
| **Huey SQLite task queue** — SQLite-backed task broker unsuitable for >100 concurrent users under sustained load. | Medium | Redis migration planned for Milestone 8 |
| **No API rate limiting** — No request throttling currently enforced at the application layer (Caddy provides basic protection). | Medium | DRF throttling classes to be added |
| **No penetration test completed** — Self-assessed security; no third-party pentest has been performed yet. | Medium | Planned in Milestone 9 pre-go-live |

### 4.2 Architectural Trade-offs

| Trade-off | Decision | Reasoning |
|-----------|----------|-----------|
| Forked from open-source (CISO Assistant Community) | Accepted upstream divergence risk | Avoids rebuilding 200k+ lines of battle-tested GRC logic; 375 commits of customization on top |
| SvelteKit vs React | SvelteKit chosen | Better performance for data-heavy tables; smaller bundles; but smaller talent pool |
| Single PostgreSQL instance | No read replicas yet | Suitable for current scale; read replicas planned before high-concurrency deployment |
| WeasyPrint for PDF | CPU-intensive on same process | Offloading to Huey worker planned; current scale acceptable |

### 4.3 Test Coverage Gaps

- Backend test suite: 21 modules passing; coverage estimate ~60% (target: 80%).
- E2E Playwright tests: exist for core flows; not yet run in CI automatically.
- SSO flows (SAML/OIDC): integration tested manually; no automated IdP mock test.
- File upload edge cases: basic validation tested; adversarial content (malformed YAML, oversized files) partially covered.

---

## 5. Repository Access

| Resource | Details |
|---------|---------|
| **GitHub Repository** | `https://github.com/sonaiso/sanadcom` (request read access via NDA) |
| **Branch** | `main` (stable) |
| **Commits** | 375+ commits, 6 contributors |
| **API Docs** | `/api/schema/swagger-ui/` (on running instance) |
| **OpenAPI Spec** | `/api/schema/` → downloadable YAML |

---

## 6. Running the Platform for Review

### Option A: Docker Compose (Recommended)

```bash
git clone https://github.com/sonaiso/sanadcom.git
cd sanadcom
cp .env.example .env   # Configure DATABASE_URL, SECRET_KEY
docker compose up -d
# Access: http://localhost (via Caddy proxy)
```

### Option B: Development Stack

```bash
# Backend
cd backend && poetry install
python manage.py migrate
python manage.py runserver

# Frontend
cd frontend && pnpm install
pnpm dev
```

### Option C: Sandbox Demo Environment

A pre-configured sandbox is available. Contact the team for credentials.  
The sandbox uses a read-only copy of anonymized sample data with full feature access.

---

*Document prepared by Sanadcom Engineering — May 2026*  
*All information is confidential and shared under NDA.*
