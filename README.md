# SICO GRC Platform
**Saudi Regulatory Compliance Engine**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)](https://nextjs.org/)

---

## 📋 Overview

**SICO GRC Platform** is a comprehensive Saudi regulatory compliance solution designed specifically for **ECC (Essential Cybersecurity Controls)**, **CCC (Cloud Cybersecurity Controls)**, and **PDPL (Personal Data Protection Law)** frameworks.

### 🎯 Core Value Propositions

- ✅ **Unified Control Library**: 100% operational controls with evidence requirements and test procedures
- ✅ **ECC ↔ CCC Optimization**: Baseline + Delta approach reduces compliance effort by 40-60%
- ✅ **PDPL Operational Framework**: Transforms legal requirements into actionable controls and registers
- ✅ **AI-Powered Bilingual Engine**: Arabic/English RAG with citation-backed responses
- ✅ **Audit-Ready Deliverables**: Executive reports, evidence catalogs, and test procedures
- ✅ **SOC ↔ GRC Bridge**: Seamless incident-to-compliance workflow

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SICO GRC Platform                         │
├─────────────────────────────────────────────────────────────┤
│  Frontend (Next.js + TypeScript)                            │
│  ├─ Compliance Dashboard                                    │
│  ├─ Evidence Management                                     │
│  ├─ Executive Reporting                                     │
│  └─ AI Assistant (Bilingual)                                │
├─────────────────────────────────────────────────────────────┤
│  Backend (FastAPI + Python)                                 │
│  ├─ Control Engine (ECC/CCC/PDPL)                          │
│  ├─ Evidence Validation & Tracking                         │
│  ├─ Audit Test Procedures                                  │
│  ├─ SOC Integration Layer                                  │
│  └─ Reporting & Analytics                                  │
├─────────────────────────────────────────────────────────────┤
│  AI/NLP Layer                                               │
│  ├─ RAG Engine (Retrieval + Citation)                      │
│  ├─ Bilingual Knowledge Base                               │
│  ├─ Client Dictionary Engine                               │
│  └─ BERT Adapters (Per-Client Customization)              │
├─────────────────────────────────────────────────────────────┤
│  Data Layer                                                 │
│  ├─ PostgreSQL (Structured Data)                           │
│  ├─ Vector DB (Chroma/Weaviate) - Embeddings              │
│  └─ Redis (Caching)                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Project Structure

```
sanadcom/
├── docs/                      # Documentation
│   ├── architecture/          # System architecture
│   ├── deliverables/          # 12 Core Deliverables
│   ├── user-guides/           # User manuals
│   └── api/                   # API documentation
│
├── data/                      # Regulatory Data Assets
│   ├── controls/              # ECC/CCC/PDPL Controls
│   ├── mappings/              # Cross-framework mappings
│   ├── evidence/              # Evidence Master Catalog
│   ├── audit/                 # Test Procedures Library
│   └── pdpl/                  # PDPL Registers
│
├── packs/                     # SICO Compliance Packs
│   ├── ecc-baseline/
│   ├── ccc-cloud/
│   └── pdpl-privacy/
│
├── reporting/                 # Executive Reporting Kit
│   ├── templates/
│   └── generators/
│
├── soc-grc-bridge/           # SOC ↔ GRC Integration
│   ├── incident-control-matrix.yaml
│   └── playbooks/
│
├── ai/                        # AI/NLP Engine
│   ├── knowledge-base/        # RAG Knowledge Base
│   ├── rag/                   # Retrieval & Citation
│   ├── dictionary/            # Client Dictionary Engine
│   └── models/                # BERT Adapters
│
├── playbooks/                 # Delivery Factory Playbooks
│   ├── onboarding/
│   ├── evidence-collection/
│   └── qa-checklists/
│
├── src/                       # Application Code
│   ├── backend/               # FastAPI backend
│   └── frontend/              # Next.js frontend
│
├── scripts/                   # Utility Scripts
├── tests/                     # Test Suites
├── deployment/                # Docker & K8s
└── config/                    # Configuration Files
```

---

## 🚀 Quick Start

### Prerequisites

- **Python** 3.11+
- **Node.js** 18+
- **Docker** & Docker Compose
- **PostgreSQL** 15+
- **Redis** 7+

### Installation

```bash
# Clone the repository
git clone https://github.com/sonaiso/sanadcom.git
cd sanadcom

# Backend setup
cd src/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install

# Start services with Docker Compose
cd ../../
docker-compose up -d
```

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/sico_grc
REDIS_URL=redis://localhost:6379

# AI/NLP
VECTOR_DB_URL=http://localhost:8000
OPENAI_API_KEY=your_key_here  # Optional

# Application
SECRET_KEY=your_secret_key
ENVIRONMENT=development
```

---

## 📚 Core Deliverables (12 Assets)

### **Regulatory Preparation (Assets 1-5)**
1. **Saudi Control Library** - ECC/CCC/PDPL operational controls
2. **ECC↔CCC Unified Baseline + Delta** - Reduce duplication
3. **PDPL Operational Control Set** - Registers + policies
4. **Evidence Master Catalog** - Audit-ready evidence definitions
5. **Audit Test Procedures Library** - Test procedures per control

### **Competitive Differentiators (Assets 6-8)**
6. **SICO Packs** - Pre-packaged compliance solutions
7. **Executive Reporting Kit** - Templates + generators
8. **SOC ↔ GRC Bridge** - Incident-to-compliance workflow

### **AI Capabilities (Assets 9-11)**
9. **Bilingual Knowledge Base + RAG** - Citation-backed AI
10. **Client Dictionary Engine** - Context-aware terminology
11. **BERT Adapters** - Per-client model customization

### **Operational Excellence (Asset 12)**
12. **Delivery Factory Playbook** - Repeatable delivery process

See `/docs/deliverables/` for detailed documentation.

---

## 🛠️ Technology Stack

### Backend
- **FastAPI** - High-performance async API
- **SQLAlchemy** - ORM
- **Alembic** - Database migrations
- **Pydantic** - Data validation
- **Celery** - Background tasks

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **shadcn/ui** - Component library
- **React Query** - Data fetching

### AI/NLP
- **LangChain** - RAG orchestration
- **Hugging Face Transformers** - NLP models
- **Chroma/Weaviate** - Vector database
- **spaCy** - NER & text processing

### DevOps
- **Docker** & Docker Compose
- **GitHub Actions** - CI/CD
- **Kubernetes-ready** structure
- **Prometheus** & Grafana - Monitoring

---

## 📖 Documentation

- [Architecture Overview](./docs/architecture/README.md)
- [API Documentation](./docs/api/README.md)
- [Deployment Guide](./docs/deployment/README.md)
- [Contributing Guidelines](./CONTRIBUTING.md)

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for details.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

---

## 📧 Contact

For inquiries: **[Your Contact Email]**

---

**Built with ❤️ for Saudi Cybersecurity & Privacy Compliance**