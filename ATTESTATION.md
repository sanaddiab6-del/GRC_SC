# Build Attestation & Traceability

## 🔐 Artifact Attestation Template

**Platform**: SICO GRC Platform  
**Compliance**: NCA ECC, CCC, PDPL Standards  
**Version**: 1.0

This document provides attestation and traceability for security artifacts generated during the CI/CD pipeline.

---

## 📋 Attestation Overview

Build attestations provide cryptographic proof of:
- **What** was built (source code, dependencies)
- **How** it was built (build process, tools)
- **When** it was built (timestamp)
- **Who** built it (actor, workflow)
- **Where** artifacts are stored (locations, checksums)

---

## 🔗 Attestation Structure

### 1. Build Metadata

```json
{
  "attestation_version": "1.0",
  "platform": "SICO GRC Platform",
  "repository": "sonaiso/sanadcom",
  "compliance_frameworks": ["NCA-ECC", "NCA-CCC", "PDPL"],
  "build_metadata": {
    "workflow_name": "<WORKFLOW_NAME>",
    "workflow_run_id": "<RUN_ID>",
    "workflow_run_number": "<RUN_NUMBER>",
    "git_sha": "<COMMIT_SHA>",
    "git_ref": "<BRANCH_OR_TAG>",
    "build_timestamp": "<ISO8601_TIMESTAMP>",
    "build_actor": "<GITHUB_ACTOR>",
    "build_event": "<TRIGGER_EVENT>"
  }
}
```

### 2. Artifact Registry

```json
{
  "artifacts": [
    {
      "name": "sbom-backend-python.spdx.json",
      "type": "SBOM",
      "format": "SPDX-JSON",
      "description": "Software Bill of Materials for Python backend",
      "sha256": "<CHECKSUM>",
      "size_bytes": "<SIZE>",
      "url": "<ARTIFACT_URL>",
      "retention_days": 90,
      "compliance_mapping": ["ECC-2-5-1", "PDPL-Article-20"]
    },
    {
      "name": "bandit-report.sarif",
      "type": "SAST_REPORT",
      "format": "SARIF",
      "description": "Python Static Application Security Testing results",
      "sha256": "<CHECKSUM>",
      "size_bytes": "<SIZE>",
      "url": "<ARTIFACT_URL>",
      "retention_days": 90,
      "compliance_mapping": ["ECC-2-5-1"]
    },
    {
      "name": "trivy-backend-report.json",
      "type": "CONTAINER_SCAN",
      "format": "JSON",
      "description": "Container vulnerability scan results",
      "sha256": "<CHECKSUM>",
      "size_bytes": "<SIZE>",
      "url": "<ARTIFACT_URL>",
      "retention_days": 90,
      "compliance_mapping": ["ECC-2-3-1", "CCC-3-2-1"]
    }
  ]
}
```

### 3. Security Gates Status

```json
{
  "quality_gates": {
    "sbom_generation": {
      "status": "PASSED",
      "timestamp": "<TIMESTAMP>",
      "evidence": "sbom-reports artifact"
    },
    "python_security": {
      "status": "PASSED",
      "timestamp": "<TIMESTAMP>",
      "findings": {
        "critical": 0,
        "high": 0,
        "medium": 2,
        "low": 5
      },
      "evidence": "python-security-reports artifact"
    },
    "container_security": {
      "status": "PASSED",
      "timestamp": "<TIMESTAMP>",
      "findings": {
        "critical": 0,
        "high": 0,
        "medium": 3,
        "low": 8
      },
      "evidence": "trivy-scan-results artifact"
    },
    "codeql_analysis": {
      "status": "PASSED",
      "timestamp": "<TIMESTAMP>",
      "evidence": "GitHub Security tab"
    }
  }
}
```

### 4. Compliance Mapping

```json
{
  "nca_ecc_compliance": {
    "ECC-2-3-1": {
      "control": "Malware Protection",
      "implementation": "Container and dependency scanning",
      "evidence": ["trivy-scan-results", "npm-audit-report"]
    },
    "ECC-2-5-1": {
      "control": "Vulnerability Assessment",
      "implementation": "Automated security scanning in CI/CD",
      "evidence": ["bandit-report", "trivy-scan-results", "codeql-results"]
    },
    "ECC-2-5-2": {
      "control": "Vulnerability Remediation",
      "implementation": "Quality gates blocking HIGH/CRITICAL",
      "evidence": ["security-gate-status", "workflow-logs"]
    }
  },
  "nca_ccc_compliance": {
    "CCC-3-2-1": {
      "control": "Secure Configuration",
      "implementation": "Container image security scanning",
      "evidence": ["trivy-scan-results"]
    }
  },
  "pdpl_compliance": {
    "Article-20": {
      "requirement": "Security Measures",
      "implementation": "Comprehensive security scanning and SBOM generation",
      "evidence": ["sbom-reports", "security-summary-report"]
    }
  }
}
```

