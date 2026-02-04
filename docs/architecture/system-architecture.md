# SICO GRC Platform - System Architecture

## Overview

The SICO GRC Platform is a modern, cloud-native application designed for Saudi regulatory compliance. It follows a microservices-inspired architecture with clear separation of concerns.

## Architecture Principles

1. **Bilingual First**: All components support Arabic and English
2. **API-First**: Backend exposes RESTful APIs consumed by frontend
3. **Data-Driven**: Regulatory data separated from application logic
4. **Automation-Centric**: Minimize manual work through intelligent automation
5. **Audit-Ready**: Every action logged and traceable

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Layer                          │
│  Next.js 14 App (TypeScript + Tailwind + shadcn/ui)       │
│  - Executive Dashboards                                     │
│  - Control Management                                       │
│  - Evidence Repository                                      │
│  - PDPL Registers                                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTPS/REST
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     API Gateway Layer                       │
│                    FastAPI Backend                          │
└─────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │  PostgreSQL  │ │    Redis     │ │    Chroma    │
    │   Database   │ │    Cache     │ │  Vector DB   │
    └──────────────┘ └──────────────┘ └──────────────┘
```

## Component Details

### Frontend (Next.js 14)

**Technology Stack:**
- Next.js 14 with App Router
- TypeScript for type safety
- Tailwind CSS for styling
- shadcn/ui for components
- React Query for state management

**Key Features:**
- Server-side rendering (SSR)
- Optimized for Arabic RTL layout
- Responsive design
- Offline capability for evidence review

**Major Modules:**
- Dashboard & Analytics
- Control Library Browser
- Evidence Management
- PDPL Registers (RoPA, DSAR, Breach)
- SOC Integration View
- Executive Reports
- AI Assistant Interface

### Backend (FastAPI)

**Technology Stack:**
- Python 3.11+
- FastAPI for async API
- SQLAlchemy for ORM
- Alembic for migrations
- Pydantic for validation

**Core Services:**
- Control Management Service
- Evidence Service
- PDPL Compliance Service
- SOC Integration Service
- AI/RAG Service
- Reporting Service
- User Management Service

**API Design:**
- RESTful endpoints
- OpenAPI/Swagger documentation
- JWT authentication
- Role-based access control (RBAC)
- Rate limiting
- Audit logging

### Data Layer

**PostgreSQL Database:**
- Primary data store
- Stores controls, evidence, users, audits
- JSONB for flexible control metadata
- Full-text search support

**Redis Cache:**
- Session management
- API response caching
- Real-time updates
- Job queue for async tasks

**Chroma Vector DB:**
- Embeddings for bilingual search
- RAG knowledge base
- Semantic similarity matching
- Control and evidence search

### AI/NLP Engine

**Components:**
- LangChain for orchestration
- Sentence Transformers for embeddings
- Custom BERT adapters for Arabic
- Citation-based response generation

**Capabilities:**
- Bilingual natural language queries
- Control recommendation
- Evidence gap analysis
- Document classification
- Automated report generation

## Data Flow

### Control Implementation Flow

```
1. User selects control from library
2. System loads control requirements
3. User maps to existing evidence or creates new
4. AI suggests relevant evidence
5. User uploads/links evidence
6. System validates completeness
7. Control status updated
8. Dashboard reflects new status
```

### SOC Integration Flow

```
1. Security incident occurs
2. SIEM/SOAR closes incident
3. Webhook triggers GRC platform
4. System maps incident to controls
5. Evidence artifacts generated
6. Control status updated
7. Dashboard updated
8. Executive notification (if threshold)
```

## Security Architecture

**Authentication:**
- JWT-based authentication
- Multi-factor authentication (MFA)
- SSO integration (SAML, OAuth)

**Authorization:**
- Role-based access control (RBAC)
- Attribute-based access control (ABAC)
- Fine-grained permissions

**Data Protection:**
- Encryption at rest (AES-256)
- Encryption in transit (TLS 1.3)
- Field-level encryption for sensitive data
- Key management via HSM/KMS

**Audit & Compliance:**
- Complete audit trail
- Immutable logs
- Regular security assessments
- PDPL-compliant data handling

## Deployment Architecture

**Container Orchestration:**
- Docker for containerization
- Kubernetes for orchestration
- Helm charts for deployment

**High Availability:**
- Load balancing
- Auto-scaling
- Multi-zone deployment
- Database replication

**Backup & Recovery:**
- Automated daily backups
- Point-in-time recovery
- Disaster recovery plan
- RPO: 1 hour, RTO: 4 hours

## Integration Points

**External Systems:**
- SIEM (Splunk, QRadar, Sentinel)
- SOAR (Cortex XSOAR, Swimlane)
- Ticketing (Jira, ServiceNow)
- Cloud Providers (AWS, Azure, GCP)
- Email (SMTP, Exchange)
- Active Directory / LDAP

**APIs Provided:**
- RESTful API for all operations
- Webhook endpoints for events
- GraphQL for complex queries
- WebSocket for real-time updates

## Performance Targets

- API response time: < 200ms (p95)
- Page load time: < 2s
- Search response: < 500ms
- Report generation: < 10s for standard reports
- Concurrent users: 1000+
- Data retention: 7 years

## Scalability

**Horizontal Scaling:**
- Stateless API servers
- Database read replicas
- Cache clustering
- Queue-based async processing

**Vertical Scaling:**
- Optimized queries
- Efficient caching
- Background job processing
- Lazy loading

## Monitoring & Observability

**Metrics:**
- Application metrics (Prometheus)
- Infrastructure metrics (Node Exporter)
- Business metrics (custom)

**Logging:**
- Structured JSON logs
- Centralized log aggregation (ELK)
- Log retention policies

**Tracing:**
- Distributed tracing (Jaeger)
- Request correlation
- Performance profiling

**Alerting:**
- Threshold-based alerts
- Anomaly detection
- PagerDuty/Opsgenie integration
