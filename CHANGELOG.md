# SICO GRC Platform - Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.4] - 2026-02-04

### Security
- **CRITICAL**: Updated Next.js from 15.2.3 to 15.5.10 (fixes RCE in React flight protocol and multiple DoS vulnerabilities)

### Fixed
- All remaining security vulnerabilities resolved (0 alerts)
- All tests passing (8/8)

## [0.1.3] - 2026-02-04

### Security
- **CRITICAL**: Updated Next.js from 15.0.8 to 15.2.3 (fixes DoS via cache poisoning and authorization bypass vulnerabilities)

### Fixed
- All remaining security vulnerabilities resolved (0 alerts)
- All tests passing (8/8)

## [0.1.2] - 2026-02-04

### Security
- **CRITICAL**: Updated python-multipart from 0.0.20 to 0.0.22 (fixes arbitrary file write vulnerability)
- **CRITICAL**: Updated Next.js from 14.2.35 to 15.0.8 (fixes HTTP request deserialization DoS vulnerabilities)

### Fixed
- All remaining security vulnerabilities resolved (0 alerts)
- All tests passing (8/8)

## [0.1.1] - 2026-02-04

### Security
- **CRITICAL**: Updated fastapi from 0.109.0 to 0.115.6 (fixes ReDoS vulnerability)
- **CRITICAL**: Updated python-multipart from 0.0.6 to 0.0.20 (fixes arbitrary file write, DoS, and ReDoS vulnerabilities)
- **CRITICAL**: Updated transformers from 4.37.2 to 4.48.0 (fixes deserialization vulnerabilities)
- **CRITICAL**: Updated Next.js from 14.1.0 to 14.2.35 (fixes DoS, authorization bypass, cache poisoning, and SSRF vulnerabilities)

### Changed
- Updated pydantic from 2.5.3 to 2.10.5
- Updated uvicorn from 0.27.0 to 0.34.0
- Updated sqlalchemy from 2.0.25 to 2.0.36
- Updated langchain from 0.1.4 to 0.3.16
- Updated react from 18.2.0 to 18.3.1
- Updated axios from 1.6.5 to 1.7.9
- Updated various other dependencies to latest secure versions

### Fixed
- All security vulnerabilities resolved (0 alerts)
- All tests passing (8/8)
- No breaking changes

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