---

## 📦 Artifact Types

### SBOM (Software Bill of Materials)

**Purpose**: Complete inventory of software components and dependencies

**Formats**:
- **SPDX**: ISO/IEC 5962:2021 standard
- **CycloneDX**: OWASP standard for SBOM

**Generated Files**:
- `sbom-backend-python.spdx.json` - Python dependencies
- `sbom-frontend-nodejs.spdx.json` - Node.js dependencies
- `sbom-backend-cyclonedx.json` - Backend in CycloneDX format

**Use Cases**:
- Supply chain security
- License compliance
- Vulnerability tracking
- Component inventory

### SARIF (Static Analysis Results Interchange Format)

**Purpose**: Standardized format for static analysis tool output

**Standard**: OASIS SARIF v2.1.0

**Generated Files**:
- `bandit-report.sarif` - Python SAST results
- `trivy-backend-results.sarif` - Container scan results
- `trivy-frontend-results.sarif` - Frontend scan results
- `codeql-results-*.sarif` - CodeQL analysis results

**Use Cases**:
- GitHub Security integration
- Centralized vulnerability management
- Cross-tool compatibility
- Audit evidence

### JSON Security Reports

**Purpose**: Detailed vulnerability information in machine-readable format

**Generated Files**:
- `bandit-report.json` - Detailed Python security issues
- `safety-report.json` - Python dependency vulnerabilities
- `pip-audit-report.json` - Python package audit
- `npm-audit-report.json` - Node.js vulnerabilities
- `trivy-backend-report.json` - Backend vulnerability details
- `trivy-frontend-report.json` - Frontend vulnerability details

**Use Cases**:
- Automated processing
- Custom reporting
- Trend analysis
- Integration with other tools

---

## 🔍 Traceability Links

### GitHub Actions Workflow

**Location**: `.github/workflows/security-scan.yml`

**Runs**: Every push, pull request, daily schedule

**Artifacts URL Pattern**:
```
https://github.com/sonaiso/sanadcom/actions/runs/<RUN_ID>/artifacts
```

### Security Tab

**Location**: GitHub Repository Security Tab

**Includes**:
- CodeQL Analysis Results
- Dependabot Alerts
- Secret Scanning
- Security Advisories

**URL**:
```
https://github.com/sonaiso/sanadcom/security
```

### Artifact Downloads

**Direct Download** (Requires authentication):
```bash
# Using GitHub CLI
gh run download <RUN_ID> --name sbom-reports

# Using REST API
curl -H "Authorization: token <TOKEN>" \
  -L https://api.github.com/repos/sonaiso/sanadcom/actions/artifacts/<ARTIFACT_ID>/zip
```

---

## 🔐 Verification Procedures

### 1. Verify Artifact Integrity

```bash
# Download artifact
gh run download <RUN_ID> --name sbom-reports

# Calculate checksum
sha256sum sbom-backend-python.spdx.json

# Compare with attestation checksum
```

### 2. Verify Build Provenance

```bash
# Get workflow run details
gh run view <RUN_ID>

# Verify:
# - Commit SHA matches intended commit
# - Workflow file hasn't been tampered
# - Actor is authorized
# - Timestamp is within expected range
```

### 3. Verify Compliance Evidence

```bash
# Check that all required artifacts are present
ls -la artifacts/

# Required artifacts:
# - SBOM files (SPDX and CycloneDX)
# - SARIF reports (bandit, trivy, codeql)
# - JSON reports (detailed findings)
# - Security summary report
```

---

## 📊 Audit Trail

### Event Logging

All security-relevant events are logged:

1. **Build Trigger**
   - Event type (push, PR, schedule)
   - Actor identity
   - Commit SHA

2. **Scan Execution**
   - Start timestamp
   - Tool versions
   - Configuration used

