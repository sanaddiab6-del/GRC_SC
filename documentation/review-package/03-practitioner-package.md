# Sanadcom GRC Platform — Practitioner Review Package

**Prepared for:** GRC Consultants, vCISOs, Compliance Practitioners  
**Prepared by:** Sanadcom Product Team  
**Classification:** Confidential — Shared Under NDA  
**Date:** May 2026  
**Revision:** 1.0

---

## 1. Platform Overview for Practitioners

Sanadcom is a **unified GRC management platform** designed for organizations that need to manage compliance, risk, and governance activities across multiple frameworks simultaneously — without tool fragmentation or duplicated data entry.

**The core practitioner problem we solve:** Most organizations use separate spreadsheets, ticketing tools, and point solutions for risk registers, compliance checklists, evidence collection, and audit trails. Sanadcom consolidates all of these into a single system with native cross-framework control reuse, automated evidence expiry tracking, and out-of-the-box PDF reporting.

---

## 2. Demo Environment

A pre-configured sandbox environment is available for evaluation:

| Detail | Information |
|--------|------------|
| **Access** | Contact team for sandbox URL and credentials |
| **Data** | Anonymized sample organization with pre-loaded ISO 27001 + NIST CSF + ECC assessments |
| **Preloaded content** | 3 risk assessments, 2 compliance assessments, 20+ controls, 10+ evidence records |
| **Reset policy** | Sandbox resets nightly; changes are safe to make |
| **Scope** | Full feature access; no production data |

> **Important:** The sandbox is isolated from production. You are free to create, edit, and delete objects without risk.

---

## 3. Feature List Mapped to GRC Use Cases

### 3.1 Risk Management

| GRC Use Case | Platform Feature | How It Works |
|-------------|-----------------|-------------|
| **Risk Register** | Risk Assessments module | Create named risk assessments per scope; log scenarios with probability × impact matrix; track inherent vs. residual risk |
| **Risk Scoring & Matrix** | Configurable risk matrices | 3×3 to 5×5 matrices with custom scales; color-coded heat maps; visual matrix display |
| **Risk Treatment Plans** | Applied Controls + treatment tracking | Link risk scenarios to mitigating controls; track treatment status (open/in progress/resolved) |
| **Risk Acceptance** | Validation workflow | Formal risk acceptance flow with named approver; timestamped audit record |
| **Quantitative Risk** | CRQ module | Scenario-based quantitative studies with financial impact modeling |
| **EBIOS RM** | EBIOS RM module | Full 5-workshop EBIOS Risk Manager implementation (stakeholders, feared events, attack paths, scenarios) |
| **Asset Register** | Assets module | Classify assets by type, criticality; link to risk scenarios |
| **Incident Tracking** | Incidents module | Log and categorize security incidents; link to affected assets and controls |

### 3.2 Compliance Management

| GRC Use Case | Platform Feature | How It Works |
|-------------|-----------------|-------------|
| **Multi-framework compliance** | Compliance Assessments | Run parallel assessments against ISO 27001, NIST CSF, and ECC simultaneously; shared controls satisfy all three |
| **Control Library** | Reference Controls | Centralized control catalog; one control can satisfy requirements across multiple frameworks |
| **Gap Analysis** | Compliance Assessment results | Dashboard shows compliant / partially compliant / non-compliant per requirement; filter by status |
| **Statement of Applicability (SoA)** | Requirement Assessment module | Per-requirement applicability decisions with justification text; exportable |
| **Control Testing** | Requirement Assessments | Record test results, findings, and remediation for each control |
| **Audit Preparation** | Evidence module + Reports | Collect and organize evidence; generate audit-ready PDF compliance reports |
| **Remediation Tracking** | Applied Controls + observations | Track open findings; assign owners; set due dates; monitor progress |
| **Compliance Scoring** | Dashboard aggregations | Real-time compliance percentage per framework; trend tracking |

### 3.3 Evidence Management

| GRC Use Case | Platform Feature | How It Works |
|-------------|-----------------|-------------|
| **Evidence Collection** | Evidence module | Upload files or link URLs; server-side collection timestamp prevents backdating |
| **Evidence Expiry** | Retention policy | Set expiry dates per evidence item; automated alerts when evidence approaches expiry |
| **Evidence Versioning** | EvidenceRevision | Full version history of evidence artifacts; immutable historical record |
| **Evidence Linking** | Requirement → Evidence | Link evidence to specific compliance requirements; auditor can trace requirement → evidence directly |
| **File Storage** | Local or S3 | Evidence files stored locally or in S3-compatible object storage |
| **Audit Trail on Evidence** | django-auditlog | Every upload, edit, and deletion is logged with user and timestamp |

