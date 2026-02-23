# SICO GRC Platform - Architecture Overview

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
│              (Next.js 14 + React + TypeScript)              │
│                                                              │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌───────────┐│
│  │Dashboard │  │ Controls  │  │ Reports  │  │  AI Chat  ││
│  └──────────┘  └───────────┘  └──────────┘  └───────────┘│
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                       │
│                     (FastAPI + REST)                        │
│                                                              │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌───────────┐│
│  │Controls  │  │Assessments│  │ Evidence │  │  AI RAG   ││
│  │   API    │  │    API    │  │   API    │  │    API    ││
│  └──────────┘  └───────────┘  └──────────┘  └───────────┘│
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Business Logic Layer                      │
│                  (Services + Domain Logic)                   │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │   Control    │  │  Compliance  │  │   AI/RAG         │ │
│  │   Service    │  │   Service    │  │   Service        │ │
│  └──────────────┘  └──────────────┘  └──────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                             │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │  PostgreSQL  │  │    Redis     │  │   ChromaDB       │ │
│  │  (Primary)   │  │   (Cache)    │  │  (Vectors)       │ │
│  └──────────────┘  └──────────────┘  └──────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. Frontend (Next.js)
- **Technology**: Next.js 14, React, TypeScript, Tailwind CSS
- **Features**:
  - Server-side rendering for performance
  - Bilingual support (English/Arabic)
  - Responsive design
  - Real-time updates

### 2. Backend API (FastAPI)
- **Technology**: Python 3.11+, FastAPI, SQLAlchemy
- **Features**:
  - RESTful API design
  - Async/await for performance
  - OpenAPI documentation
  - JWT authentication

### 3. Database Layer
- **PostgreSQL**: Primary data storage
  - User accounts
  - Control library
  - Assessment data
  - Evidence records
  
- **Redis**: Caching & sessions
  - Session management
  - API response caching
  - Rate limiting
  
- **ChromaDB**: Vector database
  - RAG embeddings
  - Semantic search
  - AI knowledge base

### 4. AI/ML Components
- **RAG Engine**: Citation-backed responses
- **Embedding Models**: Multilingual support
- **BERT Adapters**: Client-specific customization

## Data Flow

1. **User Request** → Frontend (Next.js)
2. **API Call** → Backend (FastAPI)
3. **Business Logic** → Services Layer
4. **Data Access** → Database/Cache
5. **Response** → JSON API
6. **Rendering** → Frontend Display

## Security Architecture

- JWT-based authentication
- Role-based access control (RBAC)
- Encryption at rest and in transit
- API rate limiting
- CORS protection
- SQL injection prevention (SQLAlchemy ORM)

## Scalability

- Horizontal scaling via Docker/Kubernetes
- Database connection pooling
- Redis caching layer
- Async API operations
- CDN for static assets

## Deployment

- **Development**: Docker Compose
- **Production**: Kubernetes-ready
- **CI/CD**: GitHub Actions
- **Monitoring**: Built-in health checks
