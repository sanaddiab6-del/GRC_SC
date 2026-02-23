# Tests

This directory contains the test suite for the SICO GRC Platform.
## SICO GRC Platform - Test Suite

This directory contains all tests for the SICO GRC Platform.

## Test Structure

```
tests/
├── test_api.py              # API endpoint tests
├── test_controls.py         # Control management tests
├── test_evidence.py         # Evidence management tests
├── test_pdpl.py            # PDPL register tests
├── test_soc_integration.py # SOC-GRC bridge tests
└── test_ai.py              # AI/RAG engine tests
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

### All Tests
```bash
pytest
```

### Specific Test File
```bash
pytest tests/test_api.py
```

### With Coverage
```bash
pytest --cov=app --cov-report=html
```

### Specific Test
```bash
pytest tests/test_api.py::test_root_endpoint
```

## Test Categories

### Unit Tests
Test individual functions and methods in isolation.

```bash
pytest -m unit
```

### Integration Tests
Test interaction between components.

```bash
pytest -m integration
```

### End-to-End Tests
Test complete user workflows.

```bash
pytest -m e2e
```

## Writing Tests

Follow these guidelines when writing tests:

1. **Naming**: Use descriptive test names starting with `test_`
2. **Arrange-Act-Assert**: Structure tests clearly
3. **Isolation**: Tests should not depend on each other
4. **Fixtures**: Use pytest fixtures for common setup
5. **Mocking**: Mock external dependencies

Example:
```python
def test_control_creation():
    # Arrange
    control_data = {...}
    
    # Act
    response = client.post("/api/v1/controls", json=control_data)
    
    # Assert
    assert response.status_code == 201
    assert response.json()["id"] is not None
```

## CI/CD Integration

Tests run automatically on:
- Pull request creation
- Push to main branch
- Scheduled daily runs

## Coverage Requirements

- Minimum coverage: 80%
- Critical paths: 95%+
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
