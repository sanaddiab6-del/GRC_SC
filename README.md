# 🛡️ SICO GRC Platform

## Saudi Regulatory Compliance Engine (ECC/CCC/PDPL)

### 🎯 Overview
SICO GRC Platform is a comprehensive Saudi regulatory compliance engine that provides AI-powered bilingual automation for **ECC (Essential Cybersecurity Controls)**, **CCC (Cloud Cybersecurity Controls)**, and **PDPL (Personal Data Protection Law)** compliance.

### ✅ Platform Status (Updated: March 2026)
- **Backend API**: ✅ Operational (FastAPI + PostgreSQL + SQLAlchemy)
- **Frontend App**: ✅ Operational (Next.js 14 + TypeScript)  
- **Database**: ✅ PostgreSQL 15+ (Production-ready)
- **Cache/Sessions**: ✅ Redis 7+ (High-performance)
- **CI/CD Pipeline**: ✅ All checks passing
- **Security Features**: ✅ Phase 2.1-2.3 Complete (JWT, RBAC, Encryption, Audit Logging)
- **Compliance**: ✅ 100% NCA ECC/CCC/PDPL ready
- **Production Ready**: ⚠️  65% Complete - See [Gap Analysis](FUNCTIONAL_GAP_ANALYSIS.md) for details

**⚠️ Pre-Commercial Gaps:**
- Missing export functionality (PDF/Excel exports)
- Bulk operations not implemented
- Gap analysis feature required
- Some workflow lifecycles incomplete

See [FUNCTIONAL_GAP_ANALYSIS.md](FUNCTIONAL_GAP_ANALYSIS.md) for comprehensive assessment.

---

## 🚀 Quick Start

### Prerequisites Check
Before starting, ensure you have:
- ✅ Python 3.11+ (`python3 --version`)
- ✅ Node.js 20+ (`node --version`)
- ✅ PostgreSQL 15+ (`psql --version`)
- ✅ Redis 7+ (`redis-cli --version`)

### Installation Steps

1. **Clone Repository**
```bash
git clone https://github.com/sonaiso/sanadcom.git
cd sanadcom
```

2. **Setup Database** (See detailed steps below)
```bash
# Create PostgreSQL database
createdb -U postgres sico_grc
```

3. **Install Backend**
```bash
cd src/backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../../config/env.example .env
# Edit .env (update DATABASE_URL, SECRET_KEY)
alembic upgrade head
uvicorn main:app --reload
```

4. **Install Frontend** (in new terminal)
```bash
cd src/frontend
npm install
cp ../../config/env.example .env.local
npm run dev
```

5. **Access Application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs
- Login: admin@sanadcom.sa / Admin@123

---

### Prerequisites
### Prerequisites
- **Python 3.11+**
- **Node.js 20+**
- **PostgreSQL 15+** (Database)
- **Redis 7+** (Caching & Sessions)

### Development Tools
- **VS Code** (recommended) - See [VS Code setup guide](.vscode/README.md)
- **GitHub Copilot** - AI pair programming
- **pgAdmin** or **DBeaver** - Database management (optional)

---

## 📦 Project Structure

```
sanadcom/
│
├── README.md                          # Project overview
├── LICENSE
├── .gitignore
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

### 1. Database Setup (PostgreSQL)

#### Install PostgreSQL 15+
```bash
# Ubuntu/Debian
sudo apt install postgresql-15 postgresql-contrib

# macOS (Homebrew)
brew install postgresql@15

# Windows
# Download installer from https://www.postgresql.org/download/windows/
```

#### Create Database
```bash
# Start PostgreSQL service
sudo systemctl start postgresql   # Linux
brew services start postgresql@15 # macOS

# Create database and user
sudo -u postgres psql
```

```sql
CREATE DATABASE sico_grc;
CREATE USER sico_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE sico_grc TO sico_user;
\q
```

### 2. Redis Setup

#### Install Redis 7+
```bash
# Ubuntu/Debian
sudo apt install redis-server

# macOS
brew install redis

# Windows
# Download from https://redis.io/download or use WSL
```

#### Start Redis
```bash
sudo systemctl start redis   # Linux
brew services start redis    # macOS
redis-server                 # Manual start
```

### 3. Backend Setup
```bash
cd src/backend

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create environment file
cp ../../config/env.example .env

# Edit .env with your configuration
# Update these values:
# DATABASE_URL=postgresql://sico_user:your_secure_password@localhost:5432/sico_grc
# REDIS_URL=redis://localhost:6379/0
# SECRET_KEY=your-secret-key-min-32-chars
# ENCRYPTION_KEY=your-encryption-key-base64

# Run database migrations
alembic upgrade head

# Start backend server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`  
API Documentation: `http://localhost:8000/docs`

### 4. Frontend Setup
```bash
cd src/frontend

# Install dependencies
npm install

# Create environment file
cp ../../config/env.example .env.local

# Edit .env.local
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Start development server
npm run dev
```

Frontend will be available at: `http://localhost:3000`

### 5. Verify Installation
```bash
# Check backend health
curl http://localhost:8000/api/v1/health

# Check frontend
open http://localhost:3000  # or visit in browser
```

### 6. Load Sample Data (Optional)
```bash
cd src/backend
python scripts/load_saudi_frameworks.py
python scripts/load_sample_data.py
```

---

## 🔐 Default Credentials

**Admin User**:
- Email: `admin@sanadcom.sa`
- Password: `Admin@123`

⚠️ **Change default password immediately in production!**

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

---

## 📊 Development Roadmap

- [x] **Phase 1**: Repository initialization ✅
- [x] **Phase 2**: Platform Development ✅
  - Backend (FastAPI + SQLAlchemy 2.0)
  - Frontend (Next.js 14 + Bilingual UI)
  - AI/RAG Engine (LangChain)
  - Evidence & Reporting modules
- [x] **Phase 2.1-2.3**: Security Controls ✅
  - Authentication & Authorization
  - Data Encryption
  - Audit Logging
  - RBAC & Permissions
- [x] **Phase 2.4**: Production Readiness ✅
  - Backup & Disaster Recovery
  - Monitoring & Alerting
  - SIEM Integration
- [ ] **Phase 3**: Enterprise Features (In Progress - 65% Complete) 🚧
  - ⚠️ Export functionality (Controls, Evidence, Risks, Findings)
  - ⚠️ Bulk operations (Approve, Assign, Update)
  - ⚠️ Gap Analysis (Organization vs NCA frameworks)
  - ⚠️ Complete workflow lifecycles (Approval, Remediation, Escalation)
  - ⚠️ Mapping workflows (Control↔Risk↔Evidence↔Finding)
- [ ] **Phase 4**: AI Enhancement
  - Advanced RAG capabilities
  - Predictive analytics
  - Automated compliance recommendations

**📋 See [FUNCTIONAL_GAP_ANALYSIS.md](FUNCTIONAL_GAP_ANALYSIS.md) for detailed feature gaps and roadmap.**

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for:

- Development workflow
- Code standards
- Testing requirements
- Pull request process

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