# 🧪 SICO GRC Platform - Testing & Quality Assurance Guide

## Testing Strategy

### Testing Pyramid

```
        /\
       /  \      E2E Tests (10%)
      /____\     
     /      \    Integration Tests (30%)
    /________\   
   /          \  Unit Tests (60%)
  /__________  \
```

### Test Coverage Goals

- **Unit Tests**: 80% code coverage minimum
- **Integration Tests**: All API endpoints
- **E2E Tests**: Critical user journeys
- **Performance Tests**: Load capacity validation
- **Security Tests**: OWASP Top 10 compliance

---

## 1. Unit Testing

### Backend Unit Tests (pytest)

**Location**: `tests/backend/`

**Run All Tests**:
```bash
cd src/backend
pytest tests/ -v --cov=. --cov-report=html
```

**Run Specific Module**:
```bash
pytest tests/backend/test_auth.py -v
pytest tests/backend/test_controls.py -v
pytest tests/backend/test_evidence.py -v
```

**Run with Coverage**:
```bash
pytest --cov=src/backend --cov-report=term-missing
```

**Test Structure**:
```python
# tests/backend/test_example.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_endpoint(client: AsyncClient):
    """Test description"""
    response = await client.get("/api/v1/endpoint")
    assert response.status_code == 200
    assert response.json()["key"] == "value"
```

### Frontend Unit Tests (Jest)

**Location**: `src/frontend/__tests__/`

**Run All Tests**:
```bash
cd src/frontend
npm test
```

**Run with Coverage**:
```bash
npm test -- --coverage
```

**Watch Mode** (during development):
```bash
npm test -- --watch
```

---

## 2. Integration Testing

### API Integration Tests

**Test Authentication Flow**:
```bash
# Register user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!",
    "full_name": "Test User"
  }'

# Login
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }' | jq -r '.access_token')

# Test authenticated endpoint
curl -H "Authorization: ****** http://localhost:8000/api/v1/controls
```

### Database Integration Tests

```python
# tests/backend/test_database_integration.py
import pytest
from src.backend.core.database import AsyncSessionLocal
from src.backend.auth.models import User

@pytest.mark.asyncio
async def test_user_creation_and_retrieval():
    """Test full database CRUD cycle"""
    async with AsyncSessionLocal() as session:
        # Create
        user = User(
            email="integration@test.com",
            password_hash="hashed",
            full_name="Integration Test"
        )
        session.add(user)
        await session.commit()
        
        # Retrieve
        result = await session.execute(
            select(User).where(User.email == "integration@test.com")
        )
        retrieved_user = result.scalar_one()
        
        assert retrieved_user.email == "integration@test.com"
```

---

## 3. Load Testing

### Setup (Locust)

**Install**:
```bash
pip install locust
```

**Create Load Test** (`tests/load/locustfile.py`):
```python
from locust import HttpUser, task, between

class SICOUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login before tests"""
        response = self.client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "TestPass123!"
        })
        self.token = response.json()["access_token"]
        self.client.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(3)
    def list_controls(self):
        """Most common operation"""
        self.client.get("/api/v1/controls")
    
    @task(2)
    def view_control_details(self):
        """View specific control"""
        self.client.get("/api/v1/controls/ECC-GV-1")
    
    @task(1)
    def generate_report(self):
        """Less frequent operation"""
        self.client.post("/api/v1/reporting/generate", json={
            "report_type": "compliance_summary"
        })
```

### Run Load Test

**Development Test** (10 users):
```bash
locust -f tests/load/locustfile.py --host=http://localhost:8000 \
  --users 10 --spawn-rate 2 --run-time 5m --headless
```

**Production Simulation** (500 users):
```bash
locust -f tests/load/locustfile.py --host=https://your-domain.com \
  --users 500 --spawn-rate 10 --run-time 30m --headless \
  --csv=load_test_results
```

**Access Web UI**:
```bash
locust -f tests/load/locustfile.py --host=http://localhost:8000
# Open browser to http://localhost:8089
```

### Load Test Targets

| Metric | Target | Acceptable |
|--------|--------|------------|
| Response Time (p95) | < 500ms | < 1000ms |
| Response Time (p99) | < 1000ms | < 2000ms |
| Throughput | > 100 req/s | > 50 req/s |
| Error Rate | < 0.1% | < 1% |
| Concurrent Users | 500 | 250 |

### Analyzing Results

```bash
# View results
cat load_test_results_stats.csv

# Key metrics to check:
# - Request Count: Should be high
# - Failure %: Should be < 1%
# - Average Response Time: Should be < 500ms
# - Max Response Time: Should be < 2s
```

---

## 4. Security Testing

### OWASP ZAP (Automated Security Scan)

**Install**:
```bash
docker pull owasp/zap2docker-stable
```

