# CI/CD Security Pipeline Documentation

## 🔐 Automated Security Scanning & Artifact Generation

**Platform**: SICO GRC Platform  
**Compliance**: NCA ECC, CCC, PDPL Standards  
**Version**: 1.0

This document describes the automated security scanning and artifact generation pipeline implemented in the SICO GRC Platform CI/CD workflow.

---

## 📋 Overview

The security pipeline automatically:
- Generates Software Bill of Materials (SBOM)
- Performs static application security testing (SAST)
- Scans dependencies for vulnerabilities
- Scans container images for security issues
- Analyzes code with CodeQL
- Enforces quality gates (fail on HIGH/CRITICAL)
- Generates comprehensive security reports
- Maintains traceability and attestations

---

## 🔄 Workflow Triggers

The security scan workflow runs on:

### Automatic Triggers
- **Push to main/develop branches**: Full security scan
- **Pull requests**: Full scan + dependency review
- **Daily schedule**: 2 AM UTC (security maintenance scan)

### Manual Trigger
- **Workflow dispatch**: On-demand security scan via GitHub Actions UI

```yaml
on:
  push:
    branches: [ main, develop, 'release/**' ]
  pull_request:
    branches: [ main, develop ]
  schedule:
    - cron: '0 2 * * *'
  workflow_dispatch:
```

---

## 🏗️ Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Trigger Event                            │
│  (Push / Pull Request / Schedule / Manual)                  │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│              Job 1: Generate SBOM                           │
│  • Python dependencies (SPDX)                               │
│  • Node.js dependencies (SPDX)                              │
│  • CycloneDX format                                         │
└─────────────────┬───────────────────────────────────────────┘
                  │
        ┌─────────┴──────────┬──────────────┬─────────────┐
        ▼                    ▼              ▼             ▼
┌──────────────┐  ┌──────────────┐  ┌─────────────┐  ┌──────────────┐
│ Job 2:       │  │ Job 3:       │  │ Job 4:      │  │ Job 5:       │
│ Python       │  │ Node.js      │  │ Container   │  │ CodeQL       │
│ Security     │  │ Security     │  │ Security    │  │ Analysis     │
│              │  │              │  │             │  │              │
│ • Bandit     │  │ • npm audit  │  │ • Trivy     │  │ • Python     │
│ • Safety     │  │              │  │ • SARIF     │  │ • JavaScript │
│ • pip-audit  │  │              │  │ • JSON      │  │              │
└──────┬───────┘  └──────┬───────┘  └──────┬──────┘  └──────┬───────┘
       │                 │                  │                │
       └─────────────────┴──────────────────┴────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │ Job 6:                 │
                    │ Security Summary       │
                    │ • Aggregate results    │
                    │ • Generate report      │
                    │ • Post to PR           │
                    └────────────────────────┘
