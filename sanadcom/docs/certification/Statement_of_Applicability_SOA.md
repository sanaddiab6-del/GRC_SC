# Statement of Applicability (SOA)
## ISO 27001:2022 Information Security Management System

**Organization**: SICO (Saudi Information Compliance Organization)  
**ISMS Scope**: SICO GRC Platform, Cloud Infrastructure, Corporate Network  
**Document Version**: 1.0  
**Approval Date**: 2026-02-09  
**Approved By**: CEO, CISO, Board of Directors

---

## 1. ISMS Scope Definition

### In Scope
- **Systems**: SICO GRC Platform (web application, backend APIs, AI/RAG engine, databases)
- **Infrastructure**: Azure cloud services (Riyadh primary region, Jeddah DR region)
- **Locations**: Riyadh headquarters office, remote workforce (Saudi Arabia)
- **Processes**: Risk management, access control, incident response, business continuity, compliance management
- **Data**: Customer compliance data, audit evidence, security logs, employee records, intellectual property

### Out of Scope
- **None**: Full scope ISO 27001 certification (no exclusions)

---

## 2. Control Applicability Summary

**Total Annex A Controls**: 93  
**Applicable Controls**: 93 (100%)  
**Not Applicable Controls**: 0  
**Justification**: SICO is pursuing full-scope ISO 27001 certification with no exclusions to demonstrate comprehensive security posture to enterprise customers and regulatory authorities.

---

## 3. Control Selection Justification

All 93 ISO 27001:2022 Annex A controls are applicable and implemented:

### A.5 Organizational Controls (37/37)
- **Risk Assessment**: Annual risk assessment with treatment plans for all identified risks
- **Asset Management**: Complete asset inventory (200+ assets) with CIA ratings and ownership
- **Supplier Security**: Vendor risk assessments for all critical suppliers, DPAs, security SLAs
- **Incident Management**: 24/7 CSIRT, PDPL breach notification procedures
- **Business Continuity**: RTO 4h/RPO 1h, DR site, tested quarterly

### A.6 People Controls (8/8)
- **Pre-Employment Screening**: Background checks (identity, employment, criminal, credit for sensitive roles)
- **Security Training**: Mandatory awareness training (100% completion), phishing simulations quarterly
- **Termination**: Offboarding process with access revocation within 2 hours

### A.7 Physical Controls (14/14)
- **Physical Security**: Badge access, CCTV (24/7), biometric server room access
- **Environmental**: Fire suppression, HVAC, UPS, flood detection
- **Azure Data Centers**: ISO 27001 certified facilities with enhanced physical security

### A.8 Technological Controls (34/34)
- **Access Control**: RBAC, MFA, privileged access management, quarterly reviews
- **Cryptography**: TLS 1.3, AES-256, Azure Key Vault (FIPS 140-2 HSMs)
- **Vulnerability Management**: Weekly scans, 7-day critical patch SLA, annual penetration testing
- **Monitoring**: 24/7 SIEM, centralized logging (1-year retention), real-time alerts
- **Secure Development**: SDLC with security requirements, code review, SAST/DAST

---

## 4. Risk-Based Control Selection

**Risk Assessment Methodology**: ISO 27005  
**Risk Treatment Options Applied**:
1. **Risk Mitigation** (90% of controls): Implement security controls to reduce risk to acceptable levels
2. **Risk Avoidance** (5%): Discontinue risky activities (e.g., storing payment card data - not in scope)
3. **Risk Transfer** (3%): Cyber insurance, cloud provider shared responsibility
4. **Risk Acceptance** (2%): Residual risks accepted by management after mitigation

**Critical Controls (P0)**: 28 controls protecting against ransomware, data breaches, system compromise  
**High Priority (P1)**: 45 controls addressing compliance, availability, data integrity  
**Medium Priority (P2)**: 20 controls for operational efficiency and continuous improvement

---

## 5. Control Implementation Status

| **Control Domain** | **Total** | **Fully Implemented** | **Continuously Improving** |
|-------------------|-----------|----------------------|---------------------------|
| A.5 Organizational | 37 | 37 | 12 (enhanced monitoring, AI risk) |
| A.6 People | 8 | 8 | 2 (competency tracking) |
| A.7 Physical | 14 | 14 | 1 (biometric expansion) |
| A.8 Technological | 34 | 34 | 8 (automation, ML detection) |
| **TOTAL** | **93** | **93** | **23** |

---

## 6. Compliance with Saudi Regulations

All ISO 27001 controls aligned with Saudi regulatory requirements:

- **NCA Essential Cybersecurity Controls (ECC)**: 114 controls mapped to ISO 27001
- **NCA Cloud Cybersecurity Controls (CCC)**: 183 controls for Azure cloud services
- **PDPL (Personal Data Protection Law)**: Privacy controls, DPO, breach notification
- **SDAIA AI Ethics Principles**: AI governance, algorithmic transparency, bias testing

---

## 7. Continuous Improvement

**Control Enhancement Roadmap**:
- **Q2 2026**: AI-powered threat detection, automated incident response playbooks
- **Q3 2026**: Zero Trust architecture implementation, micro-segmentation
- **Q4 2026**: Extended Detection and Response (XDR) platform integration

**Performance Monitoring**: KPIs tracked monthly, management review quarterly, Board oversight

---

**Document Owner**: CISO  
**Next Review Date**: 2027-02-09 (annual)  
**Certification Target**: ISO 27001:2022 certification by Q3 2026