### 3.4 Third-Party Risk Management (TPRM)

| GRC Use Case | Platform Feature | How It Works |
|-------------|-----------------|-------------|
| **Vendor Register** | Entities module | Maintain registry of vendors, suppliers, partners |
| **Vendor Risk Assessments** | Entity Assessments | Conduct structured risk assessments against vendors; score and track results |
| **Vendor Contracts** | Contracts module | Record contract details, coverage dates, responsible parties |
| **Vendor Due Diligence** | Due Diligence library | Built-in vendor due diligence questionnaire framework (loadable library) |
| **CISA SCRM** | CISA SCRM library | US government supply chain risk management template, loadable and assessable |
| **Vendor Contacts** | Representatives | Track named vendor contacts and their roles |

### 3.5 Privacy / GDPR Management

| GRC Use Case | Platform Feature | How It Works |
|-------------|-----------------|-------------|
| **Processing Register (ROPA)** | Privacy → Processings | Record all personal data processing activities; lawful basis; retention periods |
| **Data Subject Rights** | Right Requests module | Track DSARs, deletion requests, portability requests; manage response deadlines |
| **Data Breach Management** | Data Breaches module | Log breaches; track notification timelines (72-hour GDPR clock); regulatory reporting |
| **Data Recipient Mapping** | Data Recipients | Document who receives personal data and under what basis |
| **Personal Data Inventory** | Personal Data module | Catalog data types and classify sensitivity |

### 3.6 Business Continuity (BCM)

| GRC Use Case | Platform Feature | How It Works |
|-------------|-----------------|-------------|
| **Business Impact Analysis** | Resilience → BIA Assessments | Structured BIA with asset assessments and escalation thresholds |
| **BCM Framework** | ISO 22301 library | Loadable ISO 22301:2019 business continuity framework |
| **Asset Resilience Assessment** | Asset Assessments | Assess asset criticality and recovery requirements per BIA |

### 3.7 Reporting & Dashboards

| GRC Use Case | Platform Feature | Output |
|-------------|-----------------|--------|
| **Compliance Dashboard** | Main dashboard | Per-framework compliance score; open findings; expiring evidence alerts |
| **Risk Dashboard** | Risk assessment views | Risk matrix heat map; scenario list by severity |
| **Audit-Ready Reports** | PDF report generation | WeasyPrint-generated PDF compliance reports per framework |
| **Data Export** | CSV/Excel export | Export assessments, controls, and evidence lists |
| **API Access** | REST API (OpenAPI 3.0) | Programmatic data access for integration with BI tools |
| **Metrics / KPIs** | Metrology module | Track KPIs over time; historical compliance trends |

### 3.8 Governance & Access Control

| GRC Use Case | Platform Feature | How It Works |
|-------------|-----------------|-------------|
| **Organizational Hierarchy** | Folder system | Model org units as nested folders; permissions scoped per folder |
| **Role-Based Access** | RBAC module | Assign roles (Viewer, Analyst, Manager, CISO, Admin) per folder |
| **SSO / IdP Integration** | SAML 2.0 / OIDC | Federate with Azure AD, Okta, Keycloak, and other enterprise IdPs |
| **MFA** | TOTP + FIDO2 | Authenticator apps and hardware keys (YubiKey) supported |
| **Audit Trail** | django-auditlog | Every action by every user is logged; exportable |
| **Approval Workflows** | Validation Flows | Multi-step approval for risk acceptance, SoA sign-off, assessment publication |
| **Calendar / Deadlines** | Calendar module | Assessment due dates, evidence expiry, and reminders |

---

## 4. User Journey Maps

### 4.1 Journey: New Compliance Assessment (ISO 27001)

