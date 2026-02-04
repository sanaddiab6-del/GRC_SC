# SICO GRC Platform (Sanad)

**Saudi Regulatory Compliance Engine**  
*ECC • CCC • PDPL — AI-Powered Bilingual Automation*

---

## 🎯 Overview

**SICO GRC Platform** is a comprehensive compliance and governance solution designed specifically for the Saudi regulatory landscape. It unifies **ECC (Essential Cybersecurity Controls)**, **CCC (Cloud Cybersecurity Controls)**, and **PDPL (Personal Data Protection Law)** into a single operational framework with AI-powered bilingual capabilities.

### Key Differentiators
- ✅ **Operational Control Library** — Not just text, but executable controls with evidence and test procedures
- ✅ **ECC↔CCC Baseline + Delta** — Eliminate 40-60% duplication between frameworks
- ✅ **PDPL Operational Controls** — Transform legal requirements into actionable registers and policies
- ✅ **AI-Powered RAG** — Bilingual (Arabic/English) knowledge retrieval with citation enforcement
- ✅ **SOC↔GRC Bridge** — Connect incident response to compliance controls
- ✅ **Audit-Ready Evidence** — Master catalog with templates and test procedures

---

## 📦 Project Deliverables (12 Core Outputs)

### A) Regulatory Preparation (Controls & Evidence)
1. **Saudi Control Library** (ECC + CCC + PDPL) — Unified operational format
2. **ECC↔CCC Unified Baseline + CCC Delta** — Reduce duplication
3. **PDPL Operational Control Set** — Privacy registers, policies, and evidence
4. **Evidence Master Catalog** — Audit-ready evidence dictionary
5. **Audit Test Procedures Library** — Test steps for every control

### B) Competitive Advantage
6. **SICO Packs** — Pre-packaged compliance solutions (ECC Baseline, CCC Cloud, PDPL Privacy)
7. **Executive Reporting Kit** — Templates for compliance heatmaps, risk reports, audit readiness
8. **SOC↔GRC Bridge** — Incident-to-control mapping and workflows

### C) AI Engine
9. **Bilingual Knowledge Base + RAG** — Citation-enforced retrieval
10. **Client Dictionary Engine** — Arabic/English terminology mapping
11. **Per-Client BERT Adapters** (Premium) — Customized NLP models

### D) Operational Excellence
12. **Delivery Factory Playbook** — Standardized onboarding, workshops, QA checklists

---

## 🏗️ Repository Structure

```
sanadcom/
├── docs/                    # Documentation
├── data/                    # Regulatory data (controls, mappings, evidence)
├── packs/                   # SICO Packs (ECC/CCC/PDPL bundles)
├── reporting/               # Executive reporting templates
├── soc-grc-bridge/         # Incident-control integration
├── ai/                      # AI/RAG engine
├── playbooks/               # Delivery playbooks
├── src/                     # Source code (backend + frontend)
├── scripts/                 # Utilities
├── tests/                   # Test suites
├── deployment/              # Docker, K8s, CI/CD
└── config/                  # Configuration files
```

---

## 🚀 Tech Stack

### Backend
- **Python 3.11+** (FastAPI)
- **PostgreSQL** (main database)
- **Chroma/Weaviate** (vector database for RAG)
- **Redis** (caching)

### Frontend
- **Next.js 14** (React)
- **TypeScript**
- **Tailwind CSS**
- **shadcn/ui**

### AI/NLP
- **Python** (Transformers, LangChain)
- **RAG** (Retrieval-Augmented Generation)
- **Bilingual models** (Arabic + English)

### DevOps
- **Docker** + **Docker Compose**
- **GitHub Actions** (CI/CD)
- **Kubernetes-ready**

---

## 📖 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+

### Quick Start
```bash
# Clone repository
git clone https://github.com/sonaiso/sanadcom.git
cd sanadcom

# Setup backend
cd src/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Setup frontend
cd ../frontend
npm install

# Run with Docker
docker-compose up -d
```

---

## 📚 Documentation

- [Architecture Overview](docs/architecture/)
- [12 Deliverables Guide](docs/deliverables/)
- [API Documentation](docs/api/)
- [User Guides](docs/user-guides/)

---

## 🤝 Contributing

This is a private repository. For contribution guidelines, please contact the project maintainers.

---

## 📄 License

Proprietary - All rights reserved

---

## 📞 Contact

**SICO Security Team**  
Owner: @sonaiso

---

*Built for Saudi regulatory excellence* 🇸🇦