**Run Baseline Scan**:
```bash
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t https://your-domain.com \
  -r zap_report.html
```

**Run Full Scan**:
```bash
docker run -t owasp/zap2docker-stable zap-full-scan.py \
  -t https://your-domain.com \
  -r zap_full_report.html
```

### Manual Security Tests

**1. SQL Injection Test**:
```bash
# Test control search
curl "http://localhost:8000/api/v1/controls?search=' OR '1'='1"
# Should return 400 Bad Request (input validation)
```

**2. XSS Test**:
```bash
# Test control title
curl -X POST http://localhost:8000/api/v1/controls \
  -H "Authorization: ****** \
  -H "Content-Type: application/json" \
  -d '{
    "title_en": "<script>alert('XSS')</script>",
    "control_id": "TEST-1"
  }'
# Should be sanitized
```

**3. Authentication Bypass Test**:
```bash
# Try accessing protected endpoint without token
curl http://localhost:8000/api/v1/controls
# Should return 401 Unauthorized
```

**4. Brute Force Test**:
```bash
# Multiple failed logins
for i in {1..6}; do
  curl -X POST http://localhost:8000/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"wrong"}'
done
# Should trigger account lockout after 5 attempts
```

**5. Rate Limiting Test**:
```bash
# Rapid requests
for i in {1..100}; do
  curl http://localhost:8000/api/v1/health &
done
wait
# Should trigger rate limiting after 60 requests/minute
```

### Security Checklist

- [ ] All sensitive data encrypted (TLS + field-level)
- [ ] JWT tokens securely generated and validated
- [ ] SQL injection protection active
- [ ] XSS protection enabled
- [ ] CSRF protection for state-changing operations
- [ ] Rate limiting configured
- [ ] Security headers present (HSTS, CSP, X-Frame-Options)
- [ ] Account lockout after failed logins
- [ ] Audit logging for all actions
- [ ] No secrets in logs or error messages

---

## 5. Penetration Testing

### Pre-Engagement

**Scope Definition**:
- Target: Production environment
- Duration: 1 week
- Out of Scope: DoS attacks, social engineering
- Notification: 48 hours before start

### Testing Methodology

Follow OWASP Testing Guide v4:

1. **Information Gathering**
   - Identify technologies
   - Map application
   - Discover hidden endpoints

2. **Configuration Testing**
   - SSL/TLS configuration
   - HTTP headers
   - File permissions

3. **Authentication Testing**
   - Password policy
   - Session management
   - Account lockout

4. **Authorization Testing**
   - RBAC enforcement
   - Privilege escalation
   - Insecure direct object references

5. **Input Validation**
   - SQL injection
   - XSS
   - Command injection

6. **Business Logic**
   - Workflow bypass
   - Data tampering
   - Race conditions

### Automated Penetration Testing

**Using Nikto**:
```bash
nikto -h https://your-domain.com -ssl -output nikto_report.txt
```

**Using SQLMap**:
```bash
sqlmap -u "http://localhost:8000/api/v1/controls?search=test" \
  --batch --level=5 --risk=3
```

### Reporting

Pentest report should include:
- Executive summary
- Findings by severity (Critical, High, Medium, Low)
- Proof of concept for each finding
- Remediation recommendations
- Retest results

---

## 6. Compliance Testing

### NCA ECC Compliance

**Authentication (ECC-IS-3)**:
```bash
# Verify JWT implementation
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123!"}'
# Should return JWT token

# Verify token validation
curl -H "Authorization: ******-INVALID" \
  http://localhost:8000/api/v1/controls
# Should return 401
```

**Audit Logging (ECC-IS-5)**:
```bash
# Perform action
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123!"}'

# Verify audit log created
docker compose exec postgres psql -U sico_admin -d sico_grc -c \
  "SELECT * FROM audit_logs WHERE action='login' ORDER BY timestamp DESC LIMIT 1;"
# Should show recent login event
```

### PDPL Compliance

**Consent Management (PDPL Article 6)**:
```bash
# Record consent
curl -X POST http://localhost:8000/api/v1/privacy/consent \
  -H "Authorization: ******" \
  -H "Content-Type: application/json" \
  -d '{
    "data_subject_id": "user123",
    "consent_type": "marketing",
    "consent_given": true
  }'

# Verify consent recorded
curl -H "Authorization: ******" \
  http://localhost:8000/api/v1/privacy/consent?data_subject_id=user123
# Should return consent record
```

**Data Encryption (PDPL Article 29)**:
```bash
# Check PII fields are encrypted in database
docker compose exec postgres psql -U sico_admin -d sico_grc -c \
  "SELECT email FROM users LIMIT 1;"
# Should show encrypted value (base64 encoded ciphertext)
```

---

## 7. End-to-End Testing

### E2E Test Framework (Playwright)

