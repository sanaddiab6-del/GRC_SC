# 🏗️ SICO GRC Platform - Clean Architecture Guide

## Overview

The SICO GRC Platform follows **Clean Architecture** principles to ensure:
- **Separation of Concerns** - Business logic isolated from infrastructure
- **Testability** - Easy to unit test without databases or external dependencies
- **Maintainability** - Changes in one layer don't cascade to others
- **Scalability** - Easy to add new features without breaking existing code

---

## Architecture Layers

```
src/backend/
├── api/                    # Layer 1: API Routes (HTTP interface)
│   ├── v1/
│   │   ├── controls.py
│   │   ├── evidence.py
│   │   ├── reporting.py
│   │   ├── rag.py
│   │   └── auth.py
│   └── dependencies.py     # FastAPI dependency injection
│
├── services/               # Layer 2: Business Logic
│   ├── control_service.py
│   ├── evidence_service.py
│   ├── risk_service.py
│   ├── rag_service.py
│   └── audit_service.py
│
├── repositories/           # Layer 3: Data Access
│   ├── control_repository.py
│   ├── evidence_repository.py
│   ├── user_repository.py
│   └── base_repository.py
│
├── models/                 # Layer 4: Data Models
│   ├── domain/            # Domain models (business entities)
│   │   ├── control.py
│   │   ├── evidence.py
│   │   └── user.py
│   ├── database.py        # SQLAlchemy ORM models
│   └── schemas.py         # Pydantic request/response schemas
│
├── core/                   # Layer 5: Cross-Cutting Concerns
│   ├── config.py          # Configuration management
│   ├── database.py        # Database session management
│   ├── security.py        # Encryption, hashing, JWT
│   ├── security_middleware.py  # Auth, rate limiting, audit logging
│   ├── exceptions.py      # Custom exceptions
│   └── logging.py         # Structured logging
│
├── ai/                     # Layer 6: AI/RAG Domain
│   ├── rag_engine.py      # RAG query processing
│   ├── retrieval.py       # Vector search
│   ├── guardrails.py      # Prompt injection defense
│   └── citations.py       # Citation extraction
│
└── tenancy/                # Layer 7: Multi-Tenancy
    ├── middleware.py      # Tenant context injection
    ├── isolation.py       # Tenant data isolation helpers
    └── models.py          # Tenant-specific models
```

---

## Layer Responsibilities

### Layer 1: API Routes (`api/`)
**Purpose:** Handle HTTP requests and responses

**Responsibilities:**
- Route definitions (`@app.get()`, `@app.post()`)
- Request validation (Pydantic schemas)
- Dependency injection (auth, database session)
- Response formatting (JSON, HTTP status codes)

**Rules:**
- ❌ **NO** business logic (use services instead)
- ❌ **NO** direct database access (use repositories via services)
- ✅ **YES** call service layer
- ✅ **YES** handle HTTP-specific concerns (cookies, headers)

**Example:**
```python
# api/v1/controls.py
from fastapi import APIRouter, Depends
from services.control_service import ControlService
from models.schemas import ControlCreateSchema, ControlResponseSchema
from api.dependencies import get_control_service, get_current_user

router = APIRouter()

@router.post("/controls", response_model=ControlResponseSchema)
async def create_control(
    data: ControlCreateSchema,
    service: ControlService = Depends(get_control_service),
    current_user = Depends(get_current_user)
):
    """Create a new control (API layer - no business logic here)"""
    # Validate user has permission (delegated to service)
    control = await service.create_control(data, current_user)
    return control
```

---

### Layer 2: Services (`services/`)
**Purpose:** Implement business logic and orchestrate workflows

**Responsibilities:**
- Business rules enforcement (e.g., "control must have at least 1 evidence")
- Workflow orchestration (e.g., "create control → link evidence → send notification")
- Permission checks (RBAC logic)
- Transaction management (commit/rollback)

