# Security Pipeline Quick Start Guide

## 🚀 SICO GRC Platform - Security Scanning Quick Start

**For**: Developers, DevOps Engineers  
**Time**: 5 minutes  
**Goal**: Understand and use the automated security pipeline

---

## 📋 What You Get

Every time you push code or create a PR, the security pipeline automatically:

1. ✅ **Generates SBOM** - Complete software bill of materials
2. ✅ **Scans Python code** - Static analysis with Bandit
3. ✅ **Checks Python deps** - Vulnerability scanning with Safety & pip-audit
4. ✅ **Scans Node.js deps** - Security audit with npm audit
5. ✅ **Scans containers** - Multi-purpose scanning with Trivy
6. ✅ **Deep code analysis** - Semantic analysis with CodeQL
7. ✅ **Enforces gates** - Fails on HIGH/CRITICAL vulnerabilities
8. ✅ **Generates reports** - SARIF, JSON, and executive summaries

---

## 🔄 How It Works

### Automatic Triggers

```
┌─────────────────┐
│  You Push Code  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  Security Scan Starts   │
│  (Automatically)        │
└────────┬────────────────┘
         │
         ▼
┌──────────────────────────┐
│  6 Jobs Run in Parallel  │
│  • SBOM Generation       │
│  • Python Security       │
│  • Node.js Security      │
│  • Container Scanning    │
│  • CodeQL Analysis       │
│  • Summary Generation    │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│  Results Available       │
│  • Artifacts uploaded    │
│  • Security tab updated  │
│  • PR comment posted     │
└──────────────────────────┘
```

### Triggers

- ✅ Push to `main`, `develop`, or `release/*` branches
- ✅ Pull requests to `main` or `develop`
- ✅ Daily at 2 AM UTC (scheduled scan)
- ✅ Manual trigger via Actions tab

---

## 📊 Viewing Results

### Option 1: Pull Request Comment

If you created a PR, you'll see a comment with:
- Scan status for all components
- List of artifacts generated
- NCA compliance status
- Links to detailed reports

### Option 2: GitHub Actions

1. Go to **Actions** tab
2. Click on latest workflow run
3. See job statuses (green ✅ / red ❌)
4. Download artifacts at bottom of page

### Option 3: Security Tab

1. Go to **Security** tab
2. View **Code scanning alerts** from CodeQL and Bandit
3. See **Dependabot alerts** for dependencies
4. Check **Security advisories**

---

## 🔍 Understanding Results

### ✅ All Green - Success!

```
✅ SBOM Generation - success
✅ Python Security - success  
✅ Node.js Security - success
✅ Container Security - success
```

**Meaning**: No HIGH or CRITICAL vulnerabilities found. Code is ready for deployment.

**Action**: None required. Proceed with merge.

### ⚠️ Yellow - Warnings

```
⚠️  Python Security - success (2 MEDIUM findings)
```

**Meaning**: MEDIUM severity issues found. Not blocking, but should be reviewed.

**Action**: Review findings in artifact. Consider fixing before merge.

### ❌ Red - Blocked!

```
❌ Python Security - failed (1 CRITICAL, 2 HIGH findings)
```

**Meaning**: HIGH or CRITICAL vulnerabilities found. Deployment blocked.

**Action Required**:
1. Download security report artifact
2. Review findings
3. Fix vulnerabilities
4. Push new commit
5. Pipeline runs again

---

## 📦 Downloading Artifacts

### Via GitHub UI

1. Go to **Actions** → Select workflow run
2. Scroll to **Artifacts** section
3. Click artifact name to download

### Via GitHub CLI

```bash
# List artifacts
gh run view <RUN_ID>

# Download specific artifact
gh run download <RUN_ID> --name sbom-reports

# Download all artifacts
gh run download <RUN_ID>
```

### Artifacts Available

| Artifact | Contents | When to Use |
|----------|----------|-------------|
| `sbom-reports` | Software Bill of Materials | Supply chain compliance |
| `python-security-reports` | Python scan results | Python vulnerability review |
| `nodejs-security-reports` | Node.js audit | JavaScript dependency issues |
| `trivy-scan-results` | Container scans | Container security review |
| `security-summary-report` | Executive summary | Management reporting |

---

## 🛠️ Common Scenarios

### Scenario 1: New Dependency Added

**What happens**:
- SBOM automatically regenerated
- New dependency scanned for vulnerabilities
- If HIGH/CRITICAL found → build fails

**Your action**:
1. Review vulnerability report
2. Update to patched version OR
3. Find alternative dependency OR
4. Accept risk (document in security issue)

### Scenario 2: Vulnerability in Existing Dependency

