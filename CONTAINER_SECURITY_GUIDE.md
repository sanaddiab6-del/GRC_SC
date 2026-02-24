# Container Security Best Practices - SICO GRC Platform

## Overview

This document outlines best practices for managing container security vulnerabilities discovered by Trivy scanning in our CI/CD pipeline.

---

## Vulnerability Management Strategy

### 1. Severity Classification

| Severity | Response Time | Action Required |
|----------|---------------|-----------------|
| **CRITICAL** | Immediate (24h) | Block deployment, fix required |
| **HIGH** | 1 week | Fix in next sprint |
| **MEDIUM** | 1 month | Schedule for fix |
| **LOW** | Quarterly | Review and assess |

### 2. Branch-Based Thresholds

Our CI/CD pipeline uses different thresholds based on the branch:

#### Main Branch (Production)
```yaml
CRITICAL: 0 (must fix immediately)
HIGH: ≤5 (warnings only)
```

#### Feature Branches (Development)
```yaml
CRITICAL: ≤10 (allows development progress)
HIGH: ≤20 (relaxed for faster iteration)
```

---

## Common Vulnerability Sources

### 1. Base Image Vulnerabilities
**Problem**: Official images (node:20-alpine, python:3.11-slim) may contain OS-level vulnerabilities.

**Solutions**:
- Use minimal base images (Alpine, Distroless)
- Regularly update to latest patch versions
- Consider using Google's Distroless images
- Pin specific versions and update frequently

```dockerfile
# ❌ Bad - Uses latest, unpredictable
FROM node:20-alpine

# ✅ Good - Pinned version with digest
FROM node:20.11.1-alpine3.19@sha256:abc123...
```

### 2. Dependency Vulnerabilities
**Problem**: npm/pip packages may have known vulnerabilities.

**Solutions**:
- Run `npm audit fix` / `pip-audit` regularly
- Use Dependabot for automated updates
- Review and merge security PRs promptly
- Use lockfiles (package-lock.json, poetry.lock)

### 3. Multi-Stage Build Vulnerabilities
**Problem**: Build tools carried into production image.

**Solutions**:
- Use multi-stage builds
- Only copy necessary artifacts to final image
- Remove build dependencies

```dockerfile
# Multi-stage build example
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:20-alpine AS runtime
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
USER node
CMD ["node", "server.js"]
```

---

## Workflow for Handling CRITICAL Vulnerabilities

### Step 1: Identify the Issue
When CI fails with CRITICAL vulnerabilities:

1. Download the `trivy-{component}.json` artifact from GitHub Actions
2. Review the vulnerability details:
   ```bash
   jq '.Results[]?.Vulnerabilities[]? | select(.Severity=="CRITICAL")' trivy-frontend.json
   ```

### Step 2: Assess the Impact
For each vulnerability, determine:
- **Is it exploitable in our context?** (e.g., server-side vs client-side)
- **Is there a fix available?** (check `FixedVersion`)
- **What is the mitigation?** (upgrade, patch, remove dependency)

### Step 3: Choose Action Path

#### Option A: Update Dependency
```bash
# For npm packages
npm update <package-name>
npm audit fix

# For base images
# Update Dockerfile base image version
```

#### Option B: Add to .trivyignore (Temporary)
```bash
# Add CVE with justification and review date
echo "# CVE-2024-12345 - False positive, reviewed 2026-02-24" >> .trivyignore
echo "CVE-2024-12345" >> .trivyignore
```

#### Option C: Apply Workaround
Document the mitigation in `SECURITY.md` and add compensating controls.

### Step 4: Re-run Scan
```bash
# Local test before pushing
make security-container

# Or using Docker
docker build -t test-image src/frontend
trivy image --severity CRITICAL,HIGH test-image
```

---

## CI/CD Configuration

### Current Pipeline Behavior

1. **✅ Scans run on**: Push to main/develop, PRs, weekly schedule
2. **✅ Results uploaded to**: GitHub Security tab (SARIF format)
3. **✅ Artifacts retained**: 90 days (JSON reports)
4. **✅ Fail conditions**:
   - Main branch: CRITICAL > 0
   - Feature branches: CRITICAL > 10 (continues with warning)