**Rules:**
- ❌ **NO** HTTP concerns (don't access `request` object)
- ❌ **NO** direct SQL (use repositories)
- ✅ **YES** call repositories for data access
- ✅ **YES** call other services if needed
- ✅ **YES** raise domain exceptions (e.g., `ControlNotFoundError`)

**Example:**
```python
# services/control_service.py
from repositories.control_repository import ControlRepository
from repositories.evidence_repository import EvidenceRepository
from core.exceptions import InsufficientPermissionsError, ControlNotFoundError

class ControlService:
    def __init__(self, 
                 control_repo: ControlRepository, 
                 evidence_repo: EvidenceRepository):
        self.control_repo = control_repo
        self.evidence_repo = evidence_repo
    
    async def create_control(self, data, current_user):
        """Business logic: Create control + validate permissions"""
        # Check permission (business rule)
        if not current_user.has_role("Admin", "Compliance Officer"):
            raise InsufficientPermissionsError("Cannot create controls")
        
        # Validate business rule: Control must have description
        if not data.description_en or not data.description_ar:
            raise ValueError("Control must have bilingual descriptions")
        
        # Create control (delegate to repository)
        control = await self.control_repo.create(data)
        
        # Link default evidence templates (business workflow)
        default_templates = await self.evidence_repo.get_default_templates()
        for template in default_templates:
            await self.control_repo.link_evidence(control.id, template.id)
        
        return control
```

---

### Layer 3: Repositories (`repositories/`)
**Purpose:** Data access abstraction (hide database implementation details)

**Responsibilities:**
- CRUD operations (Create, Read, Update, Delete)
- Database queries (SQLAlchemy, raw SQL if needed)
- Caching logic (Redis integration)
- Data transformation (ORM → domain models)

**Rules:**
- ❌ **NO** business logic (e.g., permission checks belong in services)
- ❌ **NO** HTTP concerns
- ✅ **YES** use SQLAlchemy ORM or raw SQL
- ✅ **YES** handle database transactions
- ✅ **YES** return domain models (not ORM objects)

**Example:**
```python
# repositories/control_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.database import ControlORM
from models.domain.control import Control

class ControlRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data) -> Control:
        """Data access: Create control in database"""
        control_orm = ControlORM(
            framework=data.framework,
            domain=data.domain,
            title_en=data.title_en,
            title_ar=data.title_ar,
            description_en=data.description_en,
            description_ar=data.description_ar,
        )
        self.db.add(control_orm)
        await self.db.commit()
        await self.db.refresh(control_orm)
        
        # Convert ORM to domain model
        return Control.from_orm(control_orm)
    
    async def get_by_id(self, control_id: str) -> Control | None:
        """Data access: Fetch control by ID"""
        result = await self.db.execute(
            select(ControlORM).where(ControlORM.id == control_id)
        )
        control_orm = result.scalar_one_or_none()
        return Control.from_orm(control_orm) if control_orm else None
```

---

### Layer 4: Models (`models/`)
**Purpose:** Define data structures

**Subdirectories:**
- `domain/` - Business entities (pure Python classes, no ORM)
- `database.py` - SQLAlchemy ORM models (database tables)
- `schemas.py` - Pydantic models (API request/response validation)

**Rules:**
- ❌ **NO** business logic (models are data containers)
- ✅ **YES** validation logic (Pydantic validators)
- ✅ **YES** helper methods (e.g., `to_dict()`, `from_orm()`)

**Example:**
```python
# models/domain/control.py (Domain model)
from dataclasses import dataclass

@dataclass
class Control:
    id: str
    framework: str
    domain: str
    title_en: str
    title_ar: str
    description_en: str
    description_ar: str
    
    @classmethod
    def from_orm(cls, orm_obj):
        """Convert SQLAlchemy ORM to domain model"""
        return cls(
            id=orm_obj.id,
            framework=orm_obj.framework,
            domain=orm_obj.domain,
            title_en=orm_obj.title_en,
            title_ar=orm_obj.title_ar,
            description_en=orm_obj.description_en,
            description_ar=orm_obj.description_ar,
        )

# models/database.py (ORM model)
from sqlalchemy import Column, String
from core.database import Base

class ControlORM(Base):
    __tablename__ = "controls"
    
    id = Column(String, primary_key=True)
    framework = Column(String, nullable=False)
    domain = Column(String, nullable=False)
    title_en = Column(String, nullable=False)
    title_ar = Column(String, nullable=False)
    description_en = Column(String)
    description_ar = Column(String)

# models/schemas.py (Pydantic schema)
from pydantic import BaseModel, Field

class ControlCreateSchema(BaseModel):
    framework: str = Field(..., min_length=1, max_length=10)
    domain: str = Field(..., min_length=1, max_length=10)
    title_en: str = Field(..., min_length=1, max_length=200)
    title_ar: str = Field(..., min_length=1, max_length=200)
    description_en: str | None = None
    description_ar: str | None = None
```

---

### Layer 5: Core (`core/`)
**Purpose:** Cross-cutting concerns used across all layers

**Responsibilities:**
- Configuration (environment variables)
- Database connection management
- Security (encryption, JWT, password hashing)
- Middleware (authentication, rate limiting, audit logging)
- Exception handling
- Logging

**Example:**
```python
# core/security_middleware.py
from fastapi import Request
from core.audit_service import AuditLogger

async def audit_logging_middleware(request: Request, call_next):
    """Log every API call for NCA ECC-IS-4 compliance"""
    audit_logger = AuditLogger()
    
    # Before request
    user_id = getattr(request.state, 'user_id', None)
    
    # Process request
    response = await call_next(request)
    
    # After request (log audit trail)
    await audit_logger.log(
        user_id=user_id,
        action=f"{request.method} {request.url.path}",
        resource_type="api",
        status_code=response.status_code,
        ip_address=request.client.host
    )
    
    return response
```

---

### Layer 6: AI (`ai/`)
**Purpose:** AI/RAG domain logic

**Responsibilities:**
- RAG query processing
- Vector search (Chroma integration)
- Prompt injection detection
- Citation extraction
- LLM response generation

**Rules:**
- ❌ **NO** HTTP concerns (called by service layer)
- ✅ **YES** integrate with external AI services (OpenAI, Chroma)
- ✅ **YES** implement AI-specific business rules (refusal policy, citation requirement)

**Example:**
```python
# ai/rag_engine.py
from ai.retrieval import VectorSearchEngine
from ai.guardrails import PromptGuardrails

class RAGEngine:
    def __init__(self):
        self.retriever = VectorSearchEngine()
        self.guardrails = PromptGuardrails()
    
    async def query(self, query_text: str, user_permissions: list[str]):
        """Process RAG query with mandatory citations"""
        # 1. Detect prompt injection
        if self.guardrails.is_malicious(query_text):
            raise ValueError("Potentially malicious query detected")
        
        # 2. Retrieve relevant documents (RBAC-aware)
        docs = await self.retriever.search(query_text, user_permissions)
        
        # 3. Check confidence threshold
        if not docs or docs[0].score < 0.7:
            return {
                "answer": None,
                "refusal_reason": "No confident answer found. Please rephrase or contact compliance officer."
            }
        
        # 4. Generate answer with citations
        answer = self._generate_answer(query_text, docs)
        citations = [{"doc_id": d.id, "section": d.section, "score": d.score} for d in docs]
        
        return {
            "answer": answer,
            "citations": citations
        }
```

---

### Layer 7: Tenancy (`tenancy/`)
**Purpose:** Multi-tenant data isolation

**Responsibilities:**
- Tenant context injection (from JWT token)
- Row-level security (filter queries by `tenant_id`)
- Tenant-specific configuration

**Example:**
```python
# tenancy/middleware.py
from fastapi import Request

async def tenant_context_middleware(request: Request, call_next):
    """Inject tenant_id into request context"""
    # Extract tenant_id from JWT token
    token = request.headers.get("Authorization")
    tenant_id = extract_tenant_from_token(token)
    
    # Store in request state
    request.state.tenant_id = tenant_id
    
    return await call_next(request)

# tenancy/isolation.py
from sqlalchemy import select

def filter_by_tenant(query, model, tenant_id):
    """Helper: Add tenant_id filter to all queries"""
    return query.where(model.tenant_id == tenant_id)
```

---

## Dependency Injection

**FastAPI's Depends pattern** manages layer dependencies:

```python
# api/dependencies.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from repositories.control_repository import ControlRepository
from repositories.evidence_repository import EvidenceRepository
from services.control_service import ControlService

def get_control_repository(db: AsyncSession = Depends(get_db)) -> ControlRepository:
    """Dependency: Control repository"""
    return ControlRepository(db)

def get_evidence_repository(db: AsyncSession = Depends(get_db)) -> EvidenceRepository:
    """Dependency: Evidence repository"""
    return EvidenceRepository(db)

def get_control_service(
    control_repo: ControlRepository = Depends(get_control_repository),
    evidence_repo: EvidenceRepository = Depends(get_evidence_repository)
) -> ControlService:
    """Dependency: Control service"""
    return ControlService(control_repo, evidence_repo)
```

---

## Testing Strategy

### Unit Tests (Fast, No DB)
**Test:** Service layer business logic

```python
# tests/unit/test_control_service.py
import pytest
from services.control_service import ControlService
from unittest.mock import Mock

def test_create_control_without_permission():
    """Test: Non-admin cannot create control"""
    # Mock dependencies
    mock_control_repo = Mock()
    mock_evidence_repo = Mock()
    service = ControlService(mock_control_repo, mock_evidence_repo)
    
    # Mock user without permission
    user = Mock(has_role=Mock(return_value=False))
    
    # Assert raises exception
    with pytest.raises(InsufficientPermissionsError):
        await service.create_control(data={}, current_user=user)
```

### Integration Tests (Require DB)
**Test:** Repository + database interaction

```python
# tests/integration/test_control_repository.py
import pytest
from repositories.control_repository import ControlRepository

@pytest.mark.asyncio
async def test_create_control(db_session):
    """Test: Create control in database"""
    repo = ControlRepository(db_session)
    control = await repo.create({
        "framework": "ECC",
        "domain": "GV",
        "title_en": "Governance Policy",
        "title_ar": "سياسة الحوكمة"
    })
    
    assert control.id is not None
    assert control.framework == "ECC"
```

### End-to-End Tests
**Test:** Full API request → response

```python
# tests/e2e/test_control_api.py
from fastapi.testclient import TestClient

def test_create_control_api(client: TestClient, admin_token):
    """Test: POST /api/v1/controls"""
    response = client.post(
        "/api/v1/controls",
        json={"framework": "ECC", "domain": "GV", ...},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 201
    assert response.json()["framework"] == "ECC"
```

---

## Migration from Current Structure

### Current Structure (Existing)
```
src/backend/
├── controls/
│   ├── router.py        # Routes + business logic mixed
│   ├── models.py        # ORM models
│   └── schemas.py       # Pydantic schemas
├── evidence/
│   ├── router.py
│   ├── models.py
│   └── schemas.py
└── core/
    ├── config.py
    └── database.py
```

### Target Structure (Clean Architecture)
```
src/backend/
├── api/v1/
│   ├── controls.py      # Routes only (extracted from controls/router.py)
│   └── evidence.py
├── services/
│   ├── control_service.py   # Business logic (extracted from controls/router.py)
│   └── evidence_service.py
├── repositories/
│   ├── control_repository.py  # Data access (extracted from controls/router.py)
│   └── evidence_repository.py
├── models/
│   ├── database.py      # ORM models (merged from controls/models.py, evidence/models.py)
│   ├── schemas.py       # Pydantic schemas (merged)
│   └── domain/
│       ├── control.py
│       └── evidence.py
└── core/  (unchanged)
```

---

## Best Practices

### 1. Single Responsibility Principle
- Each layer has **one reason to change**
- API layer changes when HTTP interface changes
- Service layer changes when business rules change
- Repository layer changes when database schema changes

### 2. Dependency Inversion
- High-level layers (services) don't depend on low-level layers (repositories)
- Both depend on abstractions (interfaces)

### 3. Don't Repeat Yourself (DRY)
- Reuse repositories across services
- Reuse services across API endpoints

### 4. Fail Fast
- Validate inputs at API layer (Pydantic schemas)
- Check business rules at service layer (raise exceptions)
- Handle database errors at repository layer

---

## Common Pitfalls

### ❌ Business Logic in API Routes
```python
# BAD: Business logic in route
@router.post("/controls")
async def create_control(data, db):
    # ❌ Permission check in route
    if not current_user.is_admin:
        raise HTTPException(403)
    
    # ❌ Direct DB access in route
    control = ControlORM(**data.dict())
    db.add(control)
    await db.commit()
```

**Fix:** Move to service layer

---

### ❌ Direct Database Access in Services
```python
# BAD: Raw SQL in service
class ControlService:
    async def get_control(self, control_id):
        # ❌ Direct SQL in service
        result = await self.db.execute(f"SELECT * FROM controls WHERE id='{control_id}'")
```

**Fix:** Use repository

---

### ❌ HTTP Concerns in Services
```python
# BAD: Accessing request object in service
class ControlService:
    async def create_control(self, request: Request):
        # ❌ Service should not know about HTTP
        user_agent = request.headers.get("User-Agent")
```

**Fix:** Pass only data needed (not entire request object)

---

## References

- [Clean Architecture (Robert C. Martin)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [SQLAlchemy Async ORM](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Dependency Injection in FastAPI](https://fastapi.tiangolo.com/tutorial/dependencies/)

---

**Last Updated:** 2026-02-10  
**Version:** 1.0  
**Owner:** SICO GRC Engineering Team
