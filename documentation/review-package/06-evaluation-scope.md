# Sanadcom GRC Platform — Evaluation Scope Document

**Prepared for:** All Reviewers (Technical / Academic / Practitioner)  
**Prepared by:** Sanadcom Team  
**Classification:** Confidential — Shared Under NDA  
**Date:** May 2026  
**Version:** 1.0

---

## 1. Purpose of This Document

This document defines the **scope, boundaries, and objectives** of the evaluation engagement. It ensures mutual alignment between the Sanadcom team and the reviewer regarding what is — and is not — subject to review.

Please read this document before beginning any evaluation activity.

---

## 2. Evaluation Objectives

| Reviewer Type | Primary Objective |
|--------------|------------------|
| **Technical / Developer** | Assess architectural soundness, code quality, security posture, and production readiness. Identify risks and improvement opportunities. |
| **Academic / GRC Scholar** | Evaluate methodology correctness, standards alignment, framework coverage completeness, and scholarly rigor of compliance model design. |
| **Practitioner / Consultant** | Validate that the platform solves real-world GRC use cases effectively. Assess feature completeness, usability, and integration fit for enterprise deployment. |

---

## 3. In-Scope Items

### 3.1 Systems & Environments

| Environment | Scope | Access |
|-------------|-------|--------|
| **Sandbox / Demo environment** | Fully in scope — all features available | Credentials provided by team |
| **GitHub repository** (read-only) | In scope for code review under NDA | Access granted per NDA |
| **API documentation** | In scope — accessible at `/api/schema/swagger-ui/` on sandbox | No credentials needed |
| **Documentation directory** | In scope — `documentation/` folder in repository | Included in repo access |

### 3.2 Areas for Review

**Technical Reviewer:**
- System architecture and data flow design
- Authentication and authorization implementation
- Security controls and OWASP Top 10 compliance
- Database model design and migration strategy
- API design and documentation completeness
- Dependency management and known vulnerabilities
- Deployment architecture (Docker Compose / Kubernetes)
- Test coverage and CI/CD readiness

**Academic Reviewer:**
- Framework library completeness and accuracy vs. published standards
- Compliance methodology correctness (EBIOS RM, qualitative/quantitative risk)
- Evidence model and chain-of-custody design
- Validation workflow alignment with standards (ISO 27001:2022, DORA, SOC 2)
- Data model design for multi-framework compliance
- Methodological citations and standards references

**Practitioner Reviewer:**
- Workflow completeness for named GRC use cases (see Practitioner Package §3)
- Usability of compliance assessment, risk assessment, and evidence workflows
- Reporting quality and audit-readiness of outputs
- Integration ecosystem fit
- Feature gaps relative to stated use cases
- Comparison accuracy vs. competitor capabilities listed in Practitioner Package §5

---

## 4. Out-of-Scope Items

The following are explicitly **not** within the scope of this evaluation:

