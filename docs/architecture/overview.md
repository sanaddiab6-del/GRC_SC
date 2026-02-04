# SICO GRC Platform - Architecture Overview

## Introduction

The SICO GRC Platform is a bilingual (Arabic/English) Governance, Risk & Compliance solution designed for Saudi regulatory compliance. The platform implements Saudi National Cybersecurity Authority (NCA) frameworks ECC and CCC, Personal Data Protection Law (PDPL), and integrates AI-powered RAG for bilingual compliance queries.

## System Architecture

### High-Level Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│   Backend API    │────▶│   Databases     │
│   (Next.js)     │     │   (FastAPI)      │     │   (PostgreSQL)  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                              │                            │
                              ▼                            ▼
                        ┌──────────────┐          ┌──────────────┐
                        │   AI/RAG     │          │  Vector DB   │
                        │  (LangChain) │          │  (Chroma)    │
                        └──────────────┘          └──────────────┘
```

## Core Components

### 1. Frontend Layer (Next.js 14)
- **Technology**: Next.js 14 App Router, TypeScript, Tailwind CSS
- **Features**:
  - Bilingual UI (Arabic RTL / English LTR)
  - Server-side rendering for performance
  - next-intl for internationalization
  - Radix UI components for accessibility
  - SWR for data fetching and caching

### 2. Backend API (FastAPI)
- **Technology**: FastAPI (Python 3.11), SQLAlchemy 2.0 Async
- **Architecture**:
  - RESTful API design with `/api/v1` prefix
  - Modular structure by domain (controls, evidence, reporting)
  - Async/await patterns for performance
  - Pydantic schemas for validation
  - Bilingual response support

**Key Modules**:
- **Controls**: Manages ECC/CCC/PDPL control libraries
- **Evidence**: Handles audit evidence collection and validation
- **Reporting**: Generates executive dashboards and compliance reports
- **AI Router**: Interfaces with RAG engine for bilingual queries

### 3. Data Layer

#### PostgreSQL Database
- Stores structured compliance data
- Bilingual columns (name_en, name_ar, description_en, description_ar)
- SQLAlchemy ORM models with async support
- Alembic for schema migrations

#### Redis Cache
- Session management
- Query result caching
- Rate limiting data
- Background job queues

#### Chroma Vector Database
- Stores control embeddings for RAG
- Supports semantic search
- Framework-specific collections
- Bilingual metadata filtering

### 4. AI/RAG Engine

**Components**:
- **Embedding Model**: intfloat/multilingual-e5-large
- **LLM**: GPT-4 or equivalent
- **Framework**: LangChain
- **Features**:
  - Citation-backed answers
  - Bilingual query support
  - Client-specific dictionaries
  - Source tracking for audit trails

**Workflow**:
1. User submits query in Arabic or English
2. Query is embedded using multilingual-e5
3. Vector similarity search in Chroma
4. Retrieved controls passed to LLM with context
5. Response generated with citations and source control IDs

## Service Boundaries

### Frontend Service
- **Port**: 3000
- **Responsibilities**:
  - User interface rendering
  - Client-side state management
  - API request orchestration
  - Internationalization

### Backend API Service
- **Port**: 8000
- **Responsibilities**:
  - Business logic processing
  - Data validation and transformation
  - Database operations
  - Authentication and authorization

### Vector DB Service (Chroma)
- **Port**: 8001
- **Responsibilities**:
  - Vector storage and retrieval
  - Semantic search
  - Similarity calculations

### PostgreSQL Service
- **Port**: 5432
- **Responsibilities**:
  - Relational data storage
  - ACID transactions
  - Query optimization

### Redis Service
- **Port**: 6379
- **Responsibilities**:
  - Caching layer
  - Session storage
  - Rate limiting

## Data Flow

### Control Management Flow
1. Control data loaded from YAML/JSON files
2. Stored in PostgreSQL with bilingual fields
3. Embedded and indexed in Chroma for RAG
4. Retrieved via REST API for frontend display
5. Updated through API with validation

### Evidence Management Flow
1. Evidence metadata stored in PostgreSQL
2. File uploads to object storage
3. Linked to controls via foreign keys
4. Validation against evidence catalog
5. Audit trail maintained

### RAG Query Flow
1. User query received in Arabic or English
2. Query embedding generated
3. Top K controls retrieved from Chroma
4. Context passed to LLM
5. Response with citations returned
6. Source controls tracked for audit

## Security Architecture

### Authentication & Authorization (Planned - Phase 2.1)
- JWT-based authentication
- OAuth2 / Azure AD integration
- Role-based access control (RBAC)
- Multi-factor authentication (MFA)

### Data Protection (Planned - Phase 2.2)
- TLS/HTTPS for all communications
- Field-level encryption for PII
- Azure Key Vault integration
- Data masking for sensitive fields

### Audit Logging (Planned - Phase 2.1)
- Comprehensive activity logging
- 7-year retention per NCA requirements
- Immutable audit trail
- SIEM integration ready

## Deployment Architecture

### Docker Compose (Development)
```yaml
services:
  - frontend (Next.js)
  - backend (FastAPI)
  - postgres (Database)
  - redis (Cache)
  - chroma (Vector DB)
```

### Kubernetes (Production - Planned)
- Horizontal pod autoscaling
- Load balancing with Ingress
- Persistent volume claims for databases
- ConfigMaps and Secrets management

## Integration Points

### SOC-GRC Bridge
- Security incidents from SIEM
- Map to control violations
- Alert severity to risk rating conversion

### External APIs
- PDPL regulations (Saudi DGA API)
- ECC/CCC updates (SAMA/CITC monitoring)

## Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend | Next.js | 14.1.0 |
| Frontend Runtime | React | 18.2.0 |
| Backend | FastAPI | 0.109.0 |
| Backend Runtime | Python | 3.11 |
| ORM | SQLAlchemy | 2.0.25 |
| Database | PostgreSQL | 15+ |
| Cache | Redis | 7+ |
| Vector DB | Chroma | 0.4.22 |
| AI Framework | LangChain | 0.1.0 |
| Embeddings | multilingual-e5-large | - |
| LLM | GPT-4 | - |

## Development Workflow

1. **Local Development**: Docker Compose environment
2. **Testing**: pytest (backend), Jest (frontend)
3. **Linting**: Black, Flake8 (backend), ESLint (frontend)
4. **Type Checking**: mypy (backend), TypeScript (frontend)
5. **Migrations**: Alembic for database schema changes
6. **CI/CD**: GitHub Actions (planned)

## Scalability Considerations

- Async API for high concurrency
- Redis caching to reduce database load
- Vector DB for fast semantic search
- Horizontal scaling via Kubernetes
- Database connection pooling
- CDN for static assets

## Monitoring & Observability (Planned)

- Application metrics (Prometheus)
- Distributed tracing (Jaeger)
- Log aggregation (ELK stack)
- Health checks and alerting

## Future Enhancements

1. **Phase 2.1**: Security & Authentication (Critical)
2. **Phase 2.2**: Data Protection & Privacy
3. **Phase 2.3**: AI Governance & Operations
4. **Phase 2.4**: Documentation & Certification
5. **Phase 3**: Enhanced AI capabilities
6. **Phase 4**: Advanced analytics and reporting

## References

- [README.md](../../README.md) - Project vision and roadmap
- [CONTRIBUTING.md](../../CONTRIBUTING.md) - Development guidelines
- [API Documentation](../api/) - REST API specifications
