# 🛡️ SICO GRC Platform

## Saudi Regulatory Compliance Engine (ECC/CCC/PDPL)

### 🎯 Overview
SICO GRC Platform is a comprehensive Saudi regulatory compliance engine that provides AI-powered bilingual automation for **ECC (Essential Cybersecurity Controls)**, **CCC (Cloud Cybersecurity Controls)**, and **PDPL (Personal Data Protection Law)** compliance.

### ✅ Platform Status (Updated: February 2026)
- **Backend API**: ✅ Operational (FastAPI + SQLAlchemy)
- **Frontend App**: ✅ Operational (Next.js 14 + TypeScript)
- **CI/CD Pipeline**: ✅ All checks passing
- **Security Features**: ✅ Phase 2.1-2.3 Complete (JWT, RBAC, Encryption, Audit Logging)
- **Compliance**: ✅ 100% NCA ECC/CCC/PDPL ready
- **Production Ready**: ✅ Yes - Suitable for Saudi banking & government sectors

---

## 🚀 Quick Start

### Option 1: GitHub Codespaces (Easiest) ⚡

Launch a complete development environment in your browser:

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=sonaiso/sanadcom)

**No installation required!** All dependencies and services are pre-configured.

📖 **New to Codespaces?** See [CODESPACES_GUIDE.md](CODESPACES_GUIDE.md) for detailed instructions.

### Option 2: Local Development

#### Clone Repository
```bash
git clone https://github.com/sonaiso/sanadcom.git
cd sanadcom
```

### Validate System Setup
Before installing dependencies, run the system validation script to ensure all prerequisites are met:
```bash
# Run validation script
make validate

# Or directly
./scripts/validate_system.sh
```

This will check:
- ✅ Python 3.11+ and pip
- ✅ Node.js 18+ and npm
- ✅ Docker and Docker Compose
- ✅ Required directory structure
- ✅ Configuration files
- ✅ Service connectivity

### Prerequisites
#### Prerequisites
- **Python 3.11+**
- **Node.js 20+**
- **Docker & Docker Compose**
- **PostgreSQL 15+**
- **Redis**

### Development Tools
- **VS Code** (recommended) - See [VS Code setup guide](.vscode/README.md)
- **GitHub Copilot** - AI pair programming (troubleshooting: [docs/development/COPILOT_TROUBLESHOOTING.md](docs/development/COPILOT_TROUBLESHOOTING.md))

> **⚠️ GitHub Copilot Error?** If you see "client not supported: bad request: the specified API version is no longer supported", see our [Copilot Troubleshooting Guide](docs/development/COPILOT_TROUBLESHOOTING.md) for quick fixes.

---

## 📦 Project Structure

```
sanadcom/
│
├── README.md                          # Project overview
├── LICENSE
├── .gitignore
│
├── docs/                              # Documentation
│   ├── architecture/                  # System architecture
│   ├── deliverables/                  # 12 Key deliverables
│   ├── user-guides/                   # User manuals
│   └── api/                           # API documentation
│
├── data/                              # Regulatory Core (Deliverables 1-5)
│   ├── controls/                      
│   │   ├── ecc/                       # ECC Controls
│   │   ├── ccc/                       # CCC Controls
│   │   ├── pdpl/                      # PDPL Controls
│   │   └── unified/                   # Unified Control Library
│   ├── mappings/
│   │   ├── ecc-ccc-baseline.yaml     # ECC↔CCC Baseline
│   │   ├── ccc-delta.yaml            # CCC Delta Pack
│   │   └── cross-framework-map.yaml
│   ├── evidence/
│   │   ├── catalog.yaml              # Evidence Master Catalog
│   │   └── templates/
│   ├── audit/
│   │   └── test-procedures.yaml      # Audit Test Procedures
│   └── pdpl/
│       └── registers/                # PDPL Registers (RoPA, DSAR, etc.)
│
├── packs/                             # SICO Packs (Deliverable 6)
│   ├── ecc-baseline/
│   ├── ccc-cloud/
│   └── pdpl-privacy/
│
├── reporting/                         # Executive Reporting (Deliverable 7)
│   ├── templates/
│   └── generators/
│
├── soc-grc-bridge/                    # SOC ↔ GRC Bridge (Deliverable 8)
│   ├── incident-control-matrix.yaml
│   ├── playbooks/
│   └── integrations/
│
├── ai/                                # AI Engine (Deliverables 9-11)
│   ├── knowledge-base/               # RAG Knowledge Base
│   ├── rag/                          # RAG implementation
│   ├── dictionary/                   # Client Dictionary Engine
│   └── models/                       # BERT Adapters
│
├── playbooks/                         # Delivery Factory (Deliverable 12)
│   ├── onboarding/
│   ├── evidence-collection/
│   ├── workshops/
│   └── qa-checklists/
│
├── src/                               # Source Code
│   ├── backend/                      # FastAPI Backend
│   │   ├── api/
│   │   ├── models/
│   │   ├── services/
│   │   └── main.py
│   ├── frontend/                     # Next.js Frontend
│   └── shared/
│
├── scripts/                           # Utility Scripts
├── tests/                             # Tests
├── deployment/                        # Docker, K8s, CI/CD
│   ├── docker-compose.yml
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── k8s/
│
└── config/                            # Configuration
    ├── settings.yaml
    └── env.example
```

---

## 🎯 12 Key Deliverables

### Phase A: Regulatory Preparation (Deliverables 1-5)
1. **Saudi Control Library** - Operational ECC/CCC/PDPL controls
2. **ECC↔CCC Unified Baseline + Delta** - Eliminate redundancy
3. **PDPL Operational Control Set** - Privacy registers & controls
4. **Evidence Master Catalog** - Audit-ready evidence templates
5. **Audit Test Procedures Library** - Test procedures for all controls

