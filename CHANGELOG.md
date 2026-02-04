# SICO GRC Platform - Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-04

### Added
- Initial project structure and setup
- Backend FastAPI application with core endpoints
- Frontend Next.js application with landing page
- Docker and Docker Compose configuration
- Configuration management (env.example, settings.yaml)
- .gitignore for Python and Node.js
- MIT License

#### Control Library (Deliverable 1)
- ECC control structure (ecc-controls.yaml)
- CCC control structure (ccc-controls.yaml)
- PDPL control structure (pdpl-controls.yaml)
- Sample controls for each framework

#### Mappings (Deliverable 2)
- ECC ↔ CCC baseline mapping (ecc-ccc-baseline.yaml)
- Mapping statistics and recommendations

#### Evidence Management (Deliverable 4)
- Evidence master catalog (catalog.yaml)
- Evidence categories and types
- Template definitions

#### API Endpoints
- Root endpoint (/)
- Health check endpoint (/health)
- Framework listing (/api/v1/frameworks)
- Control listing with filtering (/api/v1/controls/)
- Control detail retrieval (/api/v1/controls/{control_id})
- Assessment listing (/api/v1/assessments/)
- Compliance dashboard (/api/v1/assessments/dashboard)

#### Documentation
- README.md with comprehensive project overview
- Architecture overview (docs/architecture/overview.md)
- Installation guide (docs/user-guides/installation.md)
- Getting started guide (docs/user-guides/getting-started.md)
- API documentation (docs/api/README.md)
- Deliverable documentation (docs/deliverables/)

#### Scripts & Tools
- Setup script (scripts/setup.sh)
- API tests (tests/test_api.py)

### Development Setup
- Python virtual environment support
- Node.js package management
- Backend with FastAPI and Uvicorn
- Frontend with Next.js 14 and React
- Tailwind CSS for styling
- PostgreSQL and Redis integration ready

### Known Issues
- Database migrations not yet implemented
- Frontend dashboard not yet connected to backend
- AI/RAG features not yet implemented
- Authentication not yet implemented

## [Unreleased]

### Planned
- Complete all 114 ECC controls
- Complete all 180 CCC controls
- Complete all 42 PDPL controls
- Database schema and migrations
- User authentication and authorization
- Frontend dashboard implementation
- AI/RAG integration
- Bilingual content completion
- SICO Packs (Deliverable 6)
- Executive reporting (Deliverable 7)
- SOC-GRC bridge (Deliverable 8)
- Delivery playbooks (Deliverable 12)