```

---

## 📦 Jobs Breakdown

### Job 1: Generate SBOM

**Purpose**: Create Software Bill of Materials for all dependencies

**Tools**:
- Anchore SBOM Action (SPDX format)
- CycloneDX Python Generator

**Outputs**:
- `sbom-backend-python.spdx.json` - Python dependencies (SPDX)
- `sbom-frontend-nodejs.spdx.json` - Node.js dependencies (SPDX)
- `sbom-backend-cyclonedx.json` - Backend (CycloneDX)

**NCA Compliance**: ECC 2-5-1, PDPL Article 20

### Job 2: Python Security Scan

**Purpose**: Analyze Python code and dependencies for security issues

**Tools**:
- **Bandit**: Python SAST (Static Application Security Testing)
- **Safety**: Known vulnerability database for Python packages
- **pip-audit**: Python package auditing tool

**Outputs**:
- `bandit-report.json` - Detailed security findings
- `bandit-report.sarif` - SARIF format for GitHub Security
- `safety-report.json` - Vulnerability findings
- `pip-audit-report.json` - Package audit results

**Quality Gate**: ⛔ Fails on HIGH or CRITICAL severity

**NCA Compliance**: ECC 2-5-1, ECC 2-5-2

### Job 3: Node.js Security Scan

**Purpose**: Scan Node.js dependencies for vulnerabilities

**Tools**:
- **npm audit**: Built-in Node.js security auditing

**Outputs**:
- `npm-audit-report.json` - Vulnerability report

**Quality Gate**: ⛔ Fails on HIGH severity vulnerabilities

**NCA Compliance**: ECC 2-5-1, ECC 2-3-1

### Job 4: Container Security Scan

**Purpose**: Scan container filesystems and images for vulnerabilities

**Tools**:
- **Trivy**: Comprehensive vulnerability scanner
  - OS packages
  - Language dependencies
  - Misconfigurations
  - License scanning

**Outputs**:
- `trivy-backend-results.sarif` - Backend scan (SARIF)
- `trivy-frontend-results.sarif` - Frontend scan (SARIF)
- `trivy-backend-report.json` - Backend details (JSON)
- `trivy-frontend-report.json` - Frontend details (JSON)

**Quality Gate**: ⛔ Fails on HIGH or CRITICAL vulnerabilities

**NCA Compliance**: ECC 2-3-1, CCC 3-2-1

### Job 5: CodeQL Analysis

**Purpose**: Deep semantic code analysis for security vulnerabilities

**Tools**:
- **GitHub CodeQL**: Advanced static analysis

**Languages Analyzed**:
- Python
- JavaScript/TypeScript

**Queries**:
- Security-extended query pack
- Security-and-quality query pack

**Outputs**:
- Results uploaded to GitHub Security tab
- SARIF files for each language

**NCA Compliance**: ECC 2-5-1

### Job 6: Security Summary

**Purpose**: Aggregate all security scan results into comprehensive report

**Outputs**:
- `security-summary.md` - Executive summary
  - Scan status for all jobs
  - List of generated artifacts
  - NCA compliance mapping
  - Quality gate results
  - Traceability information
  - Links to detailed reports

**Actions**:
- Upload summary as artifact
- Post comment on Pull Request (if applicable)
- Generate GitHub Step Summary

---

## 🔍 Quality Gates

### Gate Policy

**FAIL** on:
- ⛔ CRITICAL severity vulnerabilities
- ⛔ HIGH severity vulnerabilities

**WARN** on:
- ⚠️  MEDIUM severity vulnerabilities (requires manual review)

**INFO** on:
- ℹ️  LOW severity vulnerabilities (tracked, no block)

### Gate Implementation

```python
# Example gate logic
has_critical = False

for vulnerability in scan_results:
    if vulnerability.severity in ['HIGH', 'CRITICAL']:
        print(f"❌ Found {vulnerability.severity} vulnerability")
        has_critical = True

if has_critical:
    print("⛔ SECURITY GATE FAILED")
    sys.exit(1)  # Fail the build
else:
    print("✅ Security gate passed")
```

### Gate Exceptions

Quality gate failures can be overridden by:
1. Security team approval (documented exception)
2. False positive verification
3. Accepted risk with mitigation plan

**All exceptions must be documented and reviewed monthly**

---

## 📊 Artifacts Generated

### Artifact Retention

All artifacts are stored for **90 days** in GitHub Actions.

### Artifact Types

| Artifact Name | Contents | Format | Size (Approx) |
|--------------|----------|--------|---------------|
| `sbom-reports` | All SBOM files | SPDX, CycloneDX | 10-50 KB |
| `python-security-reports` | Python scan results | JSON, SARIF | 50-200 KB |
| `nodejs-security-reports` | Node.js audit results | JSON | 10-50 KB |
| `trivy-scan-results` | Container scan results | JSON, SARIF | 100-500 KB |
| `security-summary-report` | Executive summary | Markdown | 5-10 KB |

### Downloading Artifacts

**Via GitHub UI**:
1. Go to Actions tab
2. Select workflow run
3. Scroll to Artifacts section
4. Click to download

**Via GitHub CLI**:
```bash
# List artifacts for a run
gh run view <RUN_ID>

# Download specific artifact
gh run download <RUN_ID> --name sbom-reports

# Download all artifacts
gh run download <RUN_ID>
```

**Via API**:
```bash
curl -H "Authorization: token $GITHUB_TOKEN" \
  -L https://api.github.com/repos/sonaiso/sanadcom/actions/artifacts/<ARTIFACT_ID>/zip \
  -o artifact.zip
