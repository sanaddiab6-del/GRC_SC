# SICO GRC Platform - Architecture Documentation

## System Overview
SICO is a comprehensive bilingual GRC platform designed specifically for Saudi Arabian regulatory frameworks (ECC, CCC, PDPL).

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Users (Browser)                       │
└─────────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────┐
│           Next.js Frontend (Port 3000)                   │
│   - Bilingual UI (Arabic RTL / English LTR)              │
│   - React Components with Tailwind CSS                   │
│   - next-intl for translations                           │
└─────────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────┐
│          FastAPI Backend (Port 8000)                     │
│   - RESTful API endpoints (/api/v1/*)                    │
│   - Async SQLAlchemy 2.0                                 │
│   - Pydantic validation                                  │
└─────────────────────────────────────────────────────────┘
                          ▼
┌──────────────┬──────────────┬──────────────────────────┐
│  PostgreSQL  │   Chroma DB  │      Redis Cache         │
│  (Port 5432) │  (Port 8001) │     (Port 6379)          │
└──────────────┴──────────────┴──────────────────────────┘
```

## Component Details

### Frontend Layer
- **Technology**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **i18n**: next-intl for Arabic/English support
- **State**: SWR for data fetching and caching

### Backend Layer
- **Framework**: FastAPI (Python 3.11)
- **ORM**: SQLAlchemy 2.0 (async)
- **Validation**: Pydantic v2
- **API Docs**: Auto-generated OpenAPI/Swagger

### Data Layer
- **Primary DB**: PostgreSQL 15+ (controls, evidence, audit trails)
- **Vector DB**: Chroma (semantic search embeddings)
- **Cache**: Redis (session data, query results)

### AI/RAG Layer
- **Framework**: LangChain
- **Embeddings**: intfloat/multilingual-e5-large
- **Vector Store**: Chroma with metadata filtering
- **Features**: Citation tracking, bilingual queries

## Data Flow Patterns

### Control Query Flow
1. User requests controls list via frontend
2. Frontend calls `/api/v1/controls` with filters
3. Backend queries PostgreSQL with SQLAlchemy
4. Results cached in Redis for 1 hour
5. Bilingual response returned to frontend

### RAG Query Flow
1. User submits question in Arabic or English
2. Query embedded using multilingual-e5 model
3. Chroma performs similarity search with metadata filters
4. Top-K results retrieved with source citations
5. Response formatted with relevance scores

## Security Considerations
- All API endpoints require authentication (JWT)
- CORS configured for frontend origin only
- Environment secrets managed via .env
- Database connections use connection pooling
- Input validation via Pydantic schemas

## Deployment Architecture
- **Development**: Docker Compose (all services)
- **Production**: Kubernetes-ready (future)
- **CI/CD**: GitHub Actions (planned)