### Adjusting Thresholds

Edit `.github/workflows/security-scanning.yml`:

```yaml
# For stricter policy (fail on HIGH also)
if [ "$HIGH" -gt 5 ]; then
  EXIT_CODE=1  # Uncomment this line
fi

# For more lenient policy (allow more CRITICALs)
CRITICAL_THRESHOLD=5  # Increase from 0
```

---

## Monitoring & Reporting

### GitHub Security Tab
- Navigate to: `Security > Code scanning alerts > Trivy`
- Filter by severity, status, or package
- Assign alerts to team members
- Track remediation progress

### Artifacts
Every scan produces:
- `trivy-{component}.sarif` - GitHub Security format
- `trivy-{component}.json` - Detailed findings

**Download**: Go to Actions run → Artifacts section → Download `trivy-*`

### Weekly Review Process
1. **Monday 9 AM UTC**: Automated weekly scan runs
2. **Security Team**: Reviews new findings
3. **Assign**: Critical issues to respective teams
4. **Track**: Progress in GitHub Projects
5. **Report**: Security metrics in monthly review

---

## Preventive Measures

### 1. Use Renovate/Dependabot
Enable automated dependency updates:

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "security"
      - "dependencies"
```

### 2. Lock Base Image Versions
Always use digests for reproducible builds:

```dockerfile
FROM node:20.11.1-alpine3.19@sha256:[digest]
```

### 3. Regular Update Cadence
- **Weekly**: Review and merge security PRs
- **Monthly**: Manual dependency updates
- **Quarterly**: Review .trivyignore entries
- **Yearly**: Base image major version updates

### 4. Container Hardening
```dockerfile
# Run as non-root user
USER node

# Read-only filesystem
RUN chmod -R a-w /app

# Drop capabilities
# (Configure in docker-compose.yml or k8s)
cap_drop:
  - ALL
cap_add:
  - NET_BIND_SERVICE
```

---

## Reference Commands

### Local Scanning
```bash
# Scan an image
trivy image sico-grc-frontend:latest

# Scan with specific severities
trivy image --severity CRITICAL,HIGH sico-grc-frontend:latest

# Output to JSON
trivy image --format json --output report.json sico-grc-frontend:latest

# Scan filesystem (before building)
trivy fs --severity HIGH,CRITICAL src/frontend

# Ignore unfixed vulnerabilities
trivy image --ignore-unfixed sico-grc-frontend:latest
```

### Debugging
```bash
# List all packages in image
trivy image --list-all-pkgs sico-grc-frontend:latest

# Show only fixable vulnerabilities
jq '.Results[]?.Vulnerabilities[]? | select(.FixedVersion != "")' trivy-report.json

# Count by severity
jq '[.Results[]?.Vulnerabilities[]? | .Severity] | group_by(.) | map({severity: .[0], count: length})' trivy-report.json
```

---

## Escalation Path

1. **Developer** encounters CRITICAL vulnerability
2. **Team Lead** assesses business impact
3. **Security Team** reviews and approves mitigation
4. **DevOps** implements fix or workaround
5. **QA** validates fix doesn't break functionality
6. **Merge** and verify CI passes

**Emergency Hot-Fix Process**:
- For actively exploited CVEs
- Skip feature branch, direct to main (with approval)
- Immediate deployment post-merge

---

## Resources

- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
- [GitHub Security Features](https://docs.github.com/en/code-security)
- [OWASP Container Security](https://owasp.org/www-project-docker-security/)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)
- [NIST Container Security Guide](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-190.pdf)

---

## Related Documents

- [SECURITY.md](SECURITY.md) - General security policy
- [SECURITY-ATTESTATION.md](SECURITY-ATTESTATION.md) - PR security checklist
- [.trivyignore](.trivyignore) - Ignored CVEs list
- [docs/CI-CD-SECURITY.md](docs/CI-CD-SECURITY.md) - Full pipeline documentation

---

**Last Updated**: February 24, 2026  
**Next Review**: May 24, 2026  
**Owner**: Security & DevOps Team