```

---

## 🎯 NCA Compliance Mapping

### Essential Cybersecurity Controls (ECC)

| Control ID | Control Name | Implementation | Evidence |
|-----------|-------------|----------------|----------|
| **ECC 2-3-1** | Malware Protection | Container & dependency scanning | Trivy reports, npm audit |
| **ECC 2-5-1** | Vulnerability Assessment | Automated scanning in CI/CD | All SARIF/JSON reports |
| **ECC 2-5-2** | Vulnerability Remediation | Quality gates block HIGH/CRITICAL | Workflow logs, gate status |

### Cloud Cybersecurity Controls (CCC)

| Control ID | Control Name | Implementation | Evidence |
|-----------|-------------|----------------|----------|
| **CCC 3-2-1** | Secure Configuration | Container image scanning | Trivy scan results |

### Personal Data Protection Law (PDPL)

| Article | Requirement | Implementation | Evidence |
|---------|-------------|----------------|----------|
| **Article 20** | Security Measures | Comprehensive security scanning & SBOM | All artifacts |

---

## 🔗 Traceability

Every build includes:

### Build Provenance
- Workflow name and version
- Run ID and run number
- Git commit SHA
- Git branch/tag
- Build timestamp
- Actor (who triggered)
- Trigger event

### Artifact Traceability
- SHA256 checksums for all artifacts
- File sizes
- Generation timestamps
- Links to workflow run
- Compliance control mappings

### Attestation
- Complete attestation document (JSON)
- Links all artifacts to build
- Documents compliance status
- Available via `scripts/generate-attestation.py`

---

## 🚀 Usage

### Running Manually

1. Go to repository on GitHub
2. Click "Actions" tab
3. Select "Security Scanning & Artifact Generation"
4. Click "Run workflow"
5. Select branch
6. Click "Run workflow" button

### Viewing Results

**Security Tab**:
- Go to repository "Security" tab
- View CodeQL analysis results
- Check Dependabot alerts
- Review security advisories

**Actions Tab**:
- View workflow run status
- Download artifacts
- Review job logs
- Check step summaries

### Interpreting Results

**Green ✅**: All scans passed, no critical issues

**Yellow ⚠️**: Medium severity issues found (review recommended)

**Red ❌**: HIGH/CRITICAL issues found (deployment blocked)

---

## 🔧 Maintenance

### Weekly Tasks
- [ ] Review security scan results
- [ ] Address any MEDIUM severity findings
- [ ] Update tools to latest versions

### Monthly Tasks
- [ ] Review and update security policies
- [ ] Audit quality gate exceptions
- [ ] Update vulnerability database
- [ ] Review artifact retention

### Quarterly Tasks
- [ ] External security audit
- [ ] Penetration testing
- [ ] Review and update workflows
- [ ] Team security training

---

## 📞 Support

### Issues with Pipeline
- Create GitHub issue with label `ci/cd`
- Tag: @security-team
- Provide: Workflow run ID, error logs

### False Positives
- Document in issue
- Request security team review
- Add to suppression list if approved

### New Security Tools
- Propose via GitHub discussion
- Provide justification and benefits
- Security team will evaluate

---

## 📚 References

### Tools Documentation
- [Bandit](https://bandit.readthedocs.io/)
- [Trivy](https://aquasecurity.github.io/trivy/)
- [CodeQL](https://codeql.github.com/)
- [Anchore SBOM](https://github.com/anchore/sbom-action)

### Standards
- [SPDX Specification](https://spdx.dev/)
- [CycloneDX](https://cyclonedx.org/)
- [SARIF](https://sarifweb.azurewebsites.net/)
- [NCA Controls](https://nca.gov.sa/)

### Best Practices
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
- [OWASP CI/CD Security](https://owasp.org/www-project-devsecops-guideline/)
- [NIST Secure Software Development Framework](https://csrc.nist.gov/Projects/ssdf)

---

**Version**: 1.0  
**Last Updated**: February 2026  
**Maintained by**: SICO DevSecOps Team

**Compliant with**:
- NCA Essential Cybersecurity Controls (ECC)
- NCA Cloud Cybersecurity Controls (CCC)
- Saudi Personal Data Protection Law (PDPL)
- NIST Secure Software Development Framework (SSDF)