```
[CISO / Compliance Manager]
    │
    ▼
1. Load ISO 27001:2022 library → framework appears in Libraries
    │
    ▼
2. Create Compliance Assessment → select scope (e.g., "ISMS for Business Unit A")
    │
    ▼
3. Assign to Analyst → analyst receives notification
    │
    ▼
4. [Analyst] Reviews each RequirementNode → sets status:
   ✅ Compliant / ⚠️ Partial / ❌ Non-compliant / N/A
   Adds finding notes; links existing AppliedControls
    │
    ▼
5. [Analyst] Uploads evidence → evidence linked to requirements
    │
    ▼
6. Assessment submitted for review → Validation Flow triggered
    │
    ▼
7. [Manager] Reviews → approves or returns with comments
    │
    ▼
8. [CISO] Final approval → Assessment status = "Published"
    │
    ▼
9. Generate PDF compliance report → download or email to auditor
    │
    ▼
10. Schedule next review → Calendar entry created; reminder set
```

**Time to complete (first time, 200 controls):** 2–4 days for a trained analyst  
**Repeat assessments (reusing prior mappings):** 50–70% faster  

### 4.2 Journey: Risk Assessment (Qualitative)

```
[Risk Manager]
    │
    ▼
1. Create Risk Assessment → select risk matrix (e.g., 5x5)
    │
    ▼
2. Add risk scenarios:
   - Asset: "Customer Database"
   - Threat: "Data Breach via SQL Injection"
   - Likelihood: 3/5 | Impact: 5/5 → Inherent Risk: Critical
    │
    ▼
3. Link mitigating Applied Controls → Residual Risk recalculated
    │
    ▼
4. Set treatment plan: Reduce / Transfer / Accept / Avoid
    │
    ▼
5. Risk acceptance (if applicable) → Validation Flow → Manager approval
    │
    ▼
6. Risk Dashboard updated → heat map shows current posture
```

### 4.3 Journey: Evidence Expiry Management

```
[Automated Background Task — Huey worker]
    │
    ▼
Daily check: Evidence items approaching expiry (configurable window)
    │
    ▼
[Email notification → assigned owner]
    ▼
[Owner] Reviews expired evidence → uploads new version or extends
    │
    ▼
New EvidenceRevision created → compliance requirement re-linked
    │
    ▼
Dashboard alert cleared
```

### 4.4 Journey: Vendor Risk Assessment

```
[Procurement / Third-Party Risk Team]
    │
    ▼
1. Create Entity (vendor) → complete vendor profile
    │
    ▼
2. Load CISA SCRM or Vendor Due Diligence library
    │
    ▼
3. Launch Entity Assessment → questionnaire assigned to vendor contact
    │
    ▼
4. Vendor completes questionnaire via Third-Party Portal
   (separate route group — no internal system access)
    │
    ▼
5. Internal review → score calculated → risk rating assigned
    │
    ▼
6. Link to contracts → track renewal dates
    │
    ▼
7. Ongoing monitoring → periodic re-assessment scheduled
```

---

## 5. Competitor Comparison

| Capability | **Sanadcom** | ServiceNow GRC | Archer IRM | Vanta | Drata | OneTrust |
|-----------|-------------|---------------|-----------|-------|-------|---------|
| **Frameworks supported** | 108+ (open library) | 50+ (licensed) | 60+ (licensed) | 10–15 (audit-focused) | 10–15 | 30+ |
| **Custom frameworks** | ✅ YAML-based | ⚠️ Complex | ⚠️ Complex | ❌ | ❌ | ⚠️ Limited |
| **Cross-framework control reuse** | ✅ Native decoupling | ⚠️ Partial | ⚠️ Partial | ❌ | ❌ | ⚠️ |
| **Risk assessment (qualitative)** | ✅ Full | ✅ Full | ✅ Full | ⚠️ Basic | ⚠️ Basic | ✅ |
| **EBIOS RM methodology** | ✅ Full | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Quantitative risk (CRQ/FAIR)** | ✅ Module | ⚠️ Add-on | ✅ | ❌ | ❌ | ❌ |
| **GDPR/Privacy module** | ✅ Full ROPA | ✅ | ✅ | ⚠️ | ⚠️ | ✅ (dedicated) |
| **TPRM** | ✅ Full | ✅ Full | ✅ Full | ⚠️ | ⚠️ | ✅ |
| **Business Continuity (BCM)** | ✅ BIA module | ✅ | ✅ | ❌ | ❌ | ⚠️ |
| **Evidence management** | ✅ Versioned + expiry | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Arabic RTL support** | ✅ Full | ⚠️ Partial | ❌ | ❌ | ❌ | ⚠️ |
| **Saudi ECC / SAMA** | ✅ Native | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Open source / Self-hostable** | ✅ AGPL Community | ❌ SaaS | ❌ SaaS | ❌ SaaS | ❌ SaaS | ❌ SaaS |
| **API-first** | ✅ OpenAPI 3.0 | ✅ | ✅ | ⚠️ | ⚠️ | ✅ |
| **CLI tooling** | ✅ CLICA + MCP | ❌ | ❌ | ❌ | ❌ | ❌ |
| **SSO (SAML/OIDC)** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **MFA (TOTP + FIDO2)** | ✅ | ✅ | ⚠️ | ✅ | ✅ | ✅ |
| **Audit log** | ✅ Full model-level | ✅ | ✅ | ⚠️ | ⚠️ | ✅ |
| **Workflow automation** | ✅ Prefect/n8n/Kafka | ✅ | ✅ | ❌ | ❌ | ⚠️ |
| **Kubernetes / Helm deployment** | ✅ | ❌ (SaaS) | ❌ (SaaS) | ❌ | ❌ | ❌ |
| **Pricing model** | Open core / Custom | Enterprise license | Enterprise license | Per-employee SaaS | Per-employee SaaS | Enterprise |

