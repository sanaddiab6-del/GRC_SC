# SICO GRC Platform - AI Agent Guide

## Architecture & Responsibilities
- Full stack spans FastAPI backend, Next.js 14 frontend, and LangChain-based RAG; backend entrypoint [src/backend/main.py](src/backend/main.py) wires controls, evidence, reporting, and AI routers under /api/v1.
- Runtime settings live in [src/backend/core/config.py](src/backend/core/config.py); .env co-located with backend sets DATABASE_URL, Redis, vector DB, and CORS, so load settings through pydantic BaseSettings instead of manual env parsing.
- Async SQLAlchemy infrastructure in [src/backend/core/database.py](src/backend/core/database.py) converts sync DSNs to asyncpg, exposes AsyncSession dependency, and auto-creates tables during startup lifespan; keep new models inheriting from Base to participate.
- Compliance domains are modularised: [src/backend/controls](src/backend/controls), [src/backend/evidence](src/backend/evidence), and [src/backend/reporting](src/backend/reporting) share a consistent trio of models, schemas, and routers.

## Backend Conventions
- Bilingual payloads are mandatory; follow the *_en/*_ar pattern and bilingual error payloads demonstrated in [src/backend/controls/router.py](src/backend/controls/router.py) and [src/backend/evidence/router.py](src/backend/evidence/router.py).
- Control identifiers must respect enums in [src/backend/controls/models.py](src/backend/controls/models.py), with framework stored as FrameworkType and statuses as ControlStatus; evidence rows reference controls via control_id.
- List endpoints implement offset/limit pagination with default 50 and optional filters; reuse the pattern in [src/backend/controls/router.py](src/backend/controls/router.py#L20-L66) to keep count queries and Query params aligned.
- Evidence creation computes expiry from retention days and stamps collection timestamps (see [src/backend/evidence/router.py](src/backend/evidence/router.py#L60-L119)); prefer server-side timestamps rather than trusting clients.
- Reporting dashboards in [src/backend/reporting/router.py](src/backend/reporting/router.py#L20-L160) aggregate SQL counts per framework and domain, so extend using SQLAlchemy queries before post-processing in Python.

## AI/RAG Layer
- Retrieval lives in [ai/rag/bilingual_retriever.py](ai/rag/bilingual_retriever.py); it instantiates HuggingFace embeddings and Chroma, returning bilingual metadata plus citations—avoid creating new retrievers per request.
- Document preparation uses [ai/rag/chunker.py](ai/rag/chunker.py) to build multi-section Document chunks mixing Arabic and English text; preserve control_id, framework, and section metadata when generating new chunks.
- Tests in [tests/ai/test_rag.py](tests/ai/test_rag.py) assert chunk metadata and mark vector-store-dependent tests with pytest.skip; mirror that gating for heavy integrations.

## Frontend Patterns
- App Router is locale-aware via [src/frontend/app/[locale]/layout.tsx](src/frontend/app/%5Blocale%5D/layout.tsx); every page receives locale and sets dir rtl/ltr, so new routes belong under [src/frontend/app/[locale]](src/frontend/app/%5Blocale%5D).
- UI strings come from [src/frontend/messages/en.json](src/frontend/messages/en.json) and [src/frontend/messages/ar.json](src/frontend/messages/ar.json); fetch translations with next-intl hooks instead of hardcoding.
- API access is centralised in [src/frontend/lib/api-client.ts](src/frontend/lib/api-client.ts) using axios with interceptors and NEXT_PUBLIC_API_URL; when adding data hooks use the shared client or SWR fetcher like [src/frontend/app/[locale]/controls/page.tsx](src/frontend/app/%5Blocale%5D/controls/page.tsx).

## Workflows & Tooling
- Make targets orchestrate common tasks: make install installs backend/frontend/AI deps, make docker-up starts the stack defined in [deployment/docker-compose.yml](deployment/docker-compose.yml), make test runs pytest then frontend npm tests.
- Backend tests under [tests/backend](tests/backend) rely on httpx.AsyncClient against the FastAPI app; ensure new routes expose predictable bilingual JSON to satisfy assertions.
- Seed data and utilities reside in [scripts](scripts); for example [scripts/load_sample_data.py](scripts/load_sample_data.py) populates baseline controls, so keep schema changes compatible.
- Security automation commands live in the Makefile (make security, make security-deps, make security-sast); align new tooling with the existing targets.
