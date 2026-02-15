# Evidence Library Index

## Purpose

This index defines required evidence artifacts for ISO 27001, NCA ECC/CCC, PDPL, and SDAIA AI audits. Evidence artifacts are linked to control IDs and stored in the SICO GRC evidence repository.

---

## Evidence Categories

1. **Policies**: Approved policy documents (PDF)
2. **Procedures**: SOPs, runbooks, playbooks
3. **Logs and Reports**: SIEM logs, access logs, audit reports
4. **System Configurations**: Screenshots, config exports
5. **Training Records**: Completion reports, attendance logs
6. **Risk Management**: Risk register, treatment plans, approvals
7. **BCP/DR**: Test results, recovery plans, backup reports
8. **Vendor Management**: DPAs, security questionnaires, assessments

---

## Evidence Mapping (Sample)

| **Control** | **Evidence Type** | **Artifact** | **Retention** |
|-------------|------------------|--------------|---------------|
| ISO A.5.15 | Policy | POL-AC-001 Access Control Policy | 7 years |
| ISO A.5.17 | Policy | POL-AC-002 Password Policy | 7 years |
| ECC-IM-1 | Procedure | Incident Response Playbook | 7 years |
| PDPL Art.14 | Report | Breach Notification Report Template | 7 years |
| CCC-IAM-2 | Config | Azure AD MFA Policy Screenshot | 2 years |
| SDAIA AI-1 | Report | AI Governance Committee Minutes | 7 years |

---

## Evidence Collection Owners

| **Evidence Area** | **Owner** |
|-------------------|----------|
| Policies and SOPs | CISO Office |
| Access Control | IAM Team |
| Logging and Monitoring | SOC Lead |
| Risk Management | Risk Manager |
| Training Records | HR/Training Lead |
| Business Continuity | IT Operations |
| Vendor Management | Procurement |
| Privacy/PDPL | DPO |

---

## Repository Location

- **Primary**: `\\fileserver\evidence\2026\` (restricted access)
- **Backup**: Encrypted Azure Blob Storage (immutable)

**Retention**: 7 years minimum (NCA requirement)

---

**Owner**: Compliance Manager  
**Last Updated**: 2026-02-09