**Key differentiators for Sanadcom:**
1. **Widest framework library** including MENA-specific standards (Saudi ECC, SAMA, OTCC) not found in any major competitor.
2. **True control decoupling** — the only platform where one implemented control natively satisfies N framework requirements without manual remapping.
3. **Full EBIOS RM implementation** — unique in the market outside French government tools.
4. **Self-hostable** — organizations with data sovereignty requirements can run entirely on-premises.
5. **Arabic-first design** — built for bilingual operation, not bolted-on translation.

---

## 6. Integration Ecosystem

| Integration | Status | Use Case |
|-------------|--------|---------|
| **Jira** | ✅ Live | Findings → Jira tickets; two-way status sync |
| **Kafka** | ✅ Live | Ingest compliance signals from Prowler, cloud scanners |
| **Webhooks** | ✅ Live | Push events to any HTTP endpoint (Slack, Teams, custom) |
| **Prefect** | 🔶 Partial | Workflow automation for scheduled compliance tasks |
| **n8n** | 🔶 Partial | No-code workflow automation |
| **CLI (CLICA)** | ✅ Live | Bulk import/export; scripted operations |
| **MCP / LLM** | ✅ Live | AI assistant integration for GRC queries |
| **SAML 2.0 IdPs** | ✅ Live | Azure AD, Okta, Keycloak, Ping |
| **OIDC IdPs** | ✅ Live | Google, Azure, Auth0 |
| **S3 Storage** | ✅ Live | Evidence file storage in AWS S3 or compatible |
| **Prometheus** | ✅ Live | Application metrics for Grafana dashboards |
| **SIEM** | ❌ Roadmap | Splunk, Microsoft Sentinel, Elastic SIEM |
| **ServiceNow** | ❌ Roadmap | Ticket creation and sync |
| **LDAP/AD Sync** | ❌ Roadmap | Automated user provisioning |

---

## 7. Evaluation Checklist for Practitioners

Use this checklist when evaluating the platform against your organization's needs:

### Must-Have Capabilities
- [ ] Multi-framework compliance tracking in one place
- [ ] Risk register with heat map visualization
- [ ] Evidence collection with expiry management
- [ ] Audit trail and non-repudiation for all actions
- [ ] Role-based access with organizational hierarchy
- [ ] PDF/export reporting for auditors and management
- [ ] Arabic RTL UI and bilingual reporting (if applicable)
- [ ] Saudi ECC / SAMA framework support (if applicable)

### Nice-to-Have Capabilities
- [ ] EBIOS RM risk methodology
- [ ] Privacy/GDPR processing register
- [ ] Third-party vendor assessments
- [ ] Business continuity (BIA)
- [ ] Quantitative risk (FAIR-style)
- [ ] LLM/AI assistant integration
- [ ] Kafka/automation integration

### Integration Requirements
- [ ] SSO with existing IdP
- [ ] Ticketing system integration (Jira/ServiceNow)
- [ ] SIEM correlation
- [ ] API access for BI tools

---

*Document prepared by Sanadcom Product Team — May 2026*  
*All information is confidential and shared under NDA.*