**Install**:
```bash
cd src/frontend
npm install -D @playwright/test
npx playwright install
```

**Create E2E Test** (`tests/e2e/auth.spec.ts`):
```typescript
import { test, expect } from '@playwright/test';

test('User can login and view dashboard', async ({ page }) => {
  // Navigate to login page
  await page.goto('https://localhost:3000/ar/login');
  
  // Fill in credentials
  await page.fill('input[name="email"]', 'admin@example.com');
  await page.fill('input[name="password"]', 'AdminPass123!');
  
  // Click login
  await page.click('button[type="submit"]');
  
  // Wait for redirect to dashboard
  await page.waitForURL('**/dashboard');
  
  // Verify dashboard loaded
  await expect(page.locator('h1')).toContainText('لوحة التحكم'); // Arabic
  
  // Verify metrics visible
  await expect(page.locator('[data-testid="total-controls"]')).toBeVisible();
});

test('User can filter controls', async ({ page }) => {
  // Login first (can use beforeEach for this)
  await page.goto('https://localhost:3000/ar/controls');
  
  // Select framework filter
  await page.selectOption('select[name="framework"]', 'ECC');
  
  // Verify URL updated
  await expect(page).toHaveURL(/framework=ECC/);
  
  // Verify filtered results
  const controlCards = page.locator('[data-testid="control-card"]');
  await expect(controlCards.first()).toContainText('ECC');
});
```

**Run E2E Tests**:
```bash
npx playwright test
npx playwright test --headed  # With browser UI
npx playwright test --debug   # Debug mode
```

### Critical User Journeys

Test these flows end-to-end:

1. **Authentication Flow**:
   - Register → Email verification → Login → Dashboard

2. **Control Management Flow**:
   - View controls → Filter by framework → View details → Update status

3. **Evidence Upload Flow**:
   - Select control → Upload evidence → Validate → Download

4. **Report Generation Flow**:
   - Select report type → Configure filters → Generate → Download

5. **DSAR Flow**:
   - Submit DSAR → Admin processes → User receives response

---

## 8. Continuous Testing (CI/CD)

### GitHub Actions Workflow

**`.github/workflows/test.yml`**:
```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd src/backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd src/backend
          pytest tests/ -v --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Node
        uses: actions/setup-node@v3
        with:
          node-version: '20'
      - name: Install dependencies
        run: |
          cd src/frontend
          npm ci
      - name: Run tests
        run: |
          cd src/frontend
          npm test -- --coverage
          
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Bandit
        run: |
          pip install bandit
          bandit -r src/backend -f json -o bandit-report.json
      - name: Run npm audit
        run: |
          cd src/frontend
          npm audit --json > npm-audit.json
```

### Pre-Commit Hooks

**`.pre-commit-config.yaml`**:
```yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        types: [python]
        pass_filenames: false
        always_run: true
        args: [tests/backend/, -v]
        
      - id: bandit
        name: bandit
        entry: bandit
        language: system
        types: [python]
        args: [-r, src/backend]
```

---

## 9. Test Data Management

### Test Data Setup

```python
# tests/conftest.py
import pytest
from src.backend.core.database import Base, engine

@pytest.fixture(scope="session")
async def setup_test_db():
    """Create test database schema"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def test_user(db_session):
    """Create test user"""
    user = User(
        email="test@example.com",
        password_hash=hash_password("TestPass123!"),
        full_name="Test User"
    )
    db_session.add(user)
    await db_session.commit()
    return user
```

### Test Data Cleanup

```python
@pytest.fixture(autouse=True)
async def cleanup(db_session):
    """Cleanup after each test"""
    yield
    # Rollback any uncommitted transactions
    await db_session.rollback()
```

---

## 10. Test Reporting

### Coverage Report

```bash
# Generate HTML coverage report
pytest --cov=src/backend --cov-report=html
open htmlcov/index.html
```

### Test Results Dashboard

Use tools like:
- **Allure**: Beautiful test reports
- **pytest-html**: Simple HTML reports
- **Codecov**: Coverage tracking over time

```bash
# Install Allure
pip install allure-pytest

# Run tests with Allure
pytest --alluredir=allure-results

# Generate report
allure serve allure-results
```

---

## Testing Checklist (Pre-Release)

- [ ] All unit tests passing (80%+ coverage)
- [ ] All integration tests passing
- [ ] Load test completed (500 concurrent users)
- [ ] Security scan passed (no high/critical issues)
- [ ] Penetration test completed and remediated
- [ ] E2E tests for critical journeys passing
- [ ] Performance benchmarks met
- [ ] Compliance tests validated
- [ ] Test reports reviewed and approved
- [ ] Regression testing completed

---

**Document Version**: 1.0  
**Last Updated**: 2026-02-10  
**Review Schedule**: Before each release
