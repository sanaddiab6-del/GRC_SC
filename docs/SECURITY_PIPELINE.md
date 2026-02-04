# Security Pipeline Documentation

## Overview

The SICO GRC Platform includes a comprehensive security pipeline that runs automated security scans on every commit and pull request. This ensures that security vulnerabilities are caught early in the development lifecycle.

## Security Scanning Components

### 1. Dependency Vulnerability Scanning

**Tools:**
- **Python**: Safety (checks PyPI packages against known vulnerabilities)
- **Node.js**: npm audit (checks npm packages against GitHub Advisory Database)

**Triggers:**
- Every push to main, develop, or copilot/* branches
- All pull requests
- Weekly scheduled scan (Mondays at 9 AM UTC)

**What it checks:**
- Known CVEs in Python dependencies
- Known vulnerabilities in Node.js dependencies
- Outdated packages with security patches

**Local execution:**
```bash
make security-deps
```

### 2. SAST (Static Application Security Testing)

**Tools:**
- **Bandit**: Python security linter (checks for common security issues)
- **CodeQL**: Advanced semantic code analysis

**What it checks:**
- SQL injection vulnerabilities
- Hardcoded secrets/passwords
- Insecure cryptography usage
- Command injection risks
- Path traversal vulnerabilities
- XSS vulnerabilities
- Insecure deserialization

**Local execution:**
```bash
make security-sast
```

### 3. CodeQL Analysis

**Languages analyzed:**
- Python (backend and AI code)
- JavaScript/TypeScript (frontend)

**Query packs:**
- Security queries (security vulnerabilities)
- Quality queries (code quality issues)

**Integration:**
- Results uploaded to GitHub Security tab
- Can block PRs if critical issues found
- Provides detailed remediation guidance

### 4. SBOM (Software Bill of Materials) Generation

**Tools:**
- CycloneDX (industry-standard SBOM format)

**What it generates:**
- Complete inventory of all dependencies
- Dependency relationships and versions
- License information
- Component hashes for verification

**Output formats:**
- JSON (machine-readable)
- Stored as artifacts for 90 days

**Use cases:**
- Supply chain security audits
- License compliance verification
- Vulnerability tracking
- Regulatory compliance (SBOM requirements)

### 5. Secret Scanning

**Tool:**
- Gitleaks (detects hardcoded secrets)

**What it checks:**
- API keys and tokens
- Passwords and credentials
- Private keys
- AWS/Azure credentials
- Database connection strings

**Scan scope:**
- Full git history
- All branches and commits

## Workflow Configuration

### Main Security Workflow
**File:** `.github/workflows/security-scanning.yml`

**Jobs:**
1. `dependency-scan` - Scans Python and Node.js dependencies
2. `sast-python` - Runs Bandit and generates SARIF reports
3. `codeql-analysis` - Deep semantic analysis
4. `sbom-generation` - Creates software inventory
5. `secret-scan` - Detects hardcoded secrets
6. `security-summary` - Aggregates all results

### CI/CD Pipeline
**File:** `.github/workflows/ci.yml`

**Additional checks:**
- Conflict marker detection
- Python import validation
- Build verification
- Test execution

## Using the Security Pipeline Locally

### Quick Security Check
```bash
# Run all security scans
make security

# This will:
# 1. Check Python dependencies with Safety
# 2. Check Node.js dependencies with npm audit
# 3. Run Bandit SAST scan
# 4. Generate reports in JSON format
```

### Individual Scans

**Dependency scanning only:**
```bash
make security-deps
```

**SAST scanning only:**
```bash
make security-sast
```

### Installing Security Tools

All security tools can be installed via the Makefile targets (they install automatically when needed). For manual installation:

```bash
# Python tools
pip install safety bandit[toml] cyclonedx-bom

# Node.js tools
npm install -g @cyclonedx/cyclonedx-npm
```

## GitHub Security Integration

### Security Tab

All security findings are automatically uploaded to the GitHub Security tab:

1. Navigate to **Security** > **Code scanning alerts**
2. Filter by severity: Critical, High, Medium, Low
3. View detailed findings with:
   - Affected code location
   - Vulnerability description
   - Remediation guidance
   - CVSS score

### Pull Request Integration

Security scans run automatically on PRs:

- ✅ Pass: No critical/high vulnerabilities found
- ⚠️ Warning: Medium/low vulnerabilities found
- ❌ Fail: Critical/high vulnerabilities found

**To resolve failures:**
1. Review the security scan results in the PR
2. Fix identified vulnerabilities
3. Push updated code
4. Scans will re-run automatically

## Fail-On-High Gates

The security pipeline is configured to **continue-on-error** for most checks to allow visibility into issues without blocking development. 

### To Enable Blocking on Critical Issues

Edit `.github/workflows/security-scanning.yml` and remove `continue-on-error: true` from:

```yaml
- name: Run Safety check (Backend)
  continue-on-error: true  # Remove this line to fail on vulnerabilities
```

**Recommended for production:**
- Remove `continue-on-error` for `main` branch
- Keep it for `develop` and feature branches

## Reports and Artifacts

### Artifact Retention

| Report Type | Retention | Location |
|-------------|-----------|----------|
| Dependency scans | 30 days | GitHub Actions artifacts |
| Bandit reports | 30 days | GitHub Actions artifacts |
| SBOM | 90 days | GitHub Actions artifacts |
| CodeQL results | Permanent | GitHub Security tab |

### Downloading Reports

1. Go to **Actions** tab
2. Click on a workflow run
3. Scroll to **Artifacts** section
4. Download desired report

### Report Formats

- **JSON**: Machine-readable, for automation
- **SARIF**: Standard format for security tools
- **HTML**: Human-readable coverage reports

## Best Practices

### Development Workflow

1. **Before committing:**
   ```bash
   make security
   ```

2. **Address findings:**
   - Fix critical and high severity issues immediately
   - Plan remediation for medium issues
   - Document why low issues are acceptable

3. **Regular updates:**
   - Keep dependencies up to date
   - Monitor weekly security scans
   - Review GitHub security advisories

### Dependency Management

**For Python:**
```bash
# Update a specific vulnerable package
pip install --upgrade vulnerable-package

# Update requirements
pip freeze > src/backend/requirements.txt
```

**For Node.js:**
```bash
# Update a specific package
npm update vulnerable-package

# Audit and fix automatically
npm audit fix
```

### Handling False Positives

**Bandit false positives:**
Create `bandit.yml` configuration:
```yaml
skips:
  - B101  # Skip assert_used if intentional
```

**Safety false positives:**
Add to `safety.policy`:
```json
{
  "ignore": {
    "CVE-2023-XXXXX": "False positive - not exploitable in our context"
  }
}
```

## Compliance Alignment

This security pipeline supports:

- ✅ **NCA ECC**: Security testing and vulnerability management
- ✅ **NCA CCC**: Cloud security controls and monitoring
- ✅ **PDPL**: Data protection and security measures
- ✅ **ISO 27001**: Information security controls
- ✅ **NIST CSF**: Identify, Protect, Detect functions

## Troubleshooting

### Common Issues

**Issue: Safety check fails**
```bash
# Update Safety database
pip install --upgrade safety
```

**Issue: npm audit shows vulnerabilities**
```bash
# Try automatic fix
npm audit fix

# If fix unavailable, check if update possible
npm outdated
```

**Issue: Bandit reports false positive**
```bash
# Add inline ignore comment
# nosec B101
```

**Issue: CodeQL timeout**
- CodeQL can take 10-20 minutes for large codebases
- This is normal and expected

## Future Enhancements

Planned additions:

- [ ] Container vulnerability scanning (Trivy)
- [ ] Infrastructure as Code scanning (Checkov)
- [ ] License compliance checking
- [ ] Dependency update automation (Dependabot)
- [ ] Security metrics dashboard
- [ ] SLA tracking for vulnerability remediation

## Support

For issues or questions about the security pipeline:

1. Check GitHub Security tab for findings
2. Review workflow logs in Actions tab
3. Consult this documentation
4. Contact security team

## References

- [Bandit Documentation](https://bandit.readthedocs.io/)
- [Safety Documentation](https://pyup.io/safety/)
- [CodeQL Documentation](https://codeql.github.com/)
- [CycloneDX Specification](https://cyclonedx.org/)
- [SARIF Format](https://sarifweb.azurewebsites.net/)
