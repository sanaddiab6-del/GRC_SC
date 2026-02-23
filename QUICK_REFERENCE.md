# 🚀 SICO GRC Platform - Quick Reference Cheat Sheet

## System At A Glance

### What is SICO?
**Saudi Compliance Platform** - Bilingual (Arabic/English) GRC system for NCA ECC, NCA CCC, PDPL, and SDAIA AI regulations.

### Tech Stack
```
Backend:  FastAPI + Python 3.11 + PostgreSQL + Redis
Frontend: Next.js 14 + TypeScript + Tailwind CSS
AI:       LangChain + Chroma + multilingual-e5-large
Deploy:   Docker Compose + Kubernetes-ready
```

### Current Status
- **Compliance**: 92% across 6 frameworks ✅
- **Security**: Production-ready with JWT, RBAC, encryption ✅
- **Modules**: 8 specialized compliance modules ✅
- **Phase**: 2.4 Complete (ready for Phase 3) ✅

---

## 🏗️ Architecture in 30 Seconds

```
Frontend (3000) → Backend (8000) → PostgreSQL (5432)
                ↓
            AI/RAG → Chroma (8001)
                ↓
            Redis (6379)
```

**8 Backend Modules**:
1. **auth** - JWT + RBAC (5 roles)
2. **controls** - ECC/CCC/PDPL frameworks
3. **evidence** - Audit evidence collection
4. **reporting** - Executive dashboards
5. **privacy** - PDPL compliance (consent, DSAR)
6. **incident** - Security incident tracking
7. **risk** - Risk management (NCA ECC-RM)
8. **ai_governance** - SDAIA AI compliance

---

## 🚀 Quick Start Commands

### Start Everything
```bash
# Clone & start
git clone https://github.com/sonaiso/sanadcom.git
cd sanadcom
docker-compose -f deployment/docker-compose.yml up -d

# Access
Frontend:  http://localhost:3000
Backend:   http://localhost:8000
API Docs:  http://localhost:8000/docs
```

### Individual Services
```bash
# Backend only
cd src/backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload

# Frontend only
cd src/frontend
npm install && npm run dev
```

### Database Operations
```bash
# Run migrations
cd src/backend
alembic upgrade head

# Create migration
alembic revision --autogenerate -m "description"

# Rollback
alembic downgrade -1

# Load sample data
cd ../../
python scripts/load_sample_data.py
```

### Testing
```bash
# Backend tests
cd src/backend && pytest tests/ -v

# Frontend tests
cd src/frontend && npm test

# AI tests
pytest tests/ai/test_rag.py -v
```

### Security
```bash
# Run all security scans
make security

# Individual scans
make security-deps     # Dependency vulnerabilities
make security-sast     # Static analysis
```

---

## 📂 Where is Everything?

### Key Directories
```
📁 src/backend/         # FastAPI application
📁 src/frontend/        # Next.js application
📁 ai/rag/              # AI/RAG engine
📁 data/                # Control frameworks & evidence catalog
📁 docs/                # Documentation
📁 tests/               # Test suites
📁 scripts/             # Utility scripts
📁 deployment/          # Docker Compose
```

### Important Files
```
📄 src/backend/main.py                    # FastAPI entry point
📄 src/backend/core/config.py             # Settings
📄 src/backend/core/database.py           # DB connection
📄 src/backend/core/security_middleware.py # Security
📄 src/frontend/app/[locale]/layout.tsx   # Frontend layout
📄 src/frontend/lib/api-client.ts         # API client
📄 data/controls/ecc_baseline.json        # ECC controls
📄 deployment/docker-compose.yml          # Docker setup
📄 config/env.example                     # Environment template
```

---

## 🔐 Security Configuration

### Environment Variables (Required)
```bash
# Security (NCA ECC-IS-3, PDPL Art 29)
SECRET_KEY=your-256-bit-secret-key-minimum-32-characters
ENCRYPTION_KEY=your-fernet-encryption-key-base64-encoded
TLS_ENABLED=true  # Required in production

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/sico_grc
REDIS_URL=redis://host:6379/0

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# Audit (NCA requirement)
AUDIT_LOG_RETENTION_YEARS=7
```

### Default Roles (RBAC)
```
Admin              → Full access
Compliance Officer → Manage controls, evidence, reports
Auditor            → Read-only + generate reports
Analyst            → Read controls, create evidence
Viewer             → Read-only public data
```

---

## 🌐 API Quick Reference

### Base URL
```
http://localhost:8000/api/v1
```

### Authentication
```bash
# Register
POST /api/v1/auth/register
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}

# Login
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
→ Returns: {"access_token": "...", "refresh_token": "..."}

# Use token in requests
Authorization: Bearer {access_token}
```

