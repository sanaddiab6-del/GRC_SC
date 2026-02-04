# SICO GRC Platform - AI Coding Agent Instructions

## Project Overview
SICO is a bilingual (Arabic/English) Governance, Risk & Compliance platform for Saudi regulatory compliance (ECC, CCC, PDPL). Full-stack platform using FastAPI backend, Next.js 14 frontend, and LangChain-based RAG for bilingual compliance queries.

## Architecture

### Service Boundaries
- **Frontend**: Next.js 14 App Router + TypeScript + Tailwind at `src/frontend/` - bilingual UI (Arabic RTL/English LTR)
- **Backend API**: FastAPI (Python 3.11) at `src/backend/` - async SQLAlchemy, serves `/api/v1/*`
- **AI/RAG Engine**: LangChain + multilingual-e5 embeddings at `ai/` - citation-backed answers
- **Data Layer**: PostgreSQL (controls/evidence), Chroma (vector embeddings), Redis (cache)

### Key Components
1. **Control Engine** (`src/backend/controls/`): Manages ECC/CCC/PDPL control mappings
2. **Evidence Manager** (`src/backend/evidence/`): Audit evidence collection & validation
3. **Reporting Engine** (`src/backend/reporting/`): Executive dashboards and compliance reports
4. **AI/RAG Engine** (`ai/rag/`): Citation-backed bilingual answers, client dictionary mapping

### Data Flow
- Control Library (data/) → Control Engine → Evidence Manager → Reporting Engine
- User Query → RAG Engine → Vector DB lookup → Citation-backed response
- SOC Incidents (soc-grc-bridge/) → GRC mapping → Control violations

## Directory Structure (as per README)
```
sanadcom/
├── data/              # Control libraries (ECC/CCC/PDPL), evidence catalog
├── packs/             # SICO Packs: pre-packaged compliance solutions
├── reporting/         # Executive report templates
├── soc-grc-bridge/    # SOC-to-GRC incident mapping
├── ai/                # AI/RAG engine, BERT adapters, bilingual models
├── playbooks/         # Delivery playbooks and operational guides
├── src/
│   ├── backend/       # FastAPI application
│   └── frontend/      # Next.js application
├── scripts/           # Utility scripts (data import, migrations)
├── tests/             # Backend & frontend test suites
├── deployment/        # Docker Compose, K8s manifests
└── docs/              # Architecture, API docs, user guides
```

## Development Workflow

### Local Development
```bash
# Quick start with Docker Compose
make docker-up

# Or manual setup
cp config/env.example .env
docker-compose -f deployment/docker-compose.yml up -d

# Access points
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Chroma Vector DB: http://localhost:8001
```

### Running Services Individually
```bash
# Backend (requires PostgreSQL + Redis running)
cd src/backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend (requires backend running)
cd src/frontend
npm install
npm run dev
```

### Testing
```bash
# Backend tests (pytest with async support)
cd src/backend && pytest tests/ -v

# Frontend tests (Jest + React Testing Library)
cd src/frontend && npm test

# Run all tests
make test
```

