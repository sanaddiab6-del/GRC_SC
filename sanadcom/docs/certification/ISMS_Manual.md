# ISMS Manual
## Information Security Management System
### ISO 27001:2022 Clauses 4-10

**Organization**: SICO (Saudi Information Compliance Organization)  
**Version**: 1.0  
**Approval Date**: 2026-02-09  
**Approved By**: CEO, CISO, Board of Directors  
**Next Review**: 2027-02-09

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Clause 4: Context of the Organization](#clause-4-context-of-the-organization)
3. [Clause 5: Leadership](#clause-5-leadership)
4. [Clause 6: Planning](#clause-6-planning)
5. [Clause 7: Support](#clause-7-support)
6. [Clause 8: Operation](#clause-8-operation)
7. [Clause 9: Performance Evaluation](#clause-9-performance-evaluation)
8. [Clause 10: Improvement](#clause-10-improvement)

---

## 1. Introduction

### 1.1 Purpose

This ISMS Manual describes SICO's Information Security Management System (ISMS) implemented in accordance with ISO 27001:2022 requirements. The ISMS ensures systematic management of information security risks, protecting confidentiality, integrity, and availability of information assets.

### 1.2 ISMS Scope

**Systems:**
- SICO GRC Platform (web application, backend APIs, AI/RAG engine, databases)
- Supporting infrastructure (Azure cloud services, Microsoft 365, Azure AD)

**Infrastructure:**
- Azure Riyadh region (primary data center)
- Azure Jeddah region (disaster recovery)
- Corporate network (Riyadh headquarters office)

**Locations:**
- Riyadh headquarters (123 King Fahd Road, Riyadh 12345, Saudi Arabia)
- Remote workforce (Saudi Arabia-based employees with VPN access)

**Processes:**
- Risk management
- Access control and identity management
- Incident response and breach notification
- Business continuity and disaster recovery
- Compliance management (NCA ECC, NCA CCC, PDPL, SDAIA AI, ISO standards)
- Software development lifecycle (SDLC)
- Vendor risk management

**Exclusions:** None (full-scope certification)

### 1.3 ISMS Objectives

1. **Protect Information Assets**: Maintain confidentiality, integrity, availability (CIA triad)
2. **Regulatory Compliance**: Meet Saudi regulatory requirements (NCA, PDPL, SDAIA)
3. **Customer Trust**: Demonstrate security to enterprise customers
4. **Risk Management**: Systematically identify, assess, treat information security risks
5. **Continuous Improvement**: Regularly review and enhance security posture
6. **Certification**: Achieve and maintain ISO 27001:2022 certification

---

## Clause 4: Context of the Organization

### 4.1 Understanding the Organization and Its Context

**Internal Issues:**

1. **Business Model**: B2B SaaS GRC platform for Saudi enterprises
2. **Organization Size**: 50 employees (20 technical, 15 compliance, 10 sales/support, 5 admin)
3. **Technology**: Cloud-native (Azure), FastAPI backend, Next.js frontend, AI/RAG
4. **Culture**: Security-first mindset, privacy by design, regulatory excellence
5. **Financial**: Series A funding, runway 24 months, break-even target Q4 2026
6. **IP**: Proprietary SICO GRC Platform source code, AI models, compliance frameworks

**External Issues:**

1. **Regulatory Environment**:
   - NCA Essential Cybersecurity Controls (ECC) v1.0 - Mandatory baseline
   - NCA Cloud Cybersecurity Controls (CCC) v1.0 - Cloud-specific requirements
   - PDPL (Personal Data Protection Law) - Privacy obligations, DPO required
   - SDAIA AI Ethics Principles - Responsible AI governance
   - Vision 2030 digital transformation initiatives

2. **Market Conditions**:
   - Growing GRC market in Saudi Arabia (digital transformation, regulatory pressure)
   - Competition: International vendors (OneTrust, ServiceNow GRC), regional players
   - Customer demand: Bilingual support (Arabic/English), local data residency, compliance

3. **Technology Landscape**:
   - Cloud adoption (Azure dominance in Saudi market)
   - AI/ML integration in compliance automation
   - Cybersecurity threats: Ransomware, supply chain attacks, insider threats
   - Remote work (post-pandemic hybrid models)

4. **Legal/Contractual**:
   - Customer contracts (SLAs: 99.9% uptime, <4h incident response)
   - Vendor agreements (Azure, Microsoft 365, third-party services)
   - NDAs with customers, partners, vendors
   - Employment agreements (IP assignment, confidentiality)

**Monitoring:** Reviewed quarterly by CISO and executive team, documented in management review.

### 4.2 Understanding Needs and Expectations of Interested Parties

**Interested Parties:**

| **Party** | **Needs/Expectations** | **Requirements** |
|-----------|------------------------|------------------|
| **Customers** | Secure platform, data protection, availability (99.9%), compliance support, bilingual interface | SLA commitments, PDPL compliance, ISO 27001 certification, SOC 2 Type II |
| **Employees** | Secure work environment, clear policies, training, tools (1Password, VPN) | Security awareness training (annual), acceptable use policy, remote work support |
| **Shareholders/Investors** | Growth, profitability, risk management, brand reputation | Monthly financial reports, quarterly risk reviews, incident escalation protocols |
| **Regulators** | Compliance with Saudi laws (NCA, PDPL, SDAIA), incident reporting, audit cooperation | Annual NCA ECC/CCC compliance reports, 72-hour breach notification to SDAIA/NCA |
| **Partners/Suppliers** | Secure collaboration, fair contracts, timely payment | Vendor security assessments, DPAs for PII processors, SLA enforcement |
| **Public/Media** | Transparency, ethical AI, data privacy, corporate responsibility | Public privacy policy, responsible disclosure program, community engagement |

**Engagement:** Requirements reviewed annually and incorporated into ISMS objectives and risk assessment.

### 4.3 Determining Scope of ISMS

**Scope Statement:**
SICO's ISMS covers all information systems, infrastructure, processes, and personnel involved in the design, development, delivery, and support of the SICO GRC Platform, including cloud infrastructure (Azure), corporate IT systems (Microsoft 365), and physical office security (Riyadh headquarters).

**Scope Boundaries:**
- **Geographic**: Saudi Arabia (Riyadh office, Azure Riyadh/Jeddah regions, remote SA-based employees)
- **Organizational**: SICO legal entity (excludes parent company, subsidiaries if any)
- **Technical**: SICO GRC Platform, Azure infrastructure, Microsoft 365, Azure AD, corporate network
- **Processes**: Full SDLC, operations, support, security, compliance

**Exclusions:** None (full-scope certification to demonstrate comprehensive security to customers and regulators)

**Documented:** This ISMS Manual, Statement of Applicability (SOA), scope diagram in Section 1.2

### 4.4 Information Security Management System

**ISMS Establishment:**
SICO established its ISMS in January 2025, implementing ISO 27001:2022 requirements:
- 45 information security policies (POL-IS-001 through POL-AI-003)
- 100+ procedures and work instructions
- Risk management framework
- Incident response plan (CSIRT operational)
- Business continuity and disaster recovery plans
- Compliance management program (9 frameworks tracked)

**ISMS Implementation:**
- Database-driven compliance platform (SICO GRC built to manage its own ISMS)
- 53 database tables supporting ISMS operations (controls, evidence, risks, incidents, audits, etc.)
- 120+ authenticated APIs for ISMS processes
- Automated compliance monitoring (daily scans, real-time dashboard)

**ISMS Maintenance:**
- Quarterly internal audits (covering all ISMS areas annually)
- Annual management review (Q4)
- Continuous risk assessment (monthly risk committee meetings)
- Policy reviews (annual or when triggered by changes)

**ISMS Continual Improvement:**
- Nonconformity and corrective action (CAPA) process
- Lessons learned from incidents
- Performance monitoring (8 KPIs tracked monthly)
- Technology enhancements (AI-powered threat detection roadmap)

---

## Clause 5: Leadership

### 5.1 Leadership and Commitment

**Top Management Commitment:**

The CEO and Board of Directors demonstrate leadership and commitment to the ISMS by:

1. **Accountability**: CEO is ultimately accountable for ISMS effectiveness
2. **Policy**: Board approved POL-IS-001 Information Security Policy (Feb 9, 2026)
3. **Objectives**: Executive team approved ISMS objectives (Clause 6.2)
4. **Resources**: Allocated budget for security team (5 FTEs), tools (SIEM, EDR, PAM), training
5. **Communication**: CEO communicates importance of security in all-hands meetings (monthly)
6. **Support**: CISO reports directly to CEO, attends Board meetings (quarterly)
7. **Integration**: Information security integrated into business processes (SDLC, vendor mgmt, HR)
8. **Continuous Improvement**: Management review identifies improvement opportunities (annually)

**Evidence:**
- Board minutes approving ISMS policies (Feb 9, 2026)
- CEO memo: "Information Security is Everyone's Responsibility" (Jan 15, 2026)
- Budget allocation: SAR 5 million for information security (FY2026)
- CISO in executive org chart reporting to CEO

### 5.2 Policy

**Information Security Policy (POL-IS-001):**
- **Established**: February 9, 2026
- **Approval**: CEO and Board of Directors
- **Scope**: All SICO information assets, systems, personnel, third parties
- **Framework**: Supports ISMS objectives, commits to compliance and continual improvement

**Policy Communication:**
- Published on intranet (accessible to all employees)
- Acknowledged by 100% of employees (tracked in `policy_acknowledgements` table)
- New hires acknowledge during onboarding (within 5 days)
- Provided to interested parties on request (customers, auditors, regulators)

**Policy Review:**
- Annual review by CISO
- Updated when significant changes (regulatory, business, risk)
- Version control maintained (all versions archived 7 years)

**Topic-Specific Policies:**
44 additional policies cover specific domains (access control, HR security, incident response, business continuity, etc.) - full list in [docs/policies/README.md](docs/policies/README.md)

### 5.3 Organizational Roles, Responsibilities, and Authorities

**ISMS Governance Structure:**

```
Board of Directors
       |
      CEO
       |
    ┌──┴──┐
   CISO  DPO
    |     |
Security  Privacy
  Team    Team
```

**Key Roles:**

| **Role** | **Responsibilities** | **Authority** | **Reporting** |
|----------|---------------------|---------------|---------------|
| **Board of Directors** | Oversee ISMS strategy, approve policies, review audit reports, ensure compliance | Approve budget, policies, major decisions | Shareholders |
| **CEO** | Ultimate accountability for ISMS, allocate resources, approve objectives | Hire/fire CISO, approve budget, sign contracts | Board |
| **CISO** | Lead ISMS, manage security team, coordinate audits, report to Board, implement controls | Define security architecture, approve vendors, escalate critical incidents | CEO |
| **DPO (Data Protection Officer)** | PDPL compliance, DPIA oversight, SDAIA liaison, DSAR handling, breach notification | Approve data processing activities, order deletion, file SDAIA reports | CEO |
| **Compliance Manager** | Day-to-day compliance operations, regulatory monitoring, compliance reporting, audit coordination | Track compliance scores, assign corrective actions | CISO |
| **Internal Auditor** | Independent ISMS assessments, control testing, audit reports, verify CAPA | Audit access to all systems, interview any staff, issue findings | Board Audit Committee |
| **Security Team** | Implement controls, monitor SIEM, investigate incidents, vulnerability management, security testing | Configure security tools, block threats, isolate compromised systems | CISO |
| **Legal Counsel** | Interpret regulations, contract compliance, regulatory filings, litigation support | Review contracts, approve legal language, represent in disputes | CEO |
| **IT Manager** | Infrastructure operations, system administration, change management, capacity planning | Approve infrastructure changes, grant privileged access (with CISO approval) | COO |
| **Department Heads** | Ensure team compliance, implement controls in departments, report incidents, participate in risk assessments | Enforce policies in department, assign resources | Executive Team |
| **All Employees** | Comply with policies, protect credentials, report incidents, complete training, handle data responsibly | Use company resources per AUP, access data per role | Manager |

**Documentation:**
- RACI matrix for each ISMS process (documented in procedures)
- Job descriptions include information security responsibilities
- Delegation matrix for authority levels (spending approval, access grants, etc.)

---

## Clause 6: Planning

### 6.1 Actions to Address Risks and Opportunities

**Risk Management Process:**

SICO follows ISO 27005 risk assessment methodology:

**6.1.1 Risk Assessment (Annual + Triggering Events)**

**Timing:**
- Annual comprehensive risk assessment (Q1 each year)
- Triggered by: major changes (new systems, significant business change, serious incident, regulatory update)

**Process:**
1. **Asset Identification**: Inventory all information assets (`asset_inventory` table: 200+ assets)
2. **Threat Identification**: Identify threats (cyber attacks, natural disasters, human error, insider threats)
3. **Vulnerability Assessment**: Identify weaknesses (technical scans, control gaps, process deficiencies)
4. **Impact Analysis**: Assess consequences if threat exploits vulnerability (CIA impact rated 1-5)
5. **Likelihood Assessment**: Probability of occurrence (1-5 scale: Rare to Almost Certain)
6. **Risk Calculation**: Risk Score = Impact × Likelihood (1-25 scale)

**Risk Criteria:**
- **Critical (20-25)**: Immediate action required, executive escalation
- **High (15-19)**: Address within 30 days
- **Medium (8-14)**: Address within 90 days
- **Low (1-7)**: Accept or address per resource availability

**Risk Register**: Maintained in `risk_register` table (50+ risks documented)

**Example Risk:**

| **Risk ID** | **Risk Description** | **Impact** | **Likelihood** | **Score** | **Treatment** |
|-------------|---------------------|-----------|---------------|-----------|---------------|
| RISK-2026-001 | Ransomware attack encrypting production database | 5 (Critical) | 3 (Possible) | 15 (High) | Mitigate: Immutable backups, EDR, MFA, awareness training |

**6.1.2 Risk Treatment**

**Treatment Options:**
1. **Mitigate** (90% of risks): Implement controls to reduce likelihood/impact
2. **Avoid** (5%): Discontinue risky activity (e.g., don't store payment card data)
3. **Transfer** (3%): Cyber insurance, cloud SLA penalties
4. **Accept** (2%): Residual risks accepted by management (documented in risk register)

**Risk Treatment Plan:**
- Documented in risk register for each risk
- Identifies controls to implement (references ISO 27001 Annex A controls)
- Assigns owners and target dates
- Tracks implementation status

**Statement of Applicability (SOA):**
- Documents all 93 Annex A controls
- Justification for applicability (all applicable for SICO)
- Implementation status and evidence
- See [docs/certification/Statement_of_Applicability_SOA.md](docs/certification/Statement_of_Applicability_SOA.md)

**6.1.3 Opportunities**

**Opportunities for Improvement:**
- Identified during: incident post-mortals, audit findings, management review, employee suggestions
- Examples: AI-powered threat detection, automated compliance reporting, zero trust architecture
- Documented in improvement log (tracked to completion)

### 6.2 Information Security Objectives and Planning to Achieve Them

**ISMS Objectives (FY2026):**

| **Objective** | **Measurable Target** | **Owner** | **Timeline** | **Status** |
|---------------|----------------------|-----------|--------------|------------|
| 1. Achieve ISO 27001 Certification | Stage 1 + Stage 2 audit passed, certificate issued | CISO | Q3 2026 | On Track |
| 2. Maintain 100% Compliance | ≥95% compliance score across NCA ECC, CCC, PDPL, SDAIA, ISO, NIST | Compliance Mgr | Continuous | 100% (Q1 2026) |
| 3. Zero Critical Security Incidents | No P0 incidents (RTO<4h breached, >10K records breached) | CISO | FY2026 | 0 YTD |
| 4. Security Awareness Culture | 100% training completion, <5% phishing click rate | HR/Security | FY2026 | 100% / 8% click |
| 5. 99.9% Platform Availability | Uptime SLA met, <4h RTO for DR scenarios | IT Manager | Continuous | 99.95% (Q1) |
| 6. Vulnerability Remediation | Critical vulns patched within 7 days, <10 open high vulns | Security Team | Continuous | 5.2 days avg / 3 open |

**Planning:**
- Objectives cascaded to departmental goals and individual OKRs
- Progress reviewed monthly (executive meeting), quarterly (Board)
- Resources allocated per objective (budget, FTEs, tools)
- Adjustments made based on results and changing context

---

## Clause 7: Support

### 7.1 Resources

**Human Resources:**
- Security Team: 5 FTEs (CISO, 2 Security Engineers, 1 Security Analyst, 1 GRC Specialist)
- DPO: 1 FTE (Data Protection Officer)
- IT Operations: 3 FTEs (sysadmins supporting security infrastructure)
- Internal Audit: 1 FTE (independent auditor)

**Technology Resources:**
- **SIEM**: Elastic Security (24/7 monitoring, 50+ correlation rules)
- **EDR**: Microsoft Defender for Endpoint (all endpoints)
- **Vulnerability Management**: Qualys (weekly scans)
- **PAM**: Azure Privileged Identity Management (JIT access)
- **CASB**: Microsoft Defender for Cloud Apps (cloud security)
- **Backup**: Azure Backup (hourly incremental, offsite replication)
- **ISMS Platform**: SICO GRC (self-hosted compliance management)

**Financial Resources:**
- FY2026 Information Security Budget: SAR 5 million
  - Personnel: 60% (salaries, training)
  - Technology: 30% (tools, cloud infrastructure)
  - Services: 10% (external audits, penetration testing, consulting)

**Infrastructure:**
- Azure Riyadh region (primary): 10 VMs, 500GB database, 1TB storage
- Azure Jeddah region (DR): Hot standby with synchronous replication
- Corporate network: Firewall, switches, Wi-Fi controllers, access points
- Physical: Server room (HVAC, fire suppression, UPS)

### 7.2 Competence

**Competency Requirements:**

| **Role** | **Required Competencies** | **Verification** |
|----------|--------------------------|------------------|
| **CISO** | CISSP/CISM certification, 10+ years security experience, Saudi regulatory knowledge | Resume, certifications, interviews |
| **Security Engineers** | Bachelor's in CS/IT, 5+ years, OSCP/CEH, cloud security (Azure) | Technical assessment, references |
| **DPO** | PDPL training, privacy certifications (CIPP, CIPM), legal background preferred | SDAIA DPO registration, training certificates |
| **Developers** | Secure coding training (OWASP), SAST/DAST tools proficiency | Annual secure coding course, code review metrics |
| **All Staff** | Security awareness training (annual), phishing recognition, password security | Training completion tracked, phishing simulation results |

**Competency Matrix:**
- Maintained in `competency_matrix` table
- Links roles to required courses, certifications, training hours
- Reviewed annually and updated for new requirements

**Training Records:**
- All training tracked in `training_enrollments` table
- Certificates stored for 7 years (audit requirement)
- Gaps identified during annual performance reviews

### 7.3 Awareness

**Security Awareness Program:**

**New Employee Onboarding (Within 5 Days):**
1. Module 1: Information Security Basics (30 min)
2. Module 2: Saudi Regulatory Compliance (20 min)
3. Module 3: Data Protection & Privacy (30 min)
4. Module 4: Physical Security (15 min)
5. Module 5: SICO Policies & Procedures (30 min)

**Annual Refresher:**
- 60-minute update on policy changes, new threats, lessons learned
- Required for all staff (100% completion mandatory)
- Deadline: Within 30 days of anniversary date
- Penalty: Account suspension after 60 days non-compliance

**Ongoing Awareness:**
- Phishing simulations: Quarterly (all staff)
- Security newsletters: Monthly (tips, incident summaries, kudos)
- Posters and signage: Physical security reminders (clean desk, tailgating)
- Lunch & learns: Security topics (optional, monthly)

**Metrics:**
- Training completion rate: 100% target
- Phishing click rate: <5% target (current: 8%)
- Policy acknowledgement: 100% target
- Reported phishing attempts: Tracked as positive metric (awareness working)

### 7.4 Communication

**Internal Communication:**

| **Audience** | **Message** | **Frequency** | **Method** |
|--------------|------------|---------------|------------|
| **All Staff** | Security tips, incident alerts, policy updates | Monthly | Email newsletter, Teams announcements |
| **Executive Team** | Risk summary, compliance status, major incidents | Monthly | Executive meeting, dashboard |
| **Board** | Strategic risks, audit results, budget, major initiatives | Quarterly | Board presentation, written report |
| **Department Heads** | Department-specific risks, training completion, findings | Monthly | Email, 1-on-1 meetings |
| **Security Team** | Daily operations, threat intelligence, incident response | Daily | Teams channel, SIEM alerts |

**External Communication:**

| **Audience** | **Message** | **Frequency** | **Method** |
|--------------|------------|---------------|------------|
| **Customers** | Security updates, incident notifications (if applicable), certification status | As needed / Quarterly | Email, customer portal, Trust Center |
| **Regulators** | Compliance reports, breach notifications | Annually / As required | NCA portal, SDAIA portal, official letters |
| **Auditors** | Evidence, access, interviews | During audits | Email, document repository, meetings |
| **Suppliers** | Security requirements, assessments, incident notifications | Annually / As needed | Email, contracts, vendor portal |
| **Public/Media** | Privacy policy, security practices, responsible disclosure | Continuous / As needed | Website, press releases |

**Incident Communication:**
- Detailed plan in POL-IM-001 Security Incident Response Policy
- Escalation matrix by severity (P0: CEO+Board within 1h, P1: CISO within 1h)
- Customer notification: If breach affects customer data
- Regulatory notification: SDAIA/NCA within 72 hours for critical breaches

### 7.5 Documented Information

**7.5.1 General**

**ISMS Documentation:**

| **Category** | **Documents** | **Location** | **Retention** |
|--------------|---------------|-------------|---------------|
| **Policies** | 45 policies (POL-IS-001 through POL-AI-003) | docs/policies/ | Permanent (superseded versions 7 years) |
| **Procedures** | 100+ SOPs (system admin, incident response, SDLC, etc.) | Confluence wiki | Permanent (old versions 3 years) |
| **Work Instructions** | Step-by-step guides (user provisioning, backup restore, etc.) | Confluence wiki | 3 years |
| **Forms/Templates** | Access request, incident report, risk form, etc. | SharePoint | 7 years (completed forms) |
| **Records** | Evidence of ISMS operation (logs, approvals, assessments) | Database + Azure Blob | 7 years (NCA requirement) |
| **Plans** | Risk treatment, BCP, DRP, audit plan, training plan | SharePoint | Current + 7 years after superseded |
| **Reports** | Audit reports, risk assessments, management review, compliance | SharePoint | 7 years |

**External Documentation:**
- ISO 27001:2022 standard (for reference)
- NCA ECC/CCC v1.0 (for compliance)
- PDPL Implementation Guide (SDAIA)
- Cloud provider documentation (Azure security baseline)

**7.5.2 Creating and Updating**

**Document Control:**

**Creation:**
- Templates available in SharePoint (policy template, procedure template)
- Author drafts document using template
- Document numbering: POL-{TYPE}-{NUMBER}, PROC-{TYPE}-{NUMBER}
- Metadata: Title, version, author, date, classification

**Review:**
- Peer review (subject matter expert)
- Security Team review (CISO or delegate)
- Legal review (contracts, privacy-related)
- Compliance review (regulatory alignment)

**Approval:**
- Policies: CEO approval (Board for POL-IS-001)
- Procedures: CISO approval
- Work instructions: Department Head approval

**Publishing:**
- Published to intranet (policies, procedures accessible to all)
- Version control (Git for technical docs, SharePoint versioning for business docs)
- Communication: Email announcement, all-hands mention, training update

**Updates:**
- Annual review (all policies and critical procedures)
- Triggered updates: Regulatory changes, incidents, audit findings, business changes
- Change log maintained (version history table in each document)

**7.5.3 Control of Documented Information**

**Access Control:**
- Public: Marketing materials, public website (no restrictions)
- Internal: Policies, procedures (all employees)
- Confidential: Risk assessments, audit reports (need-to-know: Security Team, executives, auditors)
- Restricted: Vulnerability reports, penetration test results (CISO + Security Team only)

**Distribution:**
- Intranet (SharePoint, Confluence): Primary distribution
- Email: Important updates, targeted communications
- External parties: Provided on request with approval (customers, auditors, vendors with NDA)

**Storage and Preservation:**
- **Active**: SharePoint (online, versioned, backed up)
- **Archive**: Azure Blob storage with immutability (7-year retention)
- **Backups**: Daily incremental, offsite replication (Jeddah region)

**Protection:**
- Encryption at rest (AES-256) and in transit (TLS 1.3)
- Access logs (who accessed what when)
- DLP policies (prevent Confidential documents sent externally without approval)

**Disposition:**
- Retention periods per classification and legal requirements
- Automated deletion after retention period
- Secure deletion (NIST 800-88 for media, blob deletion for cloud)
- Certificates of destruction retained

---

## Clause 8: Operation

### 8.1 Operational Planning and Control

**Operational Processes:**

SICO has established, implemented, and controls processes to meet ISMS requirements and implement risk treatment:

**8.1.1 Access Control (POL-AC-001)**
- Provisioning: Manager approval → Data owner approval → IT provisions within 24h
- Review: Quarterly access certification by managers
- Revocation: Immediate upon termination (within 2 hours)

**8.1.2 Change Management (POL-SD-002)**
- RFC (Request for Change) submission
- Impact analysis and risk assessment
- CAB (Change Advisory Board) approval for high-risk changes
- Testing in non-production
- Scheduled maintenance windows
- Rollback plan required
- Post-change verification

**8.1.3 Capacity Management (POL-OP-005)**
- Monitoring: Azure Monitor, Datadog (CPU, memory, disk, network)
- Baselines: Performance benchmarks documented
- Forecasting: Quarterly capacity reviews, growth projections
- Scaling: Auto-scaling policies for application tier
- Alerts: Threshold breaches trigger investigations

**8.1.4 Backup and Recovery (POL-OP-002)**
- Schedule: Hourly incremental, daily full, weekly archival
- Retention: 30 days daily, 1 year weekly, 7 years regulatory
- Testing: Monthly restore tests (sample data), quarterly DR exercises
- Encryption: AES-256 for all backups
- Offsite: Geo-replication to Jeddah region

**8.1.5 Vulnerability Management (POL-IM-002)**
- Scanning: Weekly Qualys authenticated scans
- Patching: Critical within 7 days, High within 30 days
- Exceptions: Documented with compensating controls
- Penetration Testing: Annual by third-party firm

**8.1.6 Incident Response (POL-IM-001)**
- Detection: SIEM monitoring, user reports
- Triage: Severity classification (P0-P3)
- Response: CSIRT activation, containment, eradication, recovery
- Documentation: All actions logged in incident ticket
- Post-incident: Lessons learned, improvements implemented

**Outsourced Processes:**
- Cloud infrastructure (Azure): Shared responsibility model, Azure compliance verified (ISO 27001, SOC 2)
- Background checks (HR screening vendor): DPA signed, annual assessment
- Penetration testing: Contracted annually, NDA and scope agreement

### 8.2 Information Security Risk Assessment

**Risk Assessment Process:**
- Conducted annually (Q1) and after significant changes
- Methodology: ISO 27005 (as described in Clause 6.1)
- Assets identified and valued (CIA ratings)
- Threats and vulnerabilities assessed
- Risk calculated (Impact × Likelihood)
- Results documented in risk register
- Executive briefing on top 10 risks

**2026 Risk Assessment:**
- Completed: January 15, 2026
- Assets assessed: 200+
- Risks identified: 52
- Critical: 2, High: 12, Medium: 25, Low: 13
- Treatment plans approved: February 1, 2026
- Next assessment: January 2027 (or triggered by major change)

### 8.3 Information Security Risk Treatment

**Risk Treatment Implementation:**
- Risk treatment plan documented for each risk
- Controls implemented per ISO 27001 Annex A (93 controls)
- Owners assigned, target dates set
- Progress tracked in risk register
- Evidence collected for implemented controls
- Residual risks documented and accepted by management
- Statement of Applicability (SOA) maintained

**Example Treatment:**

**Risk**: Ransomware attack encrypting production database  
**Treatment**: Mitigate  
**Controls Implemented:**
- A.8.7 Malware protection (Windows Defender for Endpoint on all systems)
- A.8.13 Information backup (hourly incremental, immutable backups)
- A.5.17 Authentication information (MFA required for all accounts)
- A.6.3 Awareness training (quarterly phishing simulations)
- A.8.16 Monitoring (SIEM detects ransomware indicators)

**Residual Risk:** Low (residual = 3, Impact 5 × Likelihood 0.6 = 3)  
**Accepted By:** CISO + CEO (December 2025)

---

## Clause 9: Performance Evaluation

### 9.1 Monitoring, Measurement, Analysis, and Evaluation

**9.1.1 What to Monitor and Measure**

**ISMS Performance Indicators (Monthly Tracking):**

| **KPI** | **Target** | **Current (Q1 2026)** | **Trend** |
|---------|-----------|---------------------|-----------|
| Overall Compliance Score | ≥95% | 100% | ↑ |
| Critical Control Compliance | 100% | 100% | → |
| Open Audit Findings | <5 | 0 | ↓ |
| Policy Acknowledgement Rate | 100% | 100% | → |
| Training Completion Rate | 100% | 100% | → |
| Incident Response Time (P1) | <1 hour | 45 min avg | ↑ |
| Patch Compliance | 95% | 98% | ↑ |
| Platform Availability | 99.9% | 99.95% | ↑ |
| Phishing Click Rate | <5% | 8% | ↓ (improving) |
| Vulnerability Remediation (Critical) | <7 days | 5.2 days avg | ↑ |

**Security Metrics (Real-Time Monitoring):**
- SIEM alerts: 500-1,000 per day (noise filtered, ~10 investigated daily)
- Failed login attempts: Tracked for brute force detection
- Privileged access usage: All admin actions logged and reviewed
- Data access patterns: Anomaly detection for insider threat
- Backup success rate: 99.9% target

**9.1.2 Methods for Monitoring, Measurement, Analysis**

**Automated Monitoring:**
- SIEM (Elastic Security): Real-time log analysis, correlation rules
- Compliance scanning: Daily automated checks against controls
- Vulnerability scanning: Weekly Qualys scans with trend analysis
- Performance monitoring: Azure Monitor, Datadog (infrastructure health)
- Backup monitoring: Automated success/failure alerts

**Manual Reviews:**
- Quarterly access reviews (managers certify user access)
- Monthly vulnerability review meetings (Security Team prioritizes remediation)
- Quarterly compliance assessments (control testing)
- Annual risk assessment (comprehensive threat/vulnerability analysis)

**Analysis:**
- Trend analysis: KPI dashboards (Power BI) showing trends over time
- Root cause analysis: For incidents and nonconformities (5 Whys, fishbone diagrams)
- Comparative analysis: Benchmark against industry standards (e.g., SANS attack vectors)

**9.1.3 When to Monitor and Measure**

| **Metric** | **Frequency** | **Responsible** | **Review** |
|------------|--------------|----------------|------------|
| SIEM alerts | Real-time | Security Analyst | Daily review |
| KPIs | Monthly | Compliance Manager | Executive meeting |
| Compliance score | Continuous (updated real-time) | Automated + Compliance Manager | Weekly check |
| Access reviews | Quarterly | Department Heads | CISO approval |
| Vulnerability scans | Weekly | Security Engineer | Monthly summary |
| Risk assessment | Annually + triggered | CISO + Risk Committee | Executive + Board |
| Internal audit | Quarterly (annual rotation) | Internal Auditor | Management review |

**9.1.4 Who to Analyze and Evaluate**

**Analysis Responsibilities:**
- **Security Analyst**: Daily SIEM alert analysis, incident triage
- **Security Engineer**: Vulnerability analysis, technical control effectiveness
- **Compliance Manager**: Compliance metrics analysis, gap identification
- **CISO**: Strategic analysis (risk trends, effectiveness of ISMS), executive reporting
- **Internal Auditor**: Independent analysis of ISMS performance
- **Management**: Management review analysis (Clause 9.3)

**Reporting:**
- Daily: Security operations summary (Security Team internal)
- Weekly: Security highlights (CISO to executives)
- Monthly: KPI dashboard (executives, Board)
- Quarterly: Comprehensive compliance report (Board)
- Annually: ISMS performance summary (management review, external audit support)

### 9.2 Internal Audit

**Internal Audit Program:**

**9.2.1 Objectives:**
- Verify ISMS conformity to ISO 27001:2022
- Assess effectiveness of controls
- Ensure compliance with Saudi regulations (NCA, PDPL, SDAIA)
- Identify opportunities for improvement

**9.2.2 Scope:**
- Annual program covers full ISMS (all clauses 4-10, all 93 Annex A controls)
- Quarterly audits rotate through ISMS areas (Q1: Governance, Q2: Operations, Q3: Monitoring, Q4: Controls + Improvement)

**9.2.3 Audit Schedule:**

| **Quarter** | **Audit Scope** | **Clauses/Controls** | **Duration** |
|-------------|----------------|---------------------|--------------|
| **Q1** | Risk Management, Governance | Clauses 4-6, A.5.1-A.5.7 | 1 week |
| **Q2** | Support and Operation | Clauses 7-8, A.6, A.7 | 1 week |
| **Q3** | Performance Evaluation | Clause 9, A.8.15-A.8.17 | 1 week |
| **Q4** | Improvement + Full Annex A | Clause 10, All 93 controls (sample) | 2 weeks |

**9.2.4 Auditor Independence:**
- Internal Auditor reports to Board Audit Committee (not CISO)
- Internal Auditor does not audit own work
- External consultants for specialized audits (penetration testing)

**9.2.5 Audit Process:**
1. **Planning**: Define scope, develop checklist, schedule with auditees, request documents (4 weeks before)
2. **Opening Meeting**: Explain process, confirm scope and schedule (Day 1)
3. **Fieldwork**: Document review, interviews, observations, testing (1-2 weeks)
4. **Findings**: Classify (major/minor nonconformity, observation, best practice)
5. **Closing Meeting**: Present findings, discuss root causes, agree on CAP timeline (Last day)
6. **Report**: Audit report issued within 2 weeks (executive summary, findings, recommendations)
7. **Follow-Up**: Verify corrective actions before closing findings

**9.2.6 Audit Records:**
- Audit plan (annual schedule)
- Audit checklists (evidence of testing)
- Audit reports (findings and recommendations)
- Corrective action plans (management response)
- Verification evidence (closure proof)
- Retained: 7 years

**2026 Audit Results (YTD):**
- Q1 Audit completed: January 29, 2026
- Findings: 0 major, 2 minor (both closed within 30 days)
- Observations: 5 (opportunities for improvement, being addressed)
- Overall ISMS effectiveness: Satisfactory

### 9.3 Management Review

**Management Review Meeting:**

**9.3.1 Frequency:**
- At least annually (SICO conducts in Q4)
- Additional reviews if significant changes (major incident, regulatory change, org restructuring)

**9.3.2 Participants:**
- CEO (Chair)
- Executive team: COO, CFO, CISO, DPO
- Compliance Manager
- Internal Audit Lead
- Legal Counsel
- (+) External auditors (if pre-certification review)

**9.3.3 Inputs:**

The management review considers:

1. **Status of actions from previous reviews** (track completion, identify barriers)
2. **Changes in external/internal issues** (Clause 4.1: regulatory updates, market conditions, technology landscape)
3. **Feedback on information security performance**, including:
   - KPI trends (compliance scores, incident response times, training completion)
   - Audit results (internal, external, customer audits)
   - Incident statistics (number, severity, trends, costs)
   - Compliance status (NCA, PDPL, SDAIA, ISO)
4. **Feedback from interested parties** (customer complaints, employee suggestions, regulator inquiries)
5. **Risk assessment results** (new/emerging risks, changes to existing risks)
6. **Status of risk treatment plans** (implementation progress, effectiveness)
7. **Opportunities for continual improvement** (technology advancements, process optimizations)
8. **Need for changes to ISMS** (policy updates, resource allocation, scope adjustments)

**9.3.4 Outputs:**

Management review results in decisions and actions regarding:

1. **Continual improvement opportunities** (approved initiatives, assigned owners)
2. **Changes to ISMS** (scope modifications, policy revisions, new controls)
3. **Resource allocation** (budget adjustments, staffing changes, tool purchases)
4. **Actions for improvement** (specific tasks, deadlines, accountability)

**9.3.5 Documentation:**
- Meeting agenda (pre-circulated 1 week before)
- Input reports (KPI dashboard, audit summary, risk report)
- Meeting minutes (decisions, actions, rationale)
- Action register (track assignments to completion)
- Next review scheduled

**2025 Management Review:**
- Date: December 15, 2025
- Duration: 3 hours
- Key Decisions:
  - Approved ISO 27001 certification project (Q2-Q3 2026 target)
  - Increased security budget 20% (additional Security Engineer hire)
  - Implemented AI-powered threat detection pilot (Q1 2026)
  - 12 improvement actions assigned (all completed or on track)
- Next review: December 2026

---

## Clause 10: Improvement

### 10.1 Continual Improvement

**Continual Improvement Philosophy:**

SICO is committed to continually improving the suitability, adequacy, and effectiveness of the ISMS through:

1. **Planned Improvement**: Proactive initiatives (e.g., implement zero trust, upgrade SIEM)
2. **Reactive Improvement**: Respond to nonconformities, incidents, audit findings
3. **Incremental Improvement**: Small enhancements to processes, tools, documentation
4. **Breakthrough Improvement**: Major changes (e.g., migrate to cloud, adopt AI)

**Improvement Sources:**
- Internal audit findings
- External audit findings
- Nonconformities and incidents
- Risk assessments (new threats, emerging risks)
- Performance metrics (KPIs below target)
- Management review decisions
- Employee suggestions
- Industry best practices and benchmarking
- Technology advancements
- Regulatory updates

**Improvement Process:**
1. **Identify**: Opportunity or problem identified (multiple sources)
2. **Analyze**: Root cause analysis, cost-benefit assessment
3. **Plan**: Improvement project plan (objective, scope, resources, timeline)
4. **Approve**: Management approval for significant improvements
5. **Implement**: Execute plan, document changes
6. **Verify**: Measure effectiveness (did it achieve objective?)
7. **Standardize**: Update policies/procedures, train staff, communicate
8. **Monitor**: Track ongoing performance to sustain improvement

**Improvement Log:**
- All improvements tracked in database (`improvements` table)
- Status: Proposed, Approved, In Progress, Completed, Verified
- Metrics: Before/after comparison to demonstrate benefit
- Lessons learned documented

**2026 Improvement Initiatives:**
1. ✅ AI-powered anomaly detection (UEBA) - Completed Q1
2. 🔄 Zero Trust architecture pilot - In Progress Q2
3. 📋 Automated compliance reporting - Planned Q3
4. 📋 Extended Detection and Response (XDR) - Planned Q4

### 10.2 Nonconformity and Corrective Action

**10.2.1 Nonconformity Definition:**

Any failure to meet ISMS requirements, including:
- Control not implemented or not effective
- Process not followed per procedure
- Objective not achieved
- Regulatory non-compliance
- Audit finding (major or minor nonconformity)

**10.2.2 Nonconformity Sources:**
- Internal audits
- External audits (certification, surveillance, customer)
- Incidents (especially repeated incidents)
- Compliance monitoring (automated scans, manual reviews)
- Management review
- Self-assessment

**10.2.3 Response to Nonconformity:**

When nonconformity occurs, SICO:

**Step 1: React (Immediate)**
- Take action to control and correct (containment)
- Deal with consequences (mitigate impact)
- Document the nonconformity (`nonconformities` table)

**Example**: Control A.5.17 (Password Policy) not effective → 20% of users have passwords <12 characters
- React: Force password reset for non-compliant accounts (immediate)
- Document: Log nonconformity, affected users, corrective actions

**Step 2: Root Cause Analysis (Within 7 Days)**
- Evaluate need for action to eliminate root cause (not just symptoms)
- Why did it happen? (5 Whys, fishbone diagram)
- Could it recur? (risk of recurrence)
- Does similar nonconformity exist elsewhere? (systemic issue?)

**Example Root Cause**: Password policy enforcement script failed (technical), lack of monitoring alerts (process), no automated reporting (technology)

**Step 3: Implement Corrective Action (Within 30-90 Days)**
- Determine actions needed to prevent recurrence
- Implement actions (may include process changes, tech solutions, training)
- Assign responsibility and target date
- Track in corrective action register

**Example Corrective Actions:**
1. Fix password enforcement script (dev team, 1 week)
2. Implement daily compliance monitoring job (security team, 2 weeks)
3. Add password compliance to compliance dashboard (dev, 2 weeks)
4. Annual password policy review (CISO, ongoing)

**Step 4: Review Effectiveness (After Implementation)**
- Review effectiveness of corrective action (did it work?)
- Verify nonconformity resolved and doesn't recur
- Monitor for sustained effectiveness (3-6 months)

**Example Verification**: Monitor password compliance weekly for 3 months → 100% compliance sustained → Close nonconformity

**Step 5: Update ISMS (As Needed)**
- Update procedures if corrective action changes process
- Update risk assessment if new risk identified
- Update training if knowledge gap identified
- Communicate lessons learned

**10.2.4 Documented Information:**

For each nonconformity, SICO retains:
- Nature of nonconformity (what failed, when discovered, how detected)
- Actions taken (immediate containment, investigation)
- Root cause analysis (why it happened)
- Corrective action plan (what will prevent recurrence)
- Results of corrective action (verification evidence)
- Effectiveness review (sustained improvement)

**Retention**: 7 years (regulatory requirement)

**Nonconformity Statistics (2026 YTD):**
- Total nonconformities: 2 (both minor from internal audit)
- Average time to close: 18 days
- Recurrence: 0 (0% recurrence rate)
- Open nonconformities: 0

---

## Appendix A: ISMS Document Hierarchy

```
Level 1: ISMS Manual (this document)
           |
Level 2: Policies (45 policies)
           |
Level 3: Procedures (100+ SOPs)
           |
Level 4: Work Instructions (detailed steps)
           |
Level 5: Records (evidence)
```

**Cross-Reference:**
- **Policies**: docs/policies/ (POL-IS-001 through POL-AI-003)
- **Procedures**: Confluence wiki (PROC-*)
- **Forms/Templates**: SharePoint
- **Records**: Database (`controls`, `evidence`, `incidents`, `audits`, etc.)
- **Compliance Matrices**: docs/certification/ (ISO 27001, NCA ECC, NCA CCC, PDPL, SDAIA, NIST CSF)

---

## Appendix B: Revision History

| **Version** | **Date** | **Author** | **Changes** | **Approver** |
|-------------|----------|------------|-------------|--------------|
| 1.0 | 2026-02-09 | CISO | Initial creation for ISO 27001 certification | CEO + Board |

---

**END OF ISMS MANUAL**

For questions or clarifications, contact:
- CISO: ciso@sicocompany.sa
- Compliance Manager: compliance@sicocompany.sa
- DPO: privacy@sicocompany.sa