| Out-of-Scope Item | Reason |
|------------------|--------|
| **Production environment** | No production system exists yet; sandbox only |
| **Active exploitation of discovered vulnerabilities** | Responsible disclosure applies; no unauthorized exploitation |
| **Customer or organizational data** | Sandbox uses anonymized sample data only; no real data present |
| **Financial terms, licensing, or pricing negotiations** | Separate commercial discussion |
| **Source code modification or pull requests** | Read-only access; review only |
| **Social engineering or physical security** | Not applicable to this engagement |
| **Non-platform infrastructure** (e.g., reviewer's own network) | Outside platform scope |
| **Features explicitly marked "Roadmap"** | Future development; not yet implemented |
| **Enterprise edition features** | Not included in community/sandbox access |

---

## 5. Engagement Rules of Engagement

### 5.1 Technical Reviewers — Security Testing Rules

1. **Sandbox only:** All testing activity must be confined to the designated sandbox environment. Production systems (if any) are off-limits.
2. **No DoS testing:** Do not perform denial-of-service testing, fuzzing that could destabilize the sandbox, or automated scanning without prior agreement.
3. **Responsible disclosure:** Any discovered vulnerabilities must be reported to the Sanadcom security contact (`[insert security contact email]`) within 48 hours of discovery. Do not disclose to third parties.
4. **No credential sharing:** Sandbox credentials are issued to named individuals and must not be shared.
5. **Data handling:** Any data exported from the sandbox must be treated as Confidential Information under the NDA.

### 5.2 Academic Reviewers

1. **Attribution:** If the platform's design is cited in academic work, obtain written permission from the Sanadcom team before publication.
2. **No publication of Confidential Information:** Architecture diagrams, source code, or internal methodology documents may not be published without written consent.
3. **Feedback channel:** Academic critiques and suggestions should be directed to `[insert contact]`; the team welcomes collaborative engagement.

### 5.3 Practitioner Reviewers

1. **No client recommendations without disclosure:** Do not recommend or recommend against the platform to your clients based on this evaluation without the Sanadcom team's knowledge.
2. **Competitive intelligence:** Information shared under NDA may not be used to benefit a competing product or service.
3. **Feedback format:** Please use the Evaluation Feedback Template (Section 7) to structure your findings.

---

## 6. Deliverables Expected from Reviewer

| Reviewer Type | Expected Deliverable | Format | Deadline |
|--------------|---------------------|--------|---------|
| **Technical** | Security and architecture review report | Markdown or PDF | _____ days from access grant |
| **Academic** | Standards alignment assessment | Written report | _____ days from access grant |
| **Practitioner** | Feature gap and use case fit analysis | Structured report or call | _____ days from access grant |

---

## 7. Evaluation Feedback Template

Please use the following structure when providing feedback:

```
SANADCOM GRC PLATFORM — EVALUATION FEEDBACK

Reviewer Name: ___________________________
Reviewer Role: [ ] Technical  [ ] Academic  [ ] Practitioner
Date: ___________________________

--- SUMMARY ---
Overall assessment: [ ] Meets expectations  [ ] Partially meets  [ ] Does not meet

--- STRENGTHS ---
(List 3–5 notable strengths observed)

1.
2.
3.

--- AREAS OF CONCERN ---
(List issues with severity: Critical / High / Medium / Low)

1. [Severity] — Description — Recommendation
2.
3.

--- GAPS IDENTIFIED ---
(Missing features, methodology gaps, or integration absences)

1.
2.

--- QUESTIONS FOR THE TEAM ---
(Open questions requiring clarification from Sanadcom)

1.
2.

--- RECOMMENDATION ---
[ ] Recommend for intended use case (with conditions noted above)
[ ] Recommend with significant caveats
[ ] Do not recommend — reasons:

Signature: _______________________________
Date: ___________________________________
```

---

## 8. Points of Contact

| Role | Contact | Email |
|------|---------|-------|
| Technical lead | [Name] | [email] |
| Security contact (for vulnerability reports) | [Name] | [email] |
| Academic / standards queries | [Name] | [email] |
| Sandbox access and credentials | [Name] | [email] |
| General evaluation coordination | [Name] | [email] |

---

## 9. Timeline

| Milestone | Date |
|-----------|------|
| NDA signed | ____________ |
| Repository / sandbox access granted | ____________ |
| Kickoff call (optional) | ____________ |
| Mid-point check-in (optional) | ____________ |
| Evaluation feedback due | ____________ |
| Debrief meeting | ____________ |

---

## 10. Acknowledgement

By accepting access to the sandbox environment, repository, or any materials shared under this engagement, the reviewer acknowledges having read and agreed to the terms of this Evaluation Scope Document and the associated NDA.

Reviewer name: ___________________________  
Date: ___________________________________  
Signature: _______________________________

---

*Sanadcom GRC Platform — Evaluation Scope Document — May 2026*  
*Confidential — All information shared under NDA*