### Controls
```bash
# List controls
GET /api/v1/controls?framework=ECC&status=compliant&limit=50

# Get control
GET /api/v1/controls/{id}

# Create control (admin only)
POST /api/v1/controls
{
  "control_id": "ECC-GV-1",
  "framework": "ECC",
  "title_en": "Governance Framework",
  "title_ar": "إطار الحوكمة",
  ...
}
```

### Evidence
```bash
# List evidence
GET /api/v1/evidence?control_id=ECC-GV-1

# Upload evidence
POST /api/v1/evidence
Content-Type: multipart/form-data
- file: [file]
- control_id: ECC-GV-1
- title_en: Policy Document
```

### Dashboard
```bash
# Get metrics
GET /api/v1/reporting/dashboard
→ Returns compliance stats, control counts, etc.
```

### AI/RAG Query
```bash
# Query in Arabic
POST /api/v1/ai/query
{
  "query": "ما هي متطلبات الحوكمة؟",
  "language": "ar",
  "framework": ["ECC"],
  "top_k": 5
}

# Query in English
POST /api/v1/ai/query
{
  "query": "What are the governance requirements?",
  "language": "en",
  "top_k": 5
}
```

---

## 🧪 Common Development Tasks

### Add a New API Endpoint
```python
# 1. Add to router
# src/backend/{module}/router.py
@router.get("/new-endpoint")
async def new_endpoint():
    return {"message": "Hello"}

# 2. Register in main.py (if new router)
# src/backend/main.py
app.include_router(new_router, prefix="/api/v1/new")
```

### Add a New Database Model
```python
# 1. Create model
# src/backend/{module}/models.py
class NewModel(Base):
    __tablename__ = "new_table"
    id = Column(UUID, primary_key=True)
    # ... fields

# 2. Generate migration
cd src/backend
alembic revision --autogenerate -m "Add new_table"

# 3. Apply migration
alembic upgrade head
```

### Add Translation
```json
// src/frontend/messages/ar.json
{
  "new_section": {
    "title": "العنوان الجديد",
    "description": "الوصف"
  }
}

// src/frontend/messages/en.json
{
  "new_section": {
    "title": "New Title",
    "description": "Description"
  }
}
```

### Use Translation in Component
```tsx
import { useTranslations } from 'next-intl';

export default function Component() {
  const t = useTranslations('new_section');
  
  return (
    <div>
      <h1>{t('title')}</h1>
      <p>{t('description')}</p>
    </div>
  );
}
```

---

## 🔍 Troubleshooting

### Database Connection Failed
```bash
# Check PostgreSQL is running
docker-compose ps

# Restart database
docker-compose restart postgres

# Check connection
docker-compose exec postgres psql -U postgres -d sico_grc -c "\dt"
```

### Migration Error
```bash
# Check current revision
alembic current

# Show migration history
alembic history

# Downgrade to previous
alembic downgrade -1

# Upgrade to latest
alembic upgrade head
```

### Frontend Build Error
```bash
# Clear cache
rm -rf .next node_modules
npm install
npm run build
```

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Docker Issues
```bash
# Stop all containers
docker-compose down

# Remove volumes (CAUTION: deletes data)
docker-compose down -v

# Rebuild containers
docker-compose build --no-cache
docker-compose up -d
```

---

## 📊 Data Model Quick Reference

### Control Model
```python
control_id: str            # ECC-GV-1
framework: Enum            # ECC, CCC, PDPL
title_en / title_ar: str   # Bilingual
status: Enum               # compliant, partial, non_compliant, not_applicable
priority: Enum             # critical, high, medium, low
maturity_level: int        # 1-5
evidence_types: JSON       # ["policy", "log"]
related_controls: JSON     # {"CCC": ["CCC-GOV-01"]}
```

### Evidence Model
```python
control_id: FK             # Links to control
file_path: str             # Storage location
file_hash: str             # SHA-256
validation_status: Enum    # pending, validated, rejected
retention_period_years: int # NCA compliance
```

### User Model
```python
email: str (encrypted)     # User email
password_hash: str         # bcrypt
roles: Relationship        # Many-to-many
failed_login_attempts: int # Lockout tracking
locked_until: datetime     # Account lockout
```

---

## 🎯 Compliance Quick Reference

### Frameworks Supported
- **NCA ECC**: Essential Cybersecurity Controls (95% compliance)
- **NCA CCC**: Cloud Cybersecurity Controls (92% compliance)
- **PDPL**: Personal Data Protection Law (90% compliance)
- **SDAIA AI**: Saudi AI regulations (85% compliance)
- **ISO 27001**: Information security (93% compliance)
- **NIST CSF 2.0**: Cybersecurity framework (90% compliance)