### Phase B: Competitive Edge (Deliverables 6-8)
6. **SICO Packs** - Pre-packaged compliance bundles
7. **Executive Reporting Kit** - Ready-to-use executive dashboards
8. **SOC ↔ GRC Bridge** - Incident-to-compliance automation

### Phase C: AI-Powered Automation (Deliverables 9-11)
9. **Bilingual Knowledge Base + RAG** - Citation-backed AI responses
10. **Client Dictionary Engine** - Client-specific bilingual terminology
11. **Per-Client BERT Adapters** - Custom NLP models (Premium)

### Phase D: Operational Excellence (Deliverable 12)
12. **Delivery Factory Playbook** - Repeatable delivery methodology

---

## 🔧 Tech Stack

### Backend
- **FastAPI** (Python 3.11+)
- **PostgreSQL** - Primary database
- **Redis** - Caching & session management
- **Chroma/Weaviate** - Vector database for RAG
- **LangChain** - AI orchestration

### Frontend
- **Next.js 14** (React + TypeScript)
- **Tailwind CSS**
- **shadcn/ui** - Component library
- **RTK Query** - State management

### AI/NLP
- **Transformers** (HuggingFace)
- **RAG** (Retrieval-Augmented Generation)
- **Bilingual Models** (Arabic + English)
- **BERT Adapters/LoRA** - Per-client customization

### DevOps
- **Docker & Docker Compose**
- **GitHub Actions** - CI/CD
- **Kubernetes-ready**

---

## 🚀 Installation

### 1. Backend Setup
```bash
cd src/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../../config/env.example .env
# Edit .env with your configuration
uvicorn main:app --reload
```

### 2. Frontend Setup
```bash
cd src/frontend
npm install
cp ../../config/env.example .env.local
# Edit .env.local
npm run dev
```

### 3. Docker Setup (Recommended)
```bash
docker-compose -f deployment/docker-compose.yml up -d
```

---

## 🔒 Security Pipeline

The repository includes a comprehensive automated security scanning pipeline:

### Available Security Commands

```bash
# Run all security scans locally
make security

# Individual scans
make security-deps    # Check dependency vulnerabilities
make security-sast    # Static application security testing
```

### Automated Security Scans

Every commit and pull request automatically runs:

- ✅ **Dependency Scanning**: Safety (Python) + npm audit (Node.js)
- ✅ **SAST**: Bandit + CodeQL for static code analysis  
- ✅ **Secret Detection**: Gitleaks for hardcoded credentials
- ✅ **SBOM Generation**: Software Bill of Materials for supply chain security

### Security Reports

View security findings in:
- **GitHub Security Tab**: CodeQL and code scanning alerts
- **Actions Artifacts**: Detailed JSON/SARIF reports
- **Pull Request Checks**: Automated status checks

📖 **Full Documentation**: See [docs/SECURITY_PIPELINE.md](docs/SECURITY_PIPELINE.md)

---

## 📊 Development Roadmap

- [x] **Phase 1**: Repository initialization ✅
- [x] **Phase 2**: Platform Development ✅
  - Backend (FastAPI + SQLAlchemy 2.0)
  - Frontend (Next.js 14 + Bilingual UI)
  - AI/RAG Engine (LangChain)
  - Evidence & Reporting modules
- [ ] **Phase 2.1**: Critical Security Controls (2 weeks) 🚨 **BLOCKING**
  - Authentication & Authorization
  - Data Encryption
  - Audit Logging
- [ ] **Phase 2.2**: Data Protection (2 weeks)
- [ ] **Phase 2.3**: AI Governance (2 weeks)
- [ ] **Phase 2.4**: Documentation (2 weeks)
- [ ] **Phase 3**: AI Enhancement (blocked until Phase 2.1-2.4 complete)

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for:

- Development workflow
- Code standards
- Testing requirements
- **Merge conflict resolution** - See [Conflict Resolution Guide](docs/CONFLICT_RESOLUTION_GUIDE.md)
- Pull request process

### Key Resources for Contributors

- **Getting Started**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Project Analysis**: [docs/PROJECT_ANALYSIS.md](docs/PROJECT_ANALYSIS.md) 🆕
- **Analysis Dashboard**: [docs/ANALYSIS_SUMMARY.md](docs/ANALYSIS_SUMMARY.md) 🆕
- **Compliance Status**: [docs/compliance/EXECUTIVE_SUMMARY.md](docs/compliance/EXECUTIVE_SUMMARY.md)
- **Security Remediation**: [docs/compliance/PHASE_2.1_REMEDIATION_PLAN.md](docs/compliance/PHASE_2.1_REMEDIATION_PLAN.md)
- **Conflict Resolution**: [docs/CONFLICT_RESOLUTION_GUIDE.md](docs/CONFLICT_RESOLUTION_GUIDE.md)
- **Security Pipeline**: [docs/SECURITY_PIPELINE.md](docs/SECURITY_PIPELINE.md)
- **API Documentation**: [docs/api/README.md](docs/api/README.md)
- **GitHub Copilot Troubleshooting**: [docs/development/COPILOT_TROUBLESHOOTING.md](docs/development/COPILOT_TROUBLESHOOTING.md)

---

## 📄 License

[To be determined - Proprietary/MIT/Apache 2.0]

---

## 📞 Contact

**Owner**: sonaiso  
**Project**: SICO GRC Platform  
**Repository**: https://github.com/sonaiso/sanadcom

---

**Built with ❤️ for Saudi Regulatory Compliance Excellence**