3. **Findings**
   - Vulnerabilities detected
   - Severity levels
   - Affected components

4. **Quality Gate Decisions**
   - Pass/fail status
   - Reason for failure (if applicable)
   - Override information (if any)

5. **Artifact Generation**
   - Artifact names
   - Checksums
   - Upload timestamp
   - Retention period

### Retention Policy

| Artifact Type | Retention Period | Reason |
|--------------|------------------|--------|
| SBOM | 90 days | Supply chain tracking |
| SARIF Reports | 90 days | Compliance evidence |
| JSON Reports | 90 days | Detailed analysis |
| Security Summary | 90 days | Audit reporting |
| Workflow Logs | 90 days | Troubleshooting |

---

## 🎯 NCA Compliance Evidence

### ECC Controls Evidence Matrix

| Control ID | Control Name | Evidence Artifacts | Verification Method |
|-----------|--------------|-------------------|-------------------|
| ECC-2-3-1 | Malware Protection | trivy-scan-results | Automated scanning |
| ECC-2-5-1 | Vulnerability Assessment | All SARIF/JSON reports | Daily automated scans |
| ECC-2-5-2 | Vulnerability Remediation | Quality gate logs | Blocking HIGH/CRITICAL |

### CCC Controls Evidence Matrix

| Control ID | Control Name | Evidence Artifacts | Verification Method |
|-----------|--------------|-------------------|-------------------|
| CCC-3-2-1 | Secure Configuration | trivy-scan-results | Container scanning |

### PDPL Evidence Matrix

| Article | Requirement | Evidence Artifacts | Verification Method |
|---------|-------------|-------------------|-------------------|
| Article 20 | Security Measures | SBOM + scan reports | Comprehensive security scanning |

---

## 🔄 Continuous Improvement

### Metrics Tracked

- **Vulnerability Detection Rate**: Number of vulnerabilities found per scan
- **Time to Remediation**: Average time from detection to fix
- **False Positive Rate**: Percentage of false positives
- **Coverage**: Percentage of code scanned
- **Compliance Score**: Percentage of controls with evidence

### Review Schedule

- **Weekly**: Review scan results and trends
- **Monthly**: Update security tooling and configurations
- **Quarterly**: Comprehensive audit of attestation process
- **Annually**: External audit of security controls

---

## 📞 Contact & Support

### Questions about Attestations

- **Email**: security@sicogrc.com
- **Documentation**: See SECURITY.md
- **GitHub Issues**: For technical questions

### Request Attestation Copy

To request a copy of build attestation:

1. Specify workflow run ID
2. Indicate required artifacts
3. Provide justification for request
4. Allow 24-48 hours for response

---

## 📝 Template Usage

### For Each Build

1. **Collect Metadata**
   ```bash
   WORKFLOW_ID=${{ github.run_id }}
   COMMIT_SHA=${{ github.sha }}
   BUILD_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
   ```

2. **Generate Attestation**
   ```bash
   ./scripts/generate-attestation.sh \
     --workflow-id $WORKFLOW_ID \
     --commit $COMMIT_SHA \
     --timestamp $BUILD_TIME
   ```

3. **Sign Attestation** (Future)
   ```bash
   cosign sign-blob attestation.json \
     --output-signature attestation.sig
   ```

4. **Store Attestation**
   ```bash
   # Upload to artifact storage
   # Link with build in CI/CD system
   # Archive for compliance retention
   ```

---

## 🔮 Future Enhancements

### Planned Features

1. **Digital Signatures**
   - Sign artifacts with cosign
   - Verify signatures before deployment
   - SLSA provenance generation

2. **Blockchain Integration**
   - Store attestation hashes on blockchain
   - Immutable audit trail
   - Tamper-proof evidence

3. **Automated Attestation**
   - Generate attestations automatically
   - Link with CI/CD artifacts
   - Real-time compliance dashboard

4. **SLSA Compliance**
   - Achieve SLSA Level 3
   - Supply chain security framework
   - Build provenance

---

**Version**: 1.0  
**Last Updated**: February 2026  
**Maintained by**: SICO Security Team

**Compliant with**:
- NCA Essential Cybersecurity Controls (ECC)
- NCA Cloud Cybersecurity Controls (CCC)
- Saudi Personal Data Protection Law (PDPL)
- NIST SSDF (Secure Software Development Framework)
- SLSA (Supply-chain Levels for Software Artifacts)
