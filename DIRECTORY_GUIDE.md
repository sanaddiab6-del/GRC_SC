# 📂 SICO GRC Platform - Directory & File Guide

## Quick Navigation

This guide provides a detailed explanation of every directory and file in the SICO GRC Platform repository.

---

## Root Level Files

### 📄 README.md
**Purpose**: Main project documentation  
**Contents**:
- Project overview and vision
- 12 key deliverables
- Quick start instructions
- Technology stack
- Installation guide
- Security pipeline overview
- Development roadmap

### 📄 SYSTEM_OVERVIEW.md
**Purpose**: Comprehensive system documentation (this document's companion)  
**Contents**:
- Complete architecture explanation
- Every module and component detailed
- Data flow diagrams
- API reference
- Security architecture
- Compliance framework details

### 📄 QUICK_START.md
**Purpose**: Getting started guide for developers  
**Contents**:
- Fast setup instructions
- Docker quick start
- Common commands
- Troubleshooting tips

### 📄 CONTRIBUTING.md
**Purpose**: Contributor guidelines  
**Contents**:
- Development workflow
- Code standards (Python, TypeScript)
- Testing requirements
- Pull request process
- Merge conflict resolution

### 📄 Makefile
**Purpose**: Build automation  
**Commands**:
```bash
make help              # Show all commands
make docker-up         # Start Docker Compose
make docker-down       # Stop Docker Compose
make security          # Run security scans
make security-deps     # Dependency vulnerabilities
make security-sast     # Static analysis
make test              # Run all tests
make lint              # Code linting
make format            # Code formatting
```

### 📄 .gitignore
**Purpose**: Git exclusion rules  
**Excludes**:
- Python: `__pycache__/`, `*.pyc`, `venv/`, `.env`
- Node.js: `node_modules/`, `.next/`, `dist/`
- IDE: `.vscode/`, `.idea/`, `*.swp`
- Build: `build/`, `*.egg-info/`
- Data: `vectordb/`, `*.db`, `*.sqlite`

### 📄 pyrightconfig.json
**Purpose**: Python type checking configuration  
**Settings**:
- Type checking level: basic
- Python version: 3.11
- Excluded paths: migrations, tests

### 📄 demo.html
**Purpose**: Platform demonstration page  
**Usage**: Open in browser to view project pitch/demo

### 📄 start-dev.ps1
**Purpose**: Windows PowerShell startup script  
**Usage**: Quick start for Windows developers

---

## 📁 .github/ - GitHub Configuration

### 📄 .github/copilot-instructions.md
**Purpose**: AI coding agent instructions  
**Contents**:
- Project-specific conventions
- Module boundaries
- Bilingual requirements
- Control framework standards
- API design patterns
- Database model conventions
- Security implementation details
- Phase status tracking

### 📁 .github/workflows/ (Planned)
**Purpose**: CI/CD pipeline definitions  
**Planned Workflows**:
- `ci.yml` - Continuous integration (tests, linting)
- `security.yml` - Security scans (SAST, dependency checks)
- `deploy.yml` - Automated deployment

---

## 📁 config/ - Configuration

### 📄 config/env.example
**Purpose**: Environment variables template  
**Variables**:
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
REDIS_URL=redis://host:6379/0

# Security (NCA ECC-IS-3, PDPL Art 29)
SECRET_KEY=your-256-bit-secret-key-here
ENCRYPTION_KEY=your-encryption-key-here
TLS_ENABLED=true

# Rate Limiting (Brute Force Prevention)
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# Audit Logging (NCA Requirement)
AUDIT_LOG_RETENTION_YEARS=7

# AI/RAG
VECTOR_DB_HOST=chroma
VECTOR_DB_PORT=8000

# Azure (Production)
AZURE_KEY_VAULT_URL=https://your-keyvault.vault.azure.net/
```

**Usage**:
```bash
cp config/env.example .env
# Edit .env with your values
```

---

## 📁 src/ - Source Code

### Directory Structure
```
src/
├── backend/          # FastAPI Python application
└── frontend/         # Next.js TypeScript application
```

---

## 📁 src/backend/ - FastAPI Backend

### Root Level Files

#### 📄 main.py
**Purpose**: FastAPI application entry point  
**Key Components**:
- FastAPI app initialization
- Router registration (8 modules + AI)
- Lifespan management (startup/shutdown)
- Database initialization
- RBAC setup
- Health check endpoints
- Security middleware

**Registered Routers**:
```python
/api/v1/auth          # Authentication & authorization
/api/v1/controls      # Control framework management
/api/v1/evidence      # Evidence collection
/api/v1/reporting     # Executive reporting
/api/v1/ai            # AI/RAG queries
/api/v1/privacy       # PDPL compliance
/api/v1/incident      # Security incidents
/api/v1/risk          # Risk management
/api/v1/ai-governance # AI model governance
```

#### 📄 ai_router.py
**Purpose**: AI/RAG query endpoint  
**Endpoints**:
- `POST /api/v1/ai/query` - Bilingual semantic search with citations

#### 📄 alembic.ini
**Purpose**: Alembic database migration configuration  
**Settings**:
- Script location: `migrations/`
- Sqlalchemy URL from config
- Logging configuration

#### 📄 requirements.txt
**Purpose**: Python dependencies  
**Key Packages**:
```
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
sqlalchemy>=2.0.25
asyncpg>=0.29.0
alembic>=1.13.1
pydantic>=2.5.3
pydantic-settings>=2.1.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6
cryptography>=42.0.0
redis>=5.0.1
httpx>=0.26.0
```

#### 📄 Dockerfile
**Purpose**: Backend container image definition  
**Base Image**: `python:3.11-slim`  
**Process**:
1. Install system dependencies
2. Copy requirements.txt
3. Install Python packages
4. Copy application code
5. Expose port 8000
6. Run uvicorn server

---

### 📁 core/ - Infrastructure Layer

#### 📄 core/database.py
**Purpose**: Database connection and session management  
**Components**:
- `engine`: AsyncEngine for PostgreSQL with asyncpg driver
- `AsyncSessionLocal`: Async session factory
- `Base`: SQLAlchemy declarative base
- `get_db()`: Dependency injection for database sessions
- `init_db()`: Database initialization (create tables, load models)
- `_load_models()`: Import all models for SQLAlchemy metadata

**Configuration**:
```python
DATABASE_URL = "postgresql+asyncpg://user:pass@host:5432/db"
pool_size = 10
max_overflow = 20
echo = True (development) / False (production)
```

#### 📄 core/config.py
**Purpose**: Application settings management  
**Implementation**: Pydantic BaseSettings  
**Settings Categories**:
- **Database**: URLs for PostgreSQL, Redis
- **Security**: Secret keys, encryption, TLS
- **Rate Limiting**: Per-minute, per-hour limits
- **Audit**: Log retention period
- **AI**: Vector DB configuration
- **Compliance**: Framework flags

**Validation**:
- SECRET_KEY must be 32+ characters
- ENCRYPTION_KEY required in production
- TLS_ENABLED enforced in production
- Environment-specific defaults

#### 📄 core/encryption.py
**Purpose**: Field-level data encryption  
**Algorithm**: Fernet (AES-256 symmetric encryption)  
**Key Management**:
- Development: Environment variable
- Production: Azure Key Vault

**Functions**:
```python
encrypt_field(value: str) -> str
    # Encrypts data, returns base64-encoded ciphertext

decrypt_field(encrypted_value: str) -> str
    # Decrypts ciphertext, returns plaintext

get_encryption_key() -> bytes
    # Retrieves key from Azure Key Vault or env var
```

**Use Cases**:
- PII encryption (PDPL Article 29)
- Sensitive control data
- User personal information

#### 📄 core/security_middleware.py
**Purpose**: Application-level security  
**Components**:

1. **OWASP Security Headers**:
   ```python
   X-Content-Type-Options: nosniff
   X-Frame-Options: DENY
   Content-Security-Policy: default-src 'self'
   Strict-Transport-Security: max-age=31536000
   X-XSS-Protection: 1; mode=block
   ```

2. **Rate Limiting** (NCA ECC-IS-3):
   - Per-minute limit: 60 requests/IP
   - Per-hour limit: 1000 requests/IP
   - Configurable via environment

3. **CORS Policy**:
   - Whitelist origins (localhost:3000, 8000)
   - Credentials allowed
   - All methods permitted

4. **Audit Logging Middleware**:
   - Logs all requests
   - Captures: user, action, IP, timestamp
   - 7-year retention

5. **Trusted Host Middleware**:
   - Validates Host header
   - Prevents host header injection

#### 📄 core/tls_config.py
**Purpose**: TLS/SSL certificate management  
**Features**:
- Certificate loading from filesystem
- Azure Key Vault integration (production)
- TLS 1.3 enforcement
- Certificate validation
- HTTPS redirect

#### 📄 core/input_validation.py
**Purpose**: Request validation and sanitization  
**Protections**:
- SQL injection prevention
- XSS attack prevention
- Input length limits
- Special character filtering
- HTML tag stripping

**Validators**:
```python
sanitize_string(value: str) -> str
validate_control_id(control_id: str) -> bool
validate_email(email: str) -> bool
validate_url(url: str) -> bool
```

#### 📄 core/types.py
**Purpose**: Custom type definitions  
**Types**:
- `ControlID`: Format-validated control ID
- `Framework`: Enum (ECC, CCC, PDPL)
- `Status`: Enum (compliant, partial, non_compliant, not_applicable)
- `Priority`: Enum (critical, high, medium, low)
- `MaturityLevel`: Integer 1-5

---

### 📁 migrations/ - Database Migrations

#### 📄 migrations/env.py
**Purpose**: Alembic migration environment setup  
**Functions**:
- Loads application configuration
- Imports all models for metadata detection
- Configures online/offline migration modes
- Sets up logging

#### 📁 migrations/versions/

##### 📄 001_initial_migration.py
**Purpose**: Initial database schema  
**Creates Tables**:
- `controls`: Control framework data
- `evidence`: Evidence collection
- `reports`: Reporting system

**Dependencies**: None (first migration)

##### 📄 002_auth_system.py
**Purpose**: Authentication and authorization  
**Creates Tables**:
- `users`: User accounts
- `roles`: RBAC roles (Admin, Compliance Officer, etc.)
- `permissions`: Granular permissions
- `user_roles`: Many-to-many association
- `role_permissions`: Many-to-many association
- `refresh_tokens`: Token whitelist
- `audit_logs`: 7-year audit trail

**Dependencies**: 001_initial_migration

##### 📄 003_privacy_incident_risk_ai_governance.py
**Purpose**: Compliance modules (Phase 2.2, 2.3)  
**Creates Tables**:

**Privacy (PDPL)**:
- `consent_records`: Consent management
- `dsar_requests`: Data subject access requests
- `data_classifications`: Data classification levels

**Incident Management**:
- `security_incidents`: Incident tracking
- `incident_responses`: Response actions

**Risk Management**:
- `risks`: Risk register
- `risk_treatments`: Mitigation plans

**AI Governance**:
- `ai_models`: Model registry
- `model_audits`: Model audit logs

**Dependencies**: 002_auth_system

---

### 📁 auth/ - Authentication & Authorization

#### 📄 auth/models.py
**Purpose**: Authentication data models  
**Models**:

```python
User:
  - id: UUID (primary key)
  - email: str (unique, encrypted)
  - password_hash: str (bcrypt)
  - full_name: str (encrypted)
  - is_active: bool
  - is_superuser: bool
  - created_at: datetime
  - updated_at: datetime
  - failed_login_attempts: int
  - locked_until: datetime (account lockout)
  - roles: Relationship[Role] (many-to-many)
  - audit_logs: Relationship[AuditLog]

Role:
  - id: UUID
  - name: str (Admin, Compliance Officer, Auditor, Analyst, Viewer)
  - description: str
  - permissions: Relationship[Permission] (many-to-many)

Permission:
  - id: UUID
  - resource: str (controls, evidence, reports, etc.)
  - action: str (create, read, update, delete)

AuditLog:
  - id: UUID
  - user_id: ForeignKey(User)
  - timestamp: datetime
  - action: str
  - resource_type: str
  - resource_id: str
  - ip_address: str
  - user_agent: str
  - result: str (success/failure)
  - details: JSON

RefreshToken:
  - id: UUID
  - token: str (indexed)
  - user_id: ForeignKey(User)
  - expires_at: datetime
  - revoked: bool
```

#### 📄 auth/schemas.py
**Purpose**: Pydantic validation schemas  
**Schemas**:
- `UserCreate`: Registration data
- `UserLogin`: Login credentials
- `UserResponse`: Safe user data (no password)
- `Token`: JWT token response
- `TokenRefresh`: Refresh token request
- `RoleResponse`: Role information
- `AuditLogResponse`: Audit log entry

#### 📄 auth/router.py
**Purpose**: Authentication API endpoints  
**Endpoints**:
```python
POST   /auth/register          # User registration
POST   /auth/login             # Login (returns JWT)
POST   /auth/refresh           # Refresh access token
POST   /auth/logout            # Logout (revoke token)
GET    /auth/me                # Current user info
GET    /auth/roles             # List available roles
GET    /auth/audit-logs        # Audit trail (admin only)
PUT    /auth/users/{id}/roles  # Assign roles (admin only)
```

#### 📄 auth/security.py
**Purpose**: Security utilities  
**Functions**:

```python
# Password Management
hash_password(password: str) -> str
verify_password(plain: str, hashed: str) -> bool

# JWT Tokens
create_access_token(data: dict) -> str
create_refresh_token(data: dict) -> str
verify_token(token: str) -> dict

# Account Security
check_account_lockout(user: User) -> bool
record_failed_login(user: User)
clear_failed_logins(user: User)

# Dependencies
get_current_user(token: str = Depends(oauth2_scheme)) -> User
require_role(roles: List[str])
```

**Security Features**:
- bcrypt password hashing (cost factor: 12)
- JWT with HS256 algorithm
- Token expiry: 30 min (access), 7 days (refresh)
- Account lockout: 5 attempts = 30 min lock
- Token blacklist support

#### 📄 auth/rbac_setup.py
**Purpose**: Initialize RBAC system  
**Function**: `setup_rbac(db: AsyncSession)`  
**Creates**:
1. **Roles**: Admin, Compliance Officer, Auditor, Analyst, Viewer
2. **Permissions**: Resource + action combinations
3. **Role-Permission Mappings**

**Role Hierarchy**:
```
Admin:
  - All permissions (create, read, update, delete on all resources)

Compliance Officer:
  - Manage controls, evidence, reports
  - Read privacy, incidents, risks

Auditor:
  - Read-only access to all resources
  - Generate reports

Analyst:
  - Read controls
  - Create/update evidence
  - Read reports

Viewer:
  - Read-only access to public data
```

---

### 📁 controls/ - Control Framework Management

#### 📄 controls/models.py
**Purpose**: Control data model  
**Model**:
```python
Control:
  - id: UUID (primary key)
  - control_id: str (unique, indexed) # ECC-GV-1, CCC-SEC-01, PDPL-12
  - framework: Enum[ECC, CCC, PDPL]
  - domain: str # Governance, Security, Privacy, etc.
  
  # Bilingual Content
  - title_en: str
  - title_ar: str
  - description_en: text
  - description_ar: text
  - policy_guidance_en: text
  - policy_guidance_ar: text
  - procedure_guidance_en: text
  - procedure_guidance_ar: text
  
  # Status & Maturity
  - priority: Enum[critical, high, medium, low]
  - status: Enum[compliant, partial, non_compliant, not_applicable]
  - maturity_level: int (1-5)
  
  # Relationships
  - evidence_types: JSON array
  - related_controls: JSON (cross-framework mappings)
  
  # Audit
  - created_at: datetime
  - updated_at: datetime
  - created_by: ForeignKey(User)
  - updated_by: ForeignKey(User)
```

#### 📄 controls/schemas.py
**Purpose**: API schemas  
**Schemas**:
- `ControlCreate`: Create control request
- `ControlUpdate`: Update control request
- `ControlResponse`: Control response with all fields
- `ControlListResponse`: Paginated list response
- `FrameworkEnum`: Framework choices
- `StatusEnum`: Status choices

#### 📄 controls/router.py
**Purpose**: Control API endpoints  
**Endpoints**:
```python
GET    /controls                # List controls (paginated, filtered)
POST   /controls                # Create control (admin only)
GET    /controls/{id}           # Get control details
PUT    /controls/{id}           # Update control (admin/officer)
DELETE /controls/{id}           # Delete control (admin only)
GET    /controls/frameworks     # List available frameworks
GET    /controls/stats          # Control statistics by framework
```

**Filters**:
- `framework`: ECC, CCC, PDPL, or All
- `status`: compliant, partial, non_compliant, not_applicable
- `priority`: critical, high, medium, low
- `domain`: Governance, Security, Privacy, etc.
- `search`: Search in title and description

**Pagination**:
- `offset`: Starting record (default: 0)
- `limit`: Records per page (default: 50, max: 100)

---

### 📁 evidence/ - Evidence Management

#### 📄 evidence/models.py
**Purpose**: Evidence data model  
**Model**:
```python
Evidence:
  - id: UUID (primary key)
  - control_id: ForeignKey(Control)
  - evidence_type: str # policy, log, certificate, etc.
  
  # Bilingual Content
  - title_en: str
  - title_ar: str
  - description_en: text
  - description_ar: text
  
  # File Management
  - file_path: str (storage location)
  - file_name: str
  - file_size: int (bytes)
  - file_hash: str (SHA-256)
  - mime_type: str
  
  # Validation
  - validation_status: Enum[pending, validated, rejected]
  - validated_by: ForeignKey(User)
  - validated_at: datetime
  - validation_notes: text
  
  # Retention (NCA Requirement)
  - retention_period_years: int
  - retention_start_date: date
  - retention_end_date: date
  
  # Audit
  - uploaded_by: ForeignKey(User)
  - upload_date: datetime
```

#### 📄 evidence/schemas.py
**Purpose**: Evidence API schemas  
**Schemas**:
- `EvidenceCreate`: Upload evidence
- `EvidenceUpdate`: Update metadata
- `EvidenceResponse`: Evidence details
- `EvidenceValidate`: Validation request
- `EvidenceListResponse`: Paginated list

#### 📄 evidence/router.py
**Purpose**: Evidence API endpoints  
**Endpoints**:
```python
GET    /evidence                # List evidence (paginated)
POST   /evidence                # Upload evidence
GET    /evidence/{id}           # Get evidence details
PUT    /evidence/{id}           # Update evidence metadata
DELETE /evidence/{id}           # Delete evidence (admin only)
POST   /evidence/{id}/validate  # Validate evidence (auditor)
GET    /evidence/{id}/download  # Download evidence file
```

**File Handling**:
- Upload with `multipart/form-data`
- SHA-256 hash generation
- File size limits
- Storage in secure location
- Access control via JWT

---

### 📁 reporting/ - Executive Reporting

#### 📄 reporting/models.py
**Purpose**: Report data model  
**Model**:
```python
Report:
  - id: UUID (primary key)
  - report_type: Enum[
      compliance_summary,
      risk_heatmap,
      audit_readiness,
      gap_analysis,
      executive_dashboard,
      control_maturity
    ]
  
  # Bilingual Content
  - title_en: str
  - title_ar: str
  - description_en: text
  - description_ar: text
  
  # Report Data
  - report_data: JSON (metrics, charts, etc.)
  - filters: JSON (frameworks, date range, etc.)
  
  # Output
  - output_format: Enum[PDF, HTML, JSON]
  - file_path: str (generated report location)
  
  # Metadata
  - generated_by: ForeignKey(User)
  - generated_at: datetime
  - report_period_start: date
  - report_period_end: date
```

#### 📄 reporting/schemas.py
**Purpose**: Reporting API schemas  
**Schemas**:
- `ReportGenerate`: Generate report request
- `ReportResponse`: Report metadata
- `DashboardMetrics`: Dashboard data structure
- `ReportTypeEnum`: Report type choices

#### 📄 reporting/router.py
**Purpose**: Reporting API endpoints  
**Endpoints**:
```python
GET    /reporting/dashboard      # Dashboard metrics (real-time)
POST   /reporting/generate       # Generate report
GET    /reporting/reports        # List generated reports
GET    /reporting/reports/{id}   # Get report details
DELETE /reporting/reports/{id}   # Delete report
GET    /reporting/reports/{id}/download  # Download report file
```

**Dashboard Metrics**:
```json
{
  "total_controls": {
    "ECC": 42,
    "CCC": 38,
    "PDPL": 28
  },
  "compliance_status": {
    "compliant": 65,
    "partial": 25,
    "non_compliant": 10,
    "not_applicable": 8
  },
  "priority_distribution": {
    "critical": 15,
    "high": 35,
    "medium": 45,
    "low": 13
  },
  "maturity_average": 3.2,
  "evidence_count": 234,
  "last_updated": "2026-02-08T06:00:00Z"
}
```

---

### 📁 privacy/ - PDPL Compliance

#### 📄 privacy/models.py
**Purpose**: Privacy compliance models  
**Models**:

```python
ConsentRecord:
  - id: UUID
  - data_subject_id: str (hashed identifier)
  - consent_type: Enum[
      marketing, analytics, profiling,
      third_party_sharing, automated_decision_making
    ]
  - consent_given: bool
  - consent_date: datetime
  - consent_method: str (web, email, in-person)
  - withdrawal_date: datetime (nullable)
  - language: str (ar/en)

DSARRequest:  # Data Subject Access Request
  - id: UUID
  - request_type: Enum[
      access,          # PDPL Art 12
      rectification,   # PDPL Art 13
      erasure,         # PDPL Art 14
      portability,     # PDPL Art 15
      objection,       # PDPL Art 16
      restriction      # PDPL Art 17
    ]
  - data_subject_id: str
  - request_date: datetime
  - response_date: datetime
  - status: Enum[pending, in_progress, completed, rejected]
  - notes: text

DataClassification:
  - id: UUID
  - data_type: str
  - classification_level: Enum[
      public,
      internal,
      confidential,
      restricted
    ]
  - retention_period_years: int
  - encryption_required: bool
```

#### 📄 privacy/schemas.py
**Purpose**: Privacy API schemas  
**Schemas**:
- `ConsentCreate`: Record consent
- `DSARCreate`: Submit DSAR
- `DSARUpdate`: Update DSAR status
- `DataClassificationResponse`: Classification info

#### 📄 privacy/router.py
**Purpose**: Privacy API endpoints  
**Endpoints**:
```python
POST   /privacy/consent          # Record consent
GET    /privacy/consent          # List consents
PUT    /privacy/consent/{id}     # Withdraw consent
POST   /privacy/dsar             # Submit DSAR
GET    /privacy/dsar             # List DSARs (admin)
PUT    /privacy/dsar/{id}        # Update DSAR status
GET    /privacy/classifications  # Data classification levels
```

---

### 📁 incident/ - Incident Management

#### 📄 incident/models.py
**Purpose**: Security incident models  
**Models**:

```python
SecurityIncident:
  - id: UUID
  - incident_id: str (unique, indexed) # INC-2026-001
  - severity: Enum[critical, high, medium, low]
  - category: Enum[
      data_breach,
      unauthorized_access,
      malware,
      phishing,
      ddos,
      insider_threat,
      physical_security,
      other
    ]
  
  # Timeline
  - detection_date: datetime
  - occurrence_date: datetime (estimated)
  - response_date: datetime
  - resolution_date: datetime
  - closure_date: datetime
  
  # Description
  - title_en: str
  - title_ar: str
  - description_en: text
  - description_ar: text
  
  # Impact Assessment
  - impact_assessment: JSON
  - affected_systems: list[str]
  - affected_data_types: list[str]
  - estimated_records_affected: int
  
  # Response
  - remediation_actions: JSON
  - affected_controls: list[str]
  
  # Assignment
  - reported_by: ForeignKey(User)
  - assigned_to: ForeignKey(User)
  - status: Enum[open, investigating, contained, resolved, closed]

IncidentResponse:
  - id: UUID
  - incident_id: ForeignKey(SecurityIncident)
  - response_type: str
  - action_taken: text
  - action_date: datetime
  - responder_id: ForeignKey(User)
  - effectiveness: Enum[effective, partially_effective, ineffective]
```

#### 📄 incident/schemas.py
**Purpose**: Incident API schemas  
**Schemas**:
- `IncidentCreate`: Report incident
- `IncidentUpdate`: Update incident status
- `IncidentResponse`: Incident details
- `ResponseCreate`: Record response action

#### 📄 incident/router.py
**Purpose**: Incident API endpoints  
**Endpoints**:
```python
POST   /incident                 # Report new incident
GET    /incident                 # List incidents
GET    /incident/{id}            # Incident details
PUT    /incident/{id}            # Update incident
POST   /incident/{id}/respond    # Record response action
GET    /incident/stats           # Incident statistics
```

---

### 📁 risk/ - Risk Management

#### 📄 risk/models.py
**Purpose**: Risk management models  
**Models**:

```python
Risk:
  - id: UUID
  - risk_id: str (unique, indexed) # RISK-2026-001
  - category: Enum[
      cybersecurity,
      operational,
      compliance,
      financial,
      reputational,
      strategic
    ]
  
  # Bilingual Content
  - title_en: str
  - title_ar: str
  - description_en: text
  - description_ar: text
  
  # Risk Assessment (NCA ECC-RM)
  - likelihood: int (1-5)
  - impact: int (1-5)
  - risk_score: int (calculated: likelihood × impact)
  - risk_level: Enum[critical, high, medium, low]
  
  # Control Mapping
  - affected_controls: list[str]
  - mitigating_controls: list[str]
  
  # Treatment
  - treatment_strategy: Enum[
      accept,
      mitigate,
      transfer,
      avoid
    ]
  - treatment_plan: text
  - mitigation_status: Enum[
      planned,
      in_progress,
      completed,
      monitoring
    ]
  
  # Ownership
  - risk_owner: ForeignKey(User)
  - identified_by: ForeignKey(User)
  - identified_date: datetime
  - review_date: datetime

RiskTreatment:
  - id: UUID
  - risk_id: ForeignKey(Risk)
  - action_description: text
  - responsible_party: ForeignKey(User)
  - target_completion_date: date
  - actual_completion_date: date
  - status: Enum[pending, in_progress, completed, overdue]
```

#### 📄 risk/schemas.py
**Purpose**: Risk API schemas  
**Schemas**:
- `RiskCreate`: Create risk
- `RiskUpdate`: Update risk
- `RiskResponse`: Risk details
- `RiskHeatmap`: Heatmap data structure

#### 📄 risk/router.py
**Purpose**: Risk API endpoints  
**Endpoints**:
```python
POST   /risk                     # Create risk
GET    /risk                     # List risks
GET    /risk/{id}                # Risk details
PUT    /risk/{id}                # Update risk
DELETE /risk/{id}                # Delete risk (admin)
GET    /risk/heatmap             # Risk heatmap (likelihood × impact)
GET    /risk/stats               # Risk statistics
```

---

### 📁 ai_governance/ - AI Model Governance

#### 📄 ai_governance/models.py
**Purpose**: AI governance models (SDAIA AI compliance)  
**Models**:

```python
AIModel:
  - id: UUID
  - model_id: str (unique) # GPT-SICO-001
  - model_name: str
  - model_version: str
  
  # Classification
  - model_type: Enum[
      classification,
      regression,
      nlp,
      computer_vision,
      generative,
      recommendation
    ]
  - use_case: str
  
  # Documentation (SDAIA Requirement)
  - purpose_en: text
  - purpose_ar: text
  - training_data_description_en: text
  - training_data_description_ar: text
  - limitations_en: text
  - limitations_ar: text
  
  # Bias & Ethics
  - bias_testing_completed: bool
  - bias_testing_date: datetime
  - bias_testing_results: JSON
  - fairness_metrics: JSON
  
  # Performance
  - accuracy_metrics: JSON
  - performance_benchmarks: JSON
  
  # Lifecycle
  - development_status: Enum[
      research,
      development,
      testing,
      production,
      retired
    ]
  - deployment_date: datetime
  - last_audit_date: datetime
  
  # Ownership
  - model_owner: ForeignKey(User)

ModelAudit:
  - id: UUID
  - model_id: ForeignKey(AIModel)
  - audit_date: datetime
  - auditor_id: ForeignKey(User)
  - audit_type: Enum[
      performance_review,
      bias_assessment,
      security_review,
      compliance_check
    ]
  - findings: text
  - recommendations: text
  - compliance_status: bool
```

#### 📄 ai_governance/schemas.py
**Purpose**: AI governance schemas  
**Schemas**:
- `AIModelCreate`: Register model
- `AIModelUpdate`: Update model info
- `AIModelResponse`: Model details
- `ModelAuditCreate`: Record audit

#### 📄 ai_governance/router.py
**Purpose**: AI governance endpoints  
**Endpoints**:
```python
POST   /ai-governance/models     # Register AI model
GET    /ai-governance/models     # List models
GET    /ai-governance/models/{id} # Model details
PUT    /ai-governance/models/{id} # Update model
POST   /ai-governance/audit      # Record audit
GET    /ai-governance/audit      # List audits
```

---

## 📁 src/frontend/ - Next.js Frontend

### Root Level Files

#### 📄 package.json
**Purpose**: Node.js dependencies and scripts  
**Key Dependencies**:
```json
{
  "dependencies": {
    "next": "14.1.0",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "next-intl": "3.6.0",       // i18n
    "axios": "1.6.5",           // HTTP client
    "swr": "2.2.4",             // Data fetching
    "@radix-ui/*": "latest",    // UI components
    "lucide-react": "^0.309.0", // Icons
    "recharts": "^2.10.3",      // Charts
    "tailwindcss": "3.4.1"      // Styling
  }
}
```

**Scripts**:
```bash
npm run dev         # Development server (localhost:3000)
npm run build       # Production build
npm run start       # Production server
npm run lint        # ESLint
npm test            # Jest tests
```

#### 📄 next.config.js
**Purpose**: Next.js configuration  
**Key Settings**:
- i18n: Disabled (using next-intl with App Router)
- API rewrites: `/api/*` → `http://localhost:8000/api/*`
- Image optimization: Enabled
- Strict mode: Enabled

#### 📄 tailwind.config.ts
**Purpose**: Tailwind CSS configuration  
**Custom Theme**:
```typescript
{
  colors: {
    primary: blue,
    secondary: gray,
    success: green,
    warning: yellow,
    error: red
  },
  fonts: {
    sans: ['Inter', 'Cairo', 'system-ui'],
    arabic: ['Cairo']
  }
}
```

#### 📄 tsconfig.json
**Purpose**: TypeScript configuration  
**Settings**:
- Target: ES2020
- Strict mode: Enabled
- Path aliases: `@/*` → `./src/*`

#### 📄 middleware.ts
**Purpose**: Next.js middleware for locale routing  
**Functionality**:
- Detects user locale (ar/en)
- Redirects root `/` to `/ar` (default)
- Maintains locale in URL during navigation

#### 📄 Dockerfile
**Purpose**: Frontend container image  
**Base Image**: `node:20-alpine`  
**Process**:
1. Copy package files
2. Install dependencies
3. Copy application code
4. Build Next.js application
5. Expose port 3000
6. Run Next.js production server

---

### 📁 app/ - Next.js App Router

#### 📄 app/layout.tsx
**Purpose**: Root layout component  
**Features**:
- Font loading (Inter for English, Cairo for Arabic)
- HTML lang attribute
- Global styles
- Metadata configuration

#### 📄 app/page.tsx
**Purpose**: Root page (redirects to /ar)  
**Functionality**:
```tsx
export default function RootPage() {
  redirect('/ar'); // Default to Arabic
}
```

---

### 📁 app/[locale]/ - Locale-Specific Routes

#### 📄 app/[locale]/layout.tsx
**Purpose**: Locale layout with navigation  
**Components**:
- `NextIntlClientProvider`: i18n context
- Navigation bar with language toggle
- RTL/LTR direction based on locale
- Font selection (Cairo for Arabic, Inter for English)

**Navigation Items**:
- Dashboard
- Controls
- Evidence
- Reports
- Settings

#### 📄 app/[locale]/page.tsx
**Purpose**: Home page  
**Features**:
- Welcome message (bilingual)
- Quick stats cards
- Navigation to key sections
- Recent activity

---

### 📁 app/[locale]/dashboard/ - Dashboard

#### 📄 app/[locale]/dashboard/page.tsx
**Purpose**: Executive compliance dashboard  
**Data Source**: `GET /api/v1/reporting/dashboard`  
**Sections**:

1. **Overview Cards**:
   - Total Controls
   - Compliance Rate
   - Evidence Count
   - Risk Score

2. **Compliance Status Chart** (Pie Chart):
   - Compliant
   - Partial Compliance
   - Non-Compliant
   - Not Applicable

3. **Framework Breakdown** (Bar Chart):
   - ECC controls
   - CCC controls
   - PDPL controls

4. **Priority Distribution** (Donut Chart):
   - Critical
   - High
   - Medium
   - Low

5. **Recent Activity Timeline**:
   - Control updates
   - Evidence uploads
   - Report generations

**Technologies**:
- SWR for data fetching
- Recharts for visualizations
- Tailwind for styling

---

### 📁 app/[locale]/controls/ - Controls Management

#### 📄 app/[locale]/controls/page.tsx
**Purpose**: Control framework browser  
**Data Source**: `GET /api/v1/controls?framework={f}&status={s}`  
**Features**:

1. **Filters**:
   - Framework selector (All, ECC, CCC, PDPL)
   - Status selector (All, Compliant, Partial, Non-Compliant, N/A)
   - Search box (control ID or title)

2. **Control Grid**:
   - Card layout
   - 3 columns on desktop, 1 on mobile
   - Hover effects

3. **Control Card**:
   ```
   ┌─────────────────────────────────────┐
   │ ECC-GV-1           [Compliant Badge]│
   │ إطار الحوكمة / Governance Framework│
   │                                     │
   │ Framework: ECC    Priority: Critical│
   │ Maturity: ★★★★☆                    │
   └─────────────────────────────────────┘
   ```

4. **Pagination**:
   - Load more button
   - Infinite scroll (optional)

**State Management**:
- useState for filters
- SWR for data fetching with caching
- URL query params for filter persistence

---

### 📁 lib/ - Utilities

#### 📄 lib/api-client.ts
**Purpose**: Configured Axios instance  
**Configuration**:
```typescript
const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor (add auth token)
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor (handle 401)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

---

### 📁 messages/ - i18n Translations

#### 📄 messages/ar.json
**Purpose**: Arabic translations  
**Structure**:
```json
{
  "nav": {
    "dashboard": "لوحة التحكم",
    "controls": "الضوابط",
    "evidence": "الأدلة",
    "reports": "التقارير",
    "settings": "الإعدادات"
  },
  "home": {
    "welcome": "مرحبًا بك في منصة SICO للحوكمة والمخاطر والامتثال",
    "subtitle": "إدارة الامتثال للضوابط السعودية (ECC/CCC/PDPL)"
  },
  "dashboard": {
    "title": "لوحة التحكم",
    "total_controls": "إجمالي الضوابط",
    "compliance_rate": "معدل الامتثال",
    "evidence_count": "عدد الأدلة",
    "risk_score": "درجة المخاطر"
  },
  "controls": {
    "title": "إدارة الضوابط",
    "filter_by_framework": "تصفية حسب الإطار",
    "filter_by_status": "تصفية حسب الحالة",
    "search": "البحث عن ضوابط...",
    "status": {
      "compliant": "متوافق",
      "partial": "توافق جزئي",
      "non_compliant": "غير متوافق",
      "not_applicable": "غير قابل للتطبيق"
    },
    "priority": {
      "critical": "حرج",
      "high": "عالي",
      "medium": "متوسط",
      "low": "منخفض"
    }
  }
}
```

#### 📄 messages/en.json
**Purpose**: English translations  
**Structure**: Same as Arabic but in English

---

## 📁 ai/ - AI/RAG Engine

### 📄 ai/requirements.txt
**Purpose**: AI-specific Python dependencies  
**Packages**:
```
langchain>=0.1.0
langchain-community>=0.0.20
sentence-transformers>=2.3.1
chromadb>=0.4.22
torch>=2.1.0
transformers>=4.36.0
```

### 📁 ai/rag/ - RAG Implementation

#### 📄 ai/rag/bilingual_retriever.py
**Purpose**: Core RAG retrieval engine  
**Class**: `BilingualRetriever`  
**Key Methods**:
```python
__init__(
    embedding_model: str = "intfloat/multilingual-e5-large",
    vector_db_path: str = "./vectordb"
)

retrieve(
    query: str,
    language: str = "ar",  # "ar" or "en"
    top_k: int = 5,
    framework_filter: Optional[List[str]] = None
) -> List[Dict[str, Any]]

add_documents(documents: List[Document])
```

**Features**:
- Multilingual embeddings (Arabic + English)
- Framework filtering (ECC, CCC, PDPL)
- Citation tracking (returns source control IDs)
- Relevance scoring

**Response Format**:
```python
[
  {
    "control_id": "ECC-GV-1",
    "framework": "ECC",
    "title": "إطار الحوكمة",
    "content": "...",
    "relevance_score": 0.87,
    "source": {
      "control_id": "ECC-GV-1",
      "section": "description"
    }
  }
]
```

#### 📄 ai/rag/chunker.py
**Purpose**: Document chunking for RAG  
**Strategy**:
- Split controls into logical sections:
  1. Policy guidance
  2. Procedure guidance
  3. Evidence requirements
- Preserve metadata (control_id, framework, etc.)
- Bilingual support

**Function**:
```python
def chunk_control(control: dict) -> List[Document]:
    """
    Converts a control into multiple Document chunks
    Each chunk represents a logical section
    """
```

---

## 📁 data/ - Regulatory Data

### 📁 data/controls/

#### 📄 data/controls/ecc_baseline.json
**Purpose**: ECC control definitions  
**Structure**:
```json
{
  "control_id": "ECC-GV-1",
  "framework": "ECC",
  "domain": "Governance",
  "title_en": "Governance Framework",
  "title_ar": "إطار الحوكمة",
  "description_en": "...",
  "description_ar": "...",
  "policy_guidance_en": "...",
  "policy_guidance_ar": "...",
  "procedure_guidance_en": "...",
  "procedure_guidance_ar": "...",
  "priority": "critical",
  "status": "compliant",
  "maturity_level": 4,
  "evidence_types": [
    "governance_policy",
    "organizational_chart"
  ],
  "related_controls": {
    "CCC": ["CCC-GOV-01"],
    "PDPL": ["PDPL-1"]
  }
}
```

**Domains**:
- Governance (GV)
- Information Security (IS)
- Risk Management (RM)
- Third Party Management (TP)
- Incident Management (IM)

---

### 📁 data/evidence/

#### 📄 data/evidence/evidence_catalog.json
**Purpose**: Master evidence catalog  
**Structure**:
```json
{
  "catalog_version": "1.0",
  "last_updated": "2026-02-04",
  "evidence_types": [
    {
      "evidence_id": "governance_policy",
      "name_en": "Governance Policy Document",
      "name_ar": "وثيقة سياسة الحوكمة",
      "description_en": "...",
      "description_ar": "...",
      "applicable_frameworks": ["ECC", "CCC"],
      "evidence_format": ["PDF", "DOCX"],
      "retention_period_years": 7,
      "collection_frequency": "annual"
    }
  ]
}
```

**Evidence Types**:
- governance_policy
- security_logs
- access_control_list
- risk_register
- incident_reports
- training_records
- audit_reports

---

### 📁 data/mappings/

#### 📄 data/mappings/ecc_to_ccc.json
**Purpose**: Cross-framework control mappings  
**Structure**:
```json
{
  "ECC-GV-1": ["CCC-GOV-01", "CCC-GOV-02"],
  "ECC-IS-1": ["CCC-SEC-01"],
  "ECC-IS-2": ["CCC-SEC-02", "CCC-SEC-03"],
  "ECC-RM-1": ["CCC-RISK-01"]
}
```

**Use Cases**:
- Eliminate duplicate controls
- Show control relationships
- Unified compliance view
- Delta analysis (CCC-specific controls)

---

## 📁 docs/ - Documentation

### 📁 docs/api/

#### 📄 docs/api/README.md
**Purpose**: API documentation  
**Contents**:
- Endpoint reference
- Request/response examples
- Authentication guide
- Error codes
- Rate limiting

---

### 📁 docs/architecture/

#### 📄 docs/architecture/README.md
**Purpose**: System architecture documentation  
**Contents**:
- High-level architecture
- Service boundaries
- Data flow diagrams
- Technology stack
- Design decisions

---

### 📁 docs/compliance/

#### 📄 docs/compliance/EXECUTIVE_SUMMARY.md
**Purpose**: Compliance status executive summary  
**Contents**:
- Overall compliance score (92%)
- Framework breakdown
- Critical findings
- Remediation timeline
- Regulatory risk assessment

#### 📄 docs/compliance/VALIDATION_REPORT.md
**Purpose**: Detailed compliance audit report  
**Contents**:
- Control-by-control assessment
- Gap analysis
- Evidence requirements
- Recommendations

#### 📄 docs/compliance/PHASE_2.1_REMEDIATION_PLAN.md
**Purpose**: Security remediation roadmap  
**Contents**:
- Phase 2.1 deliverables
- Implementation timeline
- Resource requirements
- Success criteria

#### 📄 docs/compliance/COMPLIANCE_STATUS_92_PERCENT.md
**Purpose**: Current compliance status details  
**Contents**:
- Completed phases (2.1, 2.2, 2.3, 2.4)
- Framework scores
- Implemented controls
- Outstanding items

---

### Security Documentation

#### 📄 docs/SECURITY_PIPELINE.md
**Purpose**: Security scanning setup  
**Contents**:
- Automated scans (SAST, dependency checks)
- GitHub Actions integration
- Report generation
- SARIF format

#### 📄 docs/SECURITY_README.md
**Purpose**: Security overview  
**Contents**:
- Security architecture
- Authentication/authorization
- Encryption
- Audit logging

#### 📄 docs/SECURITY_CHECKLIST.md
**Purpose**: Pre-deployment security checklist  
**Contents**:
- Configuration validation
- Key rotation
- TLS setup
- Backup procedures

---

### Phase Documentation

#### 📄 docs/PHASE_2.1_COMPLETE.md
**Purpose**: Phase 2.1 completion summary  
**Contents**:
- Critical security implementation
- JWT auth + RBAC
- Encryption
- Audit logging

#### 📄 docs/PHASE_2.2_2.3_COMPLETE.md
**Purpose**: Phase 2.2 & 2.3 completion summary  
**Contents**:
- Privacy module (PDPL)
- Incident & risk management
- AI governance
- SIEM integration

---

## 📁 scripts/ - Utility Scripts

### 📄 scripts/load_sample_data.py
**Purpose**: Populate database with sample data  
**Functionality**:
- Loads controls from `data/controls/`
- Loads evidence catalog
- Creates sample users
- Generates sample evidence records

**Usage**:
```bash
cd /home/runner/work/sanadcom/sanadcom
python scripts/load_sample_data.py
```

### 📄 scripts/setup_security.py
**Purpose**: Initialize security system  
**Functionality**:
- Creates RBAC roles and permissions
- Generates admin user
- Validates encryption keys
- Configures security policies

**Usage**:
```bash
python scripts/setup_security.py
```

### 📄 scripts/dev_setup.sh
**Purpose**: Development environment setup  
**Functionality**:
- Installs dependencies
- Starts Docker services
- Runs migrations
- Loads sample data

### 📄 scripts/check_conflicts.sh
**Purpose**: Check for merge conflicts  
**Usage**: Before merging branches

### 📄 scripts/setup_git_config.sh
**Purpose**: Configure Git for the project  
**Functionality**:
- Sets merge strategy
- Configures diff tool
- Sets up pre-commit hooks

---

## 📁 tests/ - Test Suites

### 📁 tests/backend/

#### 📄 tests/backend/test_api.py
**Purpose**: Backend API tests  
**Tests**:
- Health check endpoints
- Authentication flow
- CRUD operations
- Error handling

#### 📄 tests/backend/test_controls.py
**Purpose**: Controls module tests  
**Tests**:
- Create control
- Update control
- Filter controls
- Framework validation

#### 📄 tests/backend/test_evidence.py
**Purpose**: Evidence module tests  
**Tests**:
- Upload evidence
- Validate evidence
- File hash verification
- Retention period calculation

#### 📄 tests/backend/test_reporting.py
**Purpose**: Reporting module tests  
**Tests**:
- Dashboard metrics
- Report generation
- Data aggregation

---

### 📁 tests/ai/

#### 📄 tests/ai/test_rag.py
**Purpose**: AI/RAG system tests  
**Tests**:
- Bilingual retrieval
- Citation accuracy
- Framework filtering
- Relevance scoring

---

### 📄 tests/conftest.py
**Purpose**: Pytest configuration and fixtures  
**Fixtures**:
- `async_client`: Test HTTP client
- `db_session`: Test database session
- `test_user`: Sample user
- `test_control`: Sample control

---

## 📁 deployment/ - Deployment Configuration

### 📄 deployment/docker-compose.yml
**Purpose**: Local development environment  
**Services**:
1. **postgres**: PostgreSQL 15
2. **redis**: Redis 7
3. **chroma**: Chroma vector DB
4. **backend**: FastAPI application
5. **frontend**: Next.js application

**Network**: All services on `sico_network`  
**Volumes**: Persistent storage for database, Redis, Chroma

**Usage**:
```bash
cd /home/runner/work/sanadcom/sanadcom
docker-compose -f deployment/docker-compose.yml up -d
```

---

## Summary: Total Files & Directories

### File Count by Type
- **Python (.py)**: ~60 files
- **TypeScript (.ts, .tsx)**: ~15 files
- **JSON**: ~10 files
- **Markdown (.md)**: ~25 files
- **Configuration**: ~10 files

### Directory Count
- **Root directories**: 11
- **Backend modules**: 8
- **Total subdirectories**: ~40

### Lines of Code (Estimated)
- **Backend**: ~8,000 lines
- **Frontend**: ~3,000 lines
- **AI/RAG**: ~500 lines
- **Tests**: ~2,000 lines
- **Documentation**: ~5,000 lines

---

## Quick File Lookup

**Need to...**
- Change database connection? → `src/backend/core/database.py`
- Add API endpoint? → `src/backend/{module}/router.py`
- Update translations? → `src/frontend/messages/ar.json` or `en.json`
- Configure security? → `src/backend/core/config.py`
- Run migrations? → `src/backend/migrations/versions/`
- Add sample data? → `scripts/load_sample_data.py`
- View compliance status? → `docs/compliance/EXECUTIVE_SUMMARY.md`
- Configure deployment? → `deployment/docker-compose.yml`

---

**Last Updated**: 2026-02-08  
**Document Version**: 1.0
