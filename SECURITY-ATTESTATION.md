# 🔒 Security Attestation for Pull Request

> **Purpose:** This attestation ensures all security requirements are met before merging code changes into production.
> 
> **Required for:** All pull requests modifying backend, frontend, AI, or infrastructure code
> 
> **How to use:** Copy this checklist into your PR description and check off each item

---

## Security Scan Results

### Required Checks (Must Pass)

- [ ] **Dependency Scan:** No CRITICAL vulnerabilities in Python/Node.js dependencies
  - Link to CI artifact: [Download Safety/npm audit reports]
  - If vulnerabilities found: Document exceptions below

- [ ] **SAST (Static Analysis):** Bandit + CodeQL scans passed
  - Link to CodeQL results: [GitHub Security tab → Code scanning alerts]
  - If findings exist: Document risk acceptance below

- [ ] **Secret Detection:** Gitleaks scan passed (no hardcoded credentials)
  - Link to Gitleaks results: [GitHub Actions → Security CI]
  - If false positives: Document exceptions below

- [ ] **Container Scan:** Trivy scan passed (0 CRITICAL, <5 HIGH vulnerabilities)
  - Link to Trivy reports: [Download Trivy artifacts]
  - If vulnerabilities found: Document remediation plan below

- [ ] **SBOM Generated:** Software Bill of Materials created and attached
  - Link to SBOM files: [Download SBOM artifacts]

---

## Code Review Checks

### Security-Specific Review

- [ ] **Authentication:** Changes to auth logic reviewed by security team
- [ ] **Authorization:** RBAC checks verified (correct role requirements)
- [ ] **Encryption:** PII fields encrypted at rest (if applicable)
- [ ] **Audit Logging:** All sensitive actions logged (user_id, action, resource)
- [ ] **Input Validation:** User inputs sanitized (SQL injection, XSS prevention)
- [ ] **Rate Limiting:** API endpoints have appropriate rate limits
- [ ] **Error Handling:** No sensitive data leaked in error messages

### Data Protection (PDPL Compliance)

- [ ] **PII Handling:** Personal data encrypted and access-controlled
- [ ] **Data Retention:** Retention policies respected (7-year audit logs, etc.)
- [ ] **Consent Management:** User consent obtained for data processing (if applicable)
- [ ] **Cross-Border Transfer:** Data stays within Saudi Arabia (no egress to other regions)

---

## Testing Checks

- [ ] **Unit Tests:** New code has >80% test coverage
  - Coverage report: [Link to pytest-cov / Jest coverage report]

- [ ] **Integration Tests:** API endpoints tested with authentication/authorization
  - Test results: [Link to test logs]

- [ ] **Security Tests:** Negative test cases added (e.g., unauthorized access, invalid input)
  - Example: "Test that Viewer role cannot delete controls"

---

## Documentation Checks

- [ ] **API Documentation:** New endpoints documented in OpenAPI/Swagger
- [ ] **Code Comments:** Security-critical code has explanatory comments
- [ ] **README Updates:** Changes reflected in relevant README files
- [ ] **CHANGELOG:** Entry added to CHANGELOG.md (if applicable)

---

## Exception/Risk Acceptance (If Applicable)

> **Use this section ONLY if security scans found issues that cannot be fixed immediately**

### Vulnerability Exception Request

| Vulnerability ID | Severity | Component | Reason for Exception | Mitigation Plan | Expiry Date | Approved By |
|------------------|----------|-----------|----------------------|-----------------|-------------|-------------|
| CVE-2024-XXXX | HIGH | Package X v1.2.3 | No patch available; low exploitability | Firewall rule blocks attack vector | 2024-12-31 | [Security Lead] |

**Approval Process:**
1. Document vulnerability in table above
2. Link to tracking ticket (e.g., GitHub Issue #123)
3. Get approval from Security Lead (comment in PR)
4. Set expiry date (max 90 days)
5. Schedule follow-up review

---

## Deployment Checklist (For Production Releases)

- [ ] **Environment Variables:** All secrets stored in Azure Key Vault (not in `.env` files)
- [ ] **TLS/HTTPS:** HTTPS enforced (no HTTP traffic allowed)
- [ ] **Database Migrations:** Alembic migrations tested in staging environment
- [ ] **Rollback Plan:** Documented rollback procedure if deployment fails
- [ ] **Monitoring:** Alerts configured for new endpoints (latency, error rate)

---

## Sign-Off

**Author Statement:**
> I, [Author Name], confirm that:
> - I have reviewed all security scan results
> - I have addressed all CRITICAL/HIGH findings or documented exceptions
> - I have tested authentication, authorization, and audit logging
> - I have not introduced hardcoded secrets or credentials
> - I understand this code will be deployed to production serving sensitive GRC data

**Author Signature:** @[GitHub Username]  
**Date:** [YYYY-MM-DD]

---

**Security Reviewer Statement:**
> I, [Reviewer Name], confirm that:
> - I have reviewed the code for security vulnerabilities
> - I have verified all checklist items above
> - I approve this PR for merge (or have requested changes)

**Reviewer Signature:** @[GitHub Username]  
**Date:** [YYYY-MM-DD]

---

## Additional Notes

[Add any additional context, security considerations, or follow-up tasks here]

---

**References:**
- [Security Pipeline Documentation](docs/SECURITY_PIPELINE.md)
- [90-Day Engineering Plan](docs/engineering/90_DAY_ENGINEERING_PLAN.md)
- [NCA ECC-IS-4: Audit Logging Requirements](https://nca.gov.sa)
- [PDPL Article 29: Data Protection Requirements](https://sdaia.gov.sa)
