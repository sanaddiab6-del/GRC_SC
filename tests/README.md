# Tests

## SICO GRC Platform - Test Suite

This directory contains all tests for the SICO GRC Platform.

## Test Structure

```
tests/
├── backend/                # Backend API tests
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── api/               # API endpoint tests
├── frontend/              # Frontend UI tests
│   ├── unit/              # Component unit tests
│   ├── integration/       # Integration tests
│   └── e2e/               # End-to-end tests
├── ai/                    # AI/ML tests
│   ├── rag/               # RAG pipeline tests
│   ├── embeddings/        # Embedding tests
│   └── dictionary/        # Dictionary engine tests
└── fixtures/              # Test fixtures and data
```

## Running Tests

### Backend Tests
```bash
cd src/backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd src/frontend
npm test
```

### All Tests
```bash
./scripts/run-tests.sh all
```

## Test Coverage

Target: 80% code coverage minimum

### Current Coverage
- Backend: TBD
- Frontend: TBD
- AI/ML: TBD

## Test Data

Test fixtures and mock data are located in `/tests/fixtures/`

---

**Last Updated**: February 2026
