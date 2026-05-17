# Sanadcom GRC Platform — One-Page Product Overview

**Version 1.0 | May 2026 | Confidential**

---

## What is Sanadcom?

Sanadcom is an **enterprise-grade, open-architecture Governance, Risk & Compliance (GRC) platform** that unifies compliance management, risk assessment, evidence collection, and audit reporting into a single system — supporting 108+ international standards including Saudi ECC, SAMA, ISO 27001, NIST CSF, GDPR, and DORA.

---

## The Problem We Solve

| Current Reality | With Sanadcom |
|----------------|--------------|
| Spreadsheets for risk registers | Structured risk register with heat map visualization |
| Separate tools for each framework | One platform, all frameworks, shared controls |
| Manual evidence collection | Automated expiry tracking and version history |
| Inconsistent audit reports | One-click PDF compliance reports |
| Siloed teams with no shared view | Role-based multi-tenant access for all stakeholders |
| English-only tools in Arabic-speaking organizations | Full Arabic/English bilingual UI with RTL support |

---

## Who Is It For?

| Persona | Use Case |
|---------|---------|
| **CISO / Head of Cybersecurity** | Unified risk and compliance posture dashboard |
| **Compliance Manager** | Multi-framework compliance assessments and SoA |
| **Risk Analyst** | Risk register, EBIOS RM, quantitative risk studies |
| **Auditor (Internal / External)** | Evidence review, audit trail, PDF reports |
| **Privacy Officer (DPO)** | GDPR ROPA, data subject requests, breach tracking |
| **Procurement / TPRM Team** | Vendor risk assessments and due diligence |

---

## Core Capabilities at a Glance

```
┌─────────────────────────────────────────────────────────────┐
│                   SANADCOM GRC PLATFORM                      │
│                                                              │
│  📋 COMPLIANCE      🎯 RISK          📁 EVIDENCE             │
│  108+ Frameworks    Qualitative      Versioned files         │
│  Cross-framework    Quantitative     Expiry tracking         │
│  control reuse      EBIOS RM         Chain of custody        │
│                                                              │
│  🏢 GOVERNANCE      🤝 TPRM          🔒 PRIVACY              │
│  Folder-based       Vendor register  GDPR ROPA               │
│  multi-tenancy      Due diligence    Breach management       │
│  RBAC + SSO/MFA     Contracts        Right requests          │
│                                                              │
│  📊 REPORTING       🔗 INTEGRATIONS  🌍 BILINGUAL            │
│  PDF reports        Jira, Kafka      Arabic (RTL)            │
│  Dashboards         Webhooks         + 21 other languages    │
│  API / CLI          Prefect, n8n     Saudi ECC/SAMA          │
└─────────────────────────────────────────────────────────────┘
```

---

## Technology Snapshot

| Layer | Technology |
|-------|-----------|
| Backend | Django 6.0.3 + Django REST Framework |
| Frontend | SvelteKit 2 + Svelte 5 |
| Database | PostgreSQL 16 |
| Deployment | Docker Compose / Kubernetes (Helm) |
| Auth | Knox + JWT + SAML/OIDC + MFA (TOTP + FIDO2) |
| API | OpenAPI 3.0 (Swagger / ReDoc) |

---

## Key Differentiators

1. **Widest framework library:** 108+ standards including Saudi ECC, SAMA, OTCC — no competitor matches MENA coverage.
2. **True control decoupling:** One implemented control satisfies requirements across multiple frameworks — no duplicate work.
3. **Full EBIOS RM:** Only commercial platform with complete EBIOS Risk Manager implementation.
4. **Self-hostable:** On-premises deployment for data sovereignty requirements.
5. **Arabic-first:** Not translated — built bilingual from the ground up with full RTL support.
6. **API-first + automation:** CLI (CLICA), MCP/LLM integration, Kafka ingestion, webhook events.

---

## Current Status

| Milestone | Status |
|-----------|--------|
| Core GRC Engine | ✅ Complete |
| 108+ Frameworks | ✅ Complete |
| Multi-tenant RBAC | ✅ Complete |
| Authentication (SSO + MFA) | ✅ Complete |
| Evidence Management | ✅ Complete |
| Bilingual Arabic/English | ✅ Complete |
| Docker Deployment | ✅ Complete |
| Kubernetes (Helm) | ✅ Charts ready |
| CI/CD Pipeline | 🔶 In progress |
| Production Go-Live | 🔶 Planned |

---

## Contact & Next Steps

To proceed:
1. Sign NDA (template provided)
2. Request sandbox access or repository read access
3. Schedule a technical walkthrough or demo call

**Contact:** [Insert team contact details]  
**Repository:** github.com/sonaiso/sanadcom (NDA required for access)  
**Documentation:** Available in `documentation/` directory

---

*Sanadcom GRC Platform — Built for the MENA region. Ready for the world.*
