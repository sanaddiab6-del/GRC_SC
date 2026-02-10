# 🔒 SICO GRC Platform - Security Pipeline

## Overview

The SICO GRC Platform implements a **comprehensive security scanning pipeline** that runs automatically on every commit and pull request. This pipeline is designed to meet **NCA ECC-IS-4** (Security Monitoring) and **PDPL Article 29** (Data Protection) requirements.

## Security Scans

### 1. Dependency Vulnerability Scanning
**Tools:** Safety (Python), npm audit (Node.js)
**Purpose:** Detect known vulnerabilities in third-party dependencies

**What it checks:**
- Python packages in `requirements.txt`
- Node.js packages in `package.json`
- CVEs (Common Vulnerabilities and Exposures) database

**Run locally:**
```bash
make security-deps
```

**Outputs:**
- `safety-report.json` - Python vulnerabilities
- `npm-audit.json` - Node.js vulnerabilities

---

### 2. Static Application Security Testing (SAST)
**Tools:** Bandit (Python), CodeQL (Python + JavaScript)
**Purpose:** Find security issues in source code (SQL injection, XSS, hardcoded secrets)

**What it checks:**
- SQL injection vulnerabilities
- Cross-site scripting (XSS) risks
- Insecure cryptography usage
- Hardcoded passwords/tokens
- Path traversal vulnerabilities

**Run locally:**
```bash
make security-sast
```

**Outputs:**
- `bandit-report.json` - Python SAST results
- SARIF files uploaded to GitHub Security tab

---

### 3. Secret Detection
**Tool:** Gitleaks
**Purpose:** Prevent hardcoded credentials from entering the codebase

**What it checks:**
- API keys (AWS, Azure, OpenAI, etc.)
- Database passwords
- Private keys (RSA, SSH)
- JWT tokens
- OAuth client secrets

**Run locally:**
```bash
make security-secrets
# Requires gitleaks: brew install gitleaks (macOS) or see https://github.com/gitleaks/gitleaks
```

**Outputs:**
- `gitleaks-report.json` - Detected secrets

---

### 4. Container Security Scanning (NEW)
**Tool:** Trivy
**Purpose:** Scan Docker images for OS and application vulnerabilities

**What it checks:**
- OS package vulnerabilities (Ubuntu base image)
- Python package vulnerabilities in containers
- Node.js package vulnerabilities in containers
- Configuration issues (running as root, exposed secrets)

**Run locally:**
```bash
make security-containers
# Requires trivy: brew install aquasecurity/trivy/trivy (macOS) or see https://aquasecurity.github.io/trivy/
```

**Outputs:**
- `trivy-backend.json` - Backend container scan
- `trivy-frontend.json` - Frontend container scan

---

### 5. Software Bill of Materials (SBOM) (NEW)
**Tool:** CycloneDX
**Purpose:** Generate machine-readable inventory of all dependencies

**What it includes:**
- Component name, version, license
- Dependency tree (transitive dependencies)
- Vulnerability references (CVEs)

**Run locally:**
```bash
make security-sbom
```

**Outputs:**
- `sbom-python.json` - Python dependencies
- `sbom-nodejs.json` - Node.js dependencies

**Use cases:**
- Supply chain risk management
- License compliance audits
- Vendor security questionnaires

---

## CI/CD Integration

### Automated Workflow
The security pipeline runs automatically on:
- **Every push** to `main`, `develop`, or `copilot/**` branches
- **Every pull request** to `main` or `develop`
- **Weekly schedule** (Mondays at 9 AM UTC)
- **Manual trigger** (via GitHub Actions UI)

### Workflow File
`.github/workflows/security-scanning.yml`

### Quality Gate (NEW)
The pipeline now includes a **quality gate** that:
- ✅ **PASSES** if no CRITICAL vulnerabilities found
- ⚠️ **WARNS** if >5 HIGH vulnerabilities found in containers
- ❌ **FAILS** if CRITICAL vulnerabilities found in containers

**Override:** If a vulnerability cannot be fixed immediately, document it in `SECURITY-ATTESTATION.md` with:
- Risk acceptance justification
- Mitigation plan
- Expiry date (max 90 days)
- Security lead approval

---

## How to Interpret Results

### Dependency Scan (Safety / npm audit)

**Example output:**
```json
{
  "vulnerabilities": [
    {
      "package": "requests",
      "installed_version": "2.25.0",
      "affected_version": "<2.26.0",
      "advisory": "CVE-2021-12345: SSRF vulnerability",
      "severity": "HIGH"
    }
  ]
}
```

**Action required:**
- **CRITICAL/HIGH:** Upgrade package immediately (`pip install --upgrade requests`)
- **MEDIUM:** Plan upgrade in next sprint
- **LOW:** Document and defer to backlog

---

### SAST (Bandit)

**Example output:**
```python
# Code
password = "hardcoded_password"  # SECURITY ISSUE

# Bandit finding
Issue: [B105:hardcoded_password_string] Possible hardcoded password: 'hardcoded_password'
Severity: Low   Confidence: Medium
Location: src/backend/auth.py:23
```

**Action required:**
- **HIGH:** Fix immediately (move to environment variables)
- **MEDIUM:** Review and fix if applicable
- **LOW:** Review; may be false positive (e.g., test fixtures)

---

### Secret Detection (Gitleaks)