### Database Migrations
```bash
# Create migration (using Alembic)
cd src/backend
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## Project-Specific Conventions

### Bilingual Support (Critical)
- **All UI strings**: Use i18n keys, never hardcode Arabic/English text
- **Database content**: Store Arabic (`name_ar`) and English (`name_en`) columns
- **API responses**: Include both languages in response payloads
- **RAG queries**: Support both Arabic and English input, return citations in query language

### Control Framework Conventions
- **Control IDs**: Format `ECC-{domain}-{number}`, `CCC-{domain}-{number}`, `PDPL-{number}`
- **Mapping structure**: Use JSON mapping files in `data/mappings/` for ECC↔CCC relationships
- **Evidence linking**: Each control references evidence types via `evidence_catalog_id`

### API Design
- **Versioning**: `/api/v1/` prefix for all endpoints (see [main.py](src/backend/main.py))
- **Bilingual errors**: Return error messages in both languages using `{"message_en": "...", "message_ar": "..."}`
- **Pagination**: Use `offset` & `limit` query params (default limit: 50) - see [controls/router.py](src/backend/controls/router.py)
- **Filtering**: Support `?framework=ECC&status=compliant` style filters
- **Response format**: Use Pydantic schemas from `*/schemas.py` for validation

### Database Models (SQLAlchemy 2.0 Async)
- **Bilingual columns**: All user-facing text has `_en` and `_ar` suffixes (e.g., `title_en`, `title_ar`)
- **Enums**: Use Python enums for status fields (see [controls/models.py](src/backend/controls/models.py))
- **JSON fields**: Use `JSONB` for flexible data like `evidence_types` and `related_controls`
- **Timestamps**: Include `created_at` and `updated_at` with automatic updates
- **Control IDs**: Format `{FRAMEWORK}-{DOMAIN}-{NUMBER}` (e.g., `ECC-GV-1`, `PDPL-12`)

### Frontend Patterns
- **i18n**: Use `next-intl` for translations - never hardcode Arabic/English text
- **RTL Support**: Components auto-flip based on locale (`dir="rtl"` for Arabic)
- **Fonts**: Cairo for Arabic, Inter for English (see [layout.tsx](src/frontend/app/layout.tsx))
- **API calls**: Use `axios` + `swr` for data fetching with caching
- **Styling**: Tailwind CSS with custom Arabic-friendly utilities

### AI/RAG Implementation
- **Citation tracking**: Always return source control IDs with RAG responses (see [bilingual_retriever.py](ai/rag/bilingual_retriever.py))
- **Client dictionaries**: Store custom terminology mappings in `ai/dictionaries/{client_id}.json`
- **Embeddings**: Use `intfloat/multilingual-e5-large` for Arabic/English support
- **Chunking strategy**: Split controls into logical sections (policy, procedure, evidence) - see [chunker.py](ai/rag/chunker.py)
- **Vector store**: Chroma DB with metadata filters for framework-specific queries
- **Response format**: Include `relevance_score` and `source` object with each result

## Integration Points

### SOC ↔ GRC Bridge
- Security incidents from SIEM → map to control violations via `soc-grc-bridge/mappings/`
- Alert severity → Risk rating conversion in `soc-grc-bridge/risk_calculator.py`

### External Dependencies
- **PDPL Regulations**: Fetch from Saudi DGA API (endpoint in config)
- **ECC/CCC Updates**: Monitor SAMA/CITC websites (automation in `scripts/regulatory_monitor.py`)

## Key Files to Reference
- [README.md](README.md): Full project vision and 12 core deliverables
- [src/backend/main.py](src/backend/main.py): FastAPI app entry point with router registration
- [src/backend/core/config.py](src/backend/core/config.py): Settings management with Pydantic
- [src/backend/core/database.py](src/backend/core/database.py): SQLAlchemy 2.0 async session factory
- [src/backend/controls/models.py](src/backend/controls/models.py): Control model with bilingual fields
- [src/backend/controls/router.py](src/backend/controls/router.py): RESTful control endpoints
- [ai/rag/bilingual_retriever.py](ai/rag/bilingual_retriever.py): Core RAG implementation
- [ai/rag/chunker.py](ai/rag/chunker.py): Document chunking strategy
- [deployment/docker-compose.yml](deployment/docker-compose.yml): Local development environment
- [data/controls/ecc_baseline.json](data/controls/ecc_baseline.json): Example control structure

## Common Tasks

### Adding a New Control Framework
1. Define control structure in `data/controls/{framework}_controls.json`
2. Create mapping to existing frameworks in `data/mappings/{framework}_to_ecc.json`
3. Update Control Engine models in `src/backend/controls/models.py`
4. Rebuild vector embeddings: `python scripts/rebuild_embeddings.py --framework {name}`

### Implementing a New Report
1. Create template in `reporting/templates/{report_name}.html`
2. Add report logic in `src/backend/reporting/generators/{report_name}.py`
3. Register endpoint in `src/backend/reporting/routes.py`
4. Add frontend component in `src/frontend/components/reports/`

### Updating RAG Knowledge Base
1. Add source documents to `ai/knowledge_base/{category}/`
2. Run chunking: `python ai/scripts/chunk_documents.py`
3. Generate embeddings: `python ai/scripts/generate_embeddings.py`
4. Validate retrieval: `pytest tests/ai/test_rag_retrieval.py`

## Phase Status (Current: Phase 2 - Platform Development)
- ✅ Repository structure established with all directories
- ✅ Backend scaffolding complete (FastAPI + SQLAlchemy 2.0 async)
- ✅ Frontend scaffolding complete (Next.js 14 + TypeScript)
- ✅ AI/RAG foundation implemented (LangChain + Chroma)
- ✅ Docker Compose environment configured
- ✅ **Evidence Management module complete** - Full CRUD + validation
- ✅ **Reporting Engine complete** - Executive dashboard + report generation
- ✅ **Frontend pages complete** - Dashboard, Controls list with bilingual UI
- ✅ **i18n implemented** - Arabic/English translations with next-intl
- ✅ **Alembic migrations setup** - Database schema management
- ✅ **AI/RAG API integrated** - Query endpoint with citation tracking
- ✅ **Comprehensive test coverage** - Backend, AI, and integration tests
- ✅ **Sample data loader** - Automated data population script
- 🔄 Ready for Phase 3: AI Enhancement
- See README.md roadmap for upcoming phases
