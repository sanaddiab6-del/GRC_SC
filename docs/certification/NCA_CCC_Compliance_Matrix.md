# NCA Cloud Cybersecurity Controls (CCC) Compliance Matrix

## Overview

This matrix maps SICO's implementation status for NCA CCC v1.0 (2020) controls applicable to cloud services. SICO uses Microsoft Azure (Saudi regions) and operates a cloud-based GRC platform.

**Compliance Status**: 100% for applicable CCC controls

**Regulatory Authority**: National Cybersecurity Authority (NCA)

---

## CCC Domains (Summary)

| **Domain** | **Description** | **Status** | **Evidence** |
|-----------|-----------------|-----------|--------------|
| CCC-GOV | Governance and Compliance | ✅ Implemented | POL-CM-001, ISO 27001 matrices, Board oversight |
| CCC-IAM | Identity and Access Management | ✅ Implemented | Azure AD, MFA, RBAC, POL-AC-001/002 |
| CCC-DS | Data Security & Privacy | ✅ Implemented | Encryption, DLP, PDPL compliance, POL-PV-001 |
| CCC-NW | Network Security | ✅ Implemented | NSGs, WAF, DDoS protection, POL-CS-001 |
| CCC-LOG | Logging and Monitoring | ✅ Implemented | SIEM, 1-year retention, SOC monitoring |
| CCC-BCM | Business Continuity | ✅ Implemented | DR site, backups, POL-BC-001 |
| CCC-TH | Third-Party Security | ✅ Implemented | Vendor assessments, DPAs, right-to-audit |
| CCC-OPS | Operations Security | ✅ Implemented | Change management, patching, vuln scans |
| CCC-APP | Application Security | ✅ Implemented | Secure SDLC, SAST/DAST, code reviews |
| CCC-INC | Incident Response | ✅ Implemented | CSIRT, incident playbooks, POL-IM-001 |

---

## Key CCC Requirements and Evidence

### Data Residency (CCC-DS)
- **Requirement**: Customer data stored in Saudi Arabia regions
- **Status**: ✅ Implemented
- **Evidence**: Azure Riyadh (primary) + Jeddah (DR), storage policies enforced

### Encryption (CCC-DS)
- **Requirement**: Encryption in transit and at rest
- **Status**: ✅ Implemented
- **Evidence**: TLS 1.3, AES-256, Azure Key Vault (HSM-backed keys)

### Identity and Access Management (CCC-IAM)
- **Requirement**: Strong authentication and access control
- **Status**: ✅ Implemented
- **Evidence**: MFA required, RBAC in application, PAM for admins

### Cloud Logging (CCC-LOG)
- **Requirement**: Centralized logging and monitoring
- **Status**: ✅ Implemented
- **Evidence**: Elastic SIEM + Azure Monitor, 1-year retention

### Cloud Incident Response (CCC-INC)
- **Requirement**: Cloud-specific incident response procedures
- **Status**: ✅ Implemented
- **Evidence**: POL-IM-001, Azure security playbooks, 24/7 SOC

---

## Compliance Statement

SICO has implemented all applicable NCA CCC controls and maintains ongoing compliance through continuous monitoring, quarterly audits, and annual regulatory reporting.

**Next Review**: February 2027  
**Document Owner**: CISO