**What happens**:
- Daily scan detects new vulnerability
- You receive notification
- PR to main blocked until fixed

**Your action**:
1. Update dependency to patched version
2. Run tests to ensure compatibility
3. Push update
4. Verify scan passes

### Scenario 3: False Positive

**What happens**:
- Scanner reports issue that's not real
- Build fails unnecessarily

**Your action**:
1. Document finding in GitHub issue
2. Tag security team for review
3. If confirmed false positive:
   - Add to suppression list
   - Document reasoning
   - Security team approves

### Scenario 4: Urgent Fix Needed

**What happens**:
- CRITICAL vulnerability blocks production deployment
- Need immediate fix

**Your action**:
1. Create hotfix branch
2. Apply security patch
3. Test thoroughly
4. Create PR
5. Security scan runs automatically
6. If passes → fast-track merge

---

## 🎯 Quality Gate Rules

### What Gets Blocked

⛔ **CRITICAL Severity**
- Remote code execution
- Authentication bypass
- Data exposure
- **Action**: Fix immediately

⛔ **HIGH Severity**
- SQL injection
- Cross-site scripting (XSS)
- Known CVEs with exploits
- **Action**: Fix before merge

### What Gets Warning

⚠️  **MEDIUM Severity**
- Information disclosure
- Denial of service
- Security misconfigurations
- **Action**: Review and consider fixing

### What Gets Tracked

ℹ️  **LOW Severity**
- Minor issues
- Best practice violations
- Informational findings
- **Action**: Track for future cleanup

---

## 🔐 Best Practices

### Before Committing

```bash
# Run security checks locally (Python)
bandit -r src/backend/
safety check
pip-audit

# Run security checks locally (Node.js)
cd src/frontend
npm audit
```

### When Adding Dependencies

1. ✅ Check for known vulnerabilities
2. ✅ Review package reputation (downloads, stars, maintainers)
3. ✅ Check last update date
4. ✅ Review license compatibility
5. ✅ Run security scan after adding

### During Development

1. ✅ Never commit secrets (API keys, passwords)
2. ✅ Validate all user inputs
3. ✅ Use parameterized queries (no string concatenation)
4. ✅ Implement proper error handling
5. ✅ Follow principle of least privilege

### Before Deployment

1. ✅ All security scans passed
2. ✅ No HIGH/CRITICAL vulnerabilities
3. ✅ SBOM generated and reviewed
4. ✅ Security documentation updated
5. ✅ Incident response plan ready

---

## 📚 Additional Resources

### Documentation
- [SECURITY.md](../SECURITY.md) - Full security policy
- [ATTESTATION.md](../ATTESTATION.md) - Traceability details
- [SECURITY-BEST-PRACTICES.md](SECURITY-BEST-PRACTICES.md) - Secure coding guide
- [CI-CD-SECURITY.md](CI-CD-SECURITY.md) - Pipeline documentation

### Tools
- [Bandit Docs](https://bandit.readthedocs.io/)
- [Trivy Docs](https://trivy.dev/)
- [CodeQL Docs](https://codeql.github.com/)

### Getting Help
- **Security Issues**: Create issue with `security` label
- **False Positives**: Tag @security-team
- **General Questions**: GitHub Discussions
- **Urgent Security**: security@sicogrc.com

---

## ❓ FAQ

**Q: Why did my build fail?**  
A: Check the Actions tab. If security scan failed, HIGH or CRITICAL vulnerabilities were found.

**Q: How do I fix vulnerabilities?**  
A: Download the security report artifact. It lists all issues with fix recommendations.

**Q: Can I bypass the security gate?**  
A: Only with security team approval and documented exception. Create issue for review.

**Q: How often do scans run?**  
A: On every push/PR + daily at 2 AM UTC + manual trigger.

**Q: How long are artifacts stored?**  
A: 90 days in GitHub Actions.

**Q: What if a vulnerability has no fix?**  
A: Document in security issue. Assess risk. Consider alternative dependency or mitigation controls.

**Q: How do I run scans locally?**  
A: Use the tools directly: `bandit`, `safety`, `pip-audit`, `npm audit`, `trivy`.

**Q: What's an SBOM and why do I need it?**  
A: Software Bill of Materials - lists all dependencies. Required for supply chain security and NCA compliance.

---

## 🚨 Need Help?

### Quick Links
- [Actions Tab](../../actions)
- [Security Tab](../../security)
- [Documentation](../docs/)

### Contact
- **Email**: security@sicogrc.com
- **GitHub**: @security-team
- **Urgent**: See SECURITY.md

---

**Version**: 1.0  
**Last Updated**: February 2026  
**For**: SICO GRC Platform Developers

**Happy Secure Coding! 🔐**
