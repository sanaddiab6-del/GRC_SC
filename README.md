# 🛡️ SICO GRC Platform

**Saudi Regulatory Compliance Engine**  
*ECC • CCC • PDPL - AI-Powered Bilingual Automation*

---

## 🎯 Overview

SICO GRC Platform is a comprehensive Governance, Risk, and Compliance (GRC) solution specifically designed for the Saudi Arabian regulatory landscape. It provides end-to-end compliance automation for:

- **ECC** (Essential Cybersecurity Controls)
- **CCC** (Cloud Cybersecurity Controls)
- **PDPL** (Personal Data Protection Law)

### Key Differentiators

✅ **Unified Regulatory Library** - Operational control sets with evidence requirements  
✅ **ECC↔CCC Baseline** - Eliminate 40-60% compliance duplication  
✅ **PDPL Registers** - RoPA, DSAR, Breach logs, Retention tracking  
✅ **Evidence Automation** - Master catalog with audit-ready templates  
✅ **SOC↔GRC Bridge** - Incident-to-compliance workflow integration  
✅ **Bilingual AI** - Arabic/English RAG with citation-based guardrails  
✅ **Executive Reporting** - Compliance heatmaps, risk dashboards, audit readiness  

---

## 📦 Project Structure

```
sanadcom/
├── docs/                    # Comprehensive documentation
│   ├── architecture/        # System architecture & design
│   ├── deliverables/        # 12 core deliverables
│   └── user-guides/         # User & admin guides
│
├── data/                    # Regulatory core assets
│   ├── controls/            # ECC/CCC/PDPL control libraries
│   ├── mappings/            # Cross-framework mappings
│   ├── evidence/            # Evidence catalog & templates
│   ├── audit/               # Test procedures
│   └── pdpl/                # PDPL registers
│
├── packs/                   # Ready-to-deploy compliance packs
│   ├── ecc-baseline/
│   ├── ccc-cloud/
│   └── pdpl-privacy/
│
├── reporting/               # Executive reporting engine
│   ├── templates/           # PowerPoint/Word/Excel templates
│   └── generators/          # Report generation scripts
│
├── soc-grc-bridge/          # SOC integration layer
│   ├── incident-control-matrix.yaml
│   └── playbooks/
│
├── ai/                      # AI/NLP engine
│   ├── knowledge-base/      # RAG knowledge base
│   ├── rag/                 # Retrieval & citation engine
│   ├── dictionary/          # Client dictionary engine
│   └── models/              # BERT adapters
│
├── playbooks/               # Delivery factory methodology
│   ├── onboarding/
│   ├── evidence-collection/
│   └── workshops/
│
├── src/                     # Application code
│   ├── backend/             # FastAPI backend
│   ├── frontend/            # Next.js frontend
│   └── shared/              # Shared utilities
│
├── scripts/                 # Automation scripts
├── tests/                   # Test suites
├── deployment/              # Docker & K8s configs
└── config/                  # Configuration files
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Docker & Docker Compose**
- **PostgreSQL 15+**
- **Redis**

### Installation

```bash
# Clone repository
git clone https://github.com/sonaiso/sanadcom.git
cd sanadcom

# Backend setup
cd src/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install

# Start services with Docker
docker-compose up -d
```

### Environment Configuration

```bash
cp config/env.example .env
# Edit .env with your configuration
```

---

## 🏗️ Technology Stack

### Backend
- **FastAPI** - Modern Python API framework
- **PostgreSQL** - Primary database
- **Chroma/Weaviate** - Vector database for RAG
- **Redis** - Caching layer
- **SQLAlchemy** - ORM
- **Alembic** - Database migrations

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **shadcn/ui** - Component library
- **React Query** - Data fetching & state management

### AI/NLP
- **LangChain** - RAG orchestration
- **Transformers** - Bilingual NLP models
- **Sentence Transformers** - Embeddings
- **Custom BERT Adapters** - Client-specific fine-tuning

### DevOps
- **Docker** - Containerization
- **GitHub Actions** - CI/CD
- **K8s-ready** - Kubernetes deployment templates

---

## 📋 12 Core Deliverables

### Regulatory Preparation (1-5)
1. **Saudi Control Library** - Unified ECC/CCC/PDPL operational controls
2. **ECC↔CCC Baseline** - Unified baseline + CCC delta pack
3. **PDPL Operational Controls** - Registers, policies, evidence
4. **Evidence Master Catalog** - Audit-ready evidence templates
5. **Audit Test Procedures** - Control verification steps

### Competitive Advantage (6-8)
6. **SICO Packs** - Pre-packaged compliance bundles
7. **Executive Reporting Kit** - C-level dashboards & reports
8. **SOC↔GRC Bridge** - Incident-compliance integration

### AI Engine (9-11)
9. **Bilingual Knowledge Base** - RAG with citation tracking
10. **Client Dictionary Engine** - Custom terminology mapping
11. **BERT Adapters** - Per-client model customization

### Operational Excellence (12)
12. **Delivery Factory Playbook** - Scalable delivery methodology

---

## 🎯 Use Cases

### For Organizations
- **Compliance Teams** - Automated evidence collection & gap analysis
- **CISOs** - Executive dashboards & audit readiness
- **SOC Teams** - Incident-to-compliance workflow
- **Privacy Officers** - PDPL register management

### For Consultants
- **Faster Delivery** - Pre-built packs reduce implementation time
- **Scalability** - Factory methodology for multi-client operations
- **Differentiation** - AI-powered automation + bilingual support

---

## 📊 Project Status

**Phase**: Foundation & Regulatory Preparation  
**Version**: 0.1.0-alpha  
**Last Updated**: February 2026

### Roadmap
- [ ] Phase 1: Regulatory Core (Controls, Mappings, Evidence) - **In Progress**
- [ ] Phase 2: Backend API & Database Schema
- [ ] Phase 3: AI/RAG Engine Implementation
- [ ] Phase 4: Frontend Dashboard
- [ ] Phase 5: SOC Integration & Reporting
- [ ] Phase 6: Beta Testing & Refinement

---

## 🤝 Contributing

This is a private project. For team members:

1. Create feature branches from `main`
2. Follow conventional commits
3. Submit PRs with detailed descriptions
4. Ensure tests pass before merging

---

## 📄 License

**Proprietary** - All rights reserved  
© 2026 SICO Security

---

## 📞 Contact

**Project Lead**: sonaiso  
**Repository**: https://github.com/sonaiso/sanadcom

---

## 🔐 Security

For security concerns, please contact the project lead directly.

**Do not** open public issues for security vulnerabilities.