### Key Compliance Features
✅ JWT authentication (NCA ECC-IS-3)  
✅ Field-level encryption (PDPL Art 29, NCA CCC-SEC-01)  
✅ 7-year audit logs (NCA requirement)  
✅ RBAC with 5 roles  
✅ Rate limiting (brute force prevention)  
✅ OWASP security headers  
✅ Consent management (PDPL)  
✅ DSAR workflow (PDPL Art 12-17)  
✅ Incident tracking (NCA ECC-IS-5)  
✅ Risk management (NCA ECC-RM)  

---

## 📖 Documentation Index

| Document | Purpose |
|----------|---------|
| **README.md** | Project overview & quick start |
| **SYSTEM_OVERVIEW.md** | Complete system documentation |
| **DIRECTORY_GUIDE.md** | Every file & folder explained |
| **QUICK_REFERENCE.md** | This file - quick cheat sheet |
| **QUICK_START.md** | Getting started guide |
| **CONTRIBUTING.md** | Contribution guidelines |
| **docs/api/README.md** | API documentation |
| **docs/compliance/EXECUTIVE_SUMMARY.md** | Compliance status |
| **docs/SECURITY_PIPELINE.md** | Security scanning |

---

## 🆘 Need Help?

### Documentation
- Full system overview: `SYSTEM_OVERVIEW.md`
- File-by-file guide: `DIRECTORY_GUIDE.md`
- API reference: `http://localhost:8000/docs`

### Logs
```bash
# Backend logs
docker-compose logs -f backend

# Frontend logs
docker-compose logs -f frontend

# Database logs
docker-compose logs -f postgres
```

### Health Checks
```bash
# Backend health
curl http://localhost:8000/

# Detailed health
curl http://localhost:8000/api/v1/health

# Security status
curl http://localhost:8000/api/v1/security-status
```

---

## 🎓 Learning Path

### New to Project?
1. Read `README.md` → Overview
2. Run Quick Start → Get it running
3. Explore API Docs → `http://localhost:8000/docs`
4. Read `SYSTEM_OVERVIEW.md` → Understand architecture
5. Check `DIRECTORY_GUIDE.md` → Know where things are

### Backend Developer?
1. Study `src/backend/main.py` → Entry point
2. Review `src/backend/core/` → Infrastructure
3. Explore modules → `controls/`, `evidence/`, etc.
4. Check migrations → `migrations/versions/`
5. Run tests → `pytest tests/backend/ -v`

### Frontend Developer?
1. Study `src/frontend/app/[locale]/layout.tsx` → Layout
2. Check pages → `dashboard/`, `controls/`
3. Review i18n → `messages/ar.json`, `en.json`
4. API client → `lib/api-client.ts`
5. Run dev server → `npm run dev`

### AI/RAG Developer?
1. Study `ai/rag/bilingual_retriever.py` → Core retriever
2. Check chunker → `ai/rag/chunker.py`
3. Backend integration → `src/backend/ai_router.py`
4. Run tests → `pytest tests/ai/test_rag.py`

---

## 🏆 Best Practices

### Code Style
- **Python**: Black formatter, type hints, docstrings
- **TypeScript**: ESLint, Prettier, strict mode
- **Bilingual**: All UI text in i18n files, never hardcoded

### Commit Messages
```bash
feat: Add new feature
fix: Bug fix
docs: Documentation
test: Add tests
refactor: Code refactoring
chore: Maintenance
security: Security fix
```

### Branch Naming
```bash
feature/feature-name
fix/bug-description
docs/documentation-update
security/security-fix
```

### Testing
- Write tests for all new features
- Maintain >80% code coverage
- Test bilingual functionality
- Test security features

---

## 🔗 Quick Links

- **Repository**: https://github.com/sonaiso/sanadcom
- **API Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000
- **Chroma DB**: http://localhost:8001

---

## 💡 Pro Tips

1. **Use Docker**: Simplest way to start everything
2. **Check Logs**: Most issues visible in `docker-compose logs`
3. **Load Sample Data**: `python scripts/load_sample_data.py`
4. **API First**: Test backend endpoints before frontend integration
5. **Bilingual Testing**: Always test in both Arabic and English
6. **Security First**: Never commit secrets, always use env vars
7. **Read Docs**: Check `docs/` folder for detailed guides
8. **Use Makefile**: `make help` shows all available commands

---

**Quick Reference Version**: 1.0  
**Last Updated**: 2026-02-08  
**Status**: Production Ready (92% Compliance) ✅

🎯 **Ready to code? Start with `docker-compose up -d` and visit http://localhost:8000/docs**