**Example output:**
```json
{
  "Description": "AWS Access Key",
  "File": "config.py",
  "Line": "AWS_KEY = 'AKIAIOSFODNN7EXAMPLE'",
  "Commit": "abc123"
}
```

**Action required:**
- **IMMEDIATE:** Rotate the exposed secret (revoke old key, generate new one)
- Remove secret from code (use Azure Key Vault or environment variables)
- Rewrite Git history if secret is in commit history (`git filter-branch` or BFG Repo-Cleaner)

---

### Container Scan (Trivy)

**Example output:**
```json
{
  "Vulnerabilities": [
    {
      "VulnerabilityID": "CVE-2023-12345",
      "PkgName": "openssl",
      "InstalledVersion": "1.1.1f",
      "FixedVersion": "1.1.1g",
      "Severity": "CRITICAL"
    }
  ]
}
```

**Action required:**
- **CRITICAL:** Update base image or rebuild container with patched package
- **HIGH:** Plan update in current sprint
- **MEDIUM/LOW:** Monitor for fixes, update in next release

---

## False Positives

### How to Handle

1. **Verify it's actually a false positive** (consult with security team)
2. **Document in SECURITY-ATTESTATION.md**:
   - Why it's a false positive
   - Why the code is safe (e.g., "User input is sanitized before use")
3. **Suppress the finding** (use tool-specific syntax):

**Bandit:**
```python
# nosec B201 - False positive: User input is validated via Pydantic schema
user_input = request.json["data"]
```

**Trivy:**
```yaml
# .trivyignore
CVE-2023-12345  # False positive: Package not used in production code path
```

4. **Get approval** from security reviewer in PR

---

## Local Development Workflow

### Before Committing Code

```bash
# 1. Run pre-commit hooks (installs automatically run linters, secret detection)
pre-commit run --all-files

# 2. Run unit tests
cd src/backend && pytest tests/ -v
cd src/frontend && npm test

# 3. Run security scans
make security

# 4. Review scan results
cat bandit-report.json | jq '.results[] | select(.issue_severity=="HIGH")'

# 5. Fix any CRITICAL/HIGH issues

# 6. Commit and push
git add .
git commit -m "feat: Add new control mapping feature"
git push
```

---

### During Code Review

**Reviewer checklist:**
1. ✅ CI security scans passed (green checkmarks in PR)
2. ✅ No new CRITICAL/HIGH vulnerabilities introduced
3. ✅ Author completed [SECURITY-ATTESTATION.md](SECURITY-ATTESTATION.md) checklist
4. ✅ Any exceptions documented with risk acceptance + expiry date
5. ✅ Code follows secure coding practices (input validation, auth checks, audit logging)

---

## Security Metrics Dashboard

**Track weekly:**
| Metric | Target | How to Measure |
|--------|--------|----------------|
| CRITICAL vulnerabilities | 0 | GitHub Security tab → Code scanning alerts |
| HIGH vulnerabilities | <5 | Same as above |
| Secrets detected | 0 | Gitleaks report (fail build if any found) |
| SBOM freshness | <7 days old | Check `sbom-*.json` timestamp |
| Test coverage | >80% | pytest-cov report |
| Pre-commit hook usage | 100% | Enforce via branch protection rules |

---

## Compliance Mapping

| Scan Type | NCA ECC Control | PDPL Article | Purpose |
|-----------|----------------|--------------|---------|
| Dependency Scan | ECC-IS-4 (Security Monitoring) | PDPL Art. 29 (Data Protection) | Detect vulnerable libraries |
| SAST | ECC-IS-3 (Access Control) | PDPL Art. 24 (Security Measures) | Find code security flaws |
| Secret Detection | ECC-IS-2 (Cryptography) | PDPL Art. 29 | Prevent credential leakage |
| Container Scan | ECC-CCC-SEC-01 (Cloud Security) | PDPL Art. 25 (Data Residency) | Secure container images |
| SBOM | ECC-GV-6 (Third-Party Management) | PDPL Art. 26 (Processor Compliance) | Vendor risk management |

---

## Troubleshooting

### Issue: Safety scan fails with "Rate limit exceeded"

**Solution:**
```bash
# Use --db flag to specify local vulnerability database
cd src/backend
safety check --db ./safety-db.json
```

### Issue: Trivy scan times out

**Solution:**
```bash
# Increase timeout and use cached DB
trivy image --timeout 10m --skip-update sico-grc-backend:local
```

### Issue: False positive in Bandit

**Solution:**
Add `# nosec` comment with justification:
```python
# nosec B603 - Subprocess call is safe: input is validated via Pydantic
subprocess.run(["ls", validated_path])
```

---

## Resources

- **GitHub Security Tab:** https://github.com/sonaiso/sanadcom/security
- **Safety Database:** https://pyup.io/safety/
- **Bandit Rules:** https://bandit.readthedocs.io/en/latest/plugins/index.html
- **Gitleaks:** https://github.com/gitleaks/gitleaks
- **Trivy:** https://aquasecurity.github.io/trivy/
- **CycloneDX:** https://cyclonedx.org/
- **NCA ECC Controls:** https://nca.gov.sa/en/Pages/default.aspx
- **PDPL:** https://sdaia.gov.sa/en/PDPL/Pages/default.aspx

---

**Last Updated:** 2026-02-10  
**Version:** 2.0 (Enhanced with Container Scanning + SBOM)  
**Owner:** SICO GRC Security Team
