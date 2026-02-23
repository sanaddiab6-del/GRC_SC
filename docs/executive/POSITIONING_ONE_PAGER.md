# 🛡️ SICO GRC Platform - Executive Positioning

## Problem

**Current State: Saudi Organizations Face Critical GRC Challenges**

Saudi organizations managing **ECC (Essential Cybersecurity Controls)**, **CCC (Cloud Cybersecurity Controls)**, and **PDPL (Personal Data Protection Law)** compliance face:

1. **Manual Evidence Collection Crisis**
   - 114 ECC controls + 175 CCC controls = 289 controls requiring continuous evidence
   - Average 6-8 hours per control for evidence gathering
   - 1,734+ annual hours for a single framework audit
   - Manual processes cause 40-60% audit delays

2. **Multi-Framework Overlap Burden**
   - 78% overlap between ECC and CCC controls causes duplicate effort
   - No unified control library = redundant policies, redundant evidence, redundant testing
   - Consultants charge SAR 800-1,200/hour to manually map frameworks

3. **SOC-GRC Disconnection**
   - Security incidents (SIEM/SOC) don't auto-map to control violations
   - Compliance teams discover incidents weeks late via manual review
   - No automated risk scoring from security events

4. **Bilingual Documentation Overhead**
   - NCA requires Arabic + English documentation
   - Manual translation costs SAR 0.50-1.50 per word
   - Consistency errors between Arabic/English versions

5. **AI Adoption Without Compliance**
   - Organizations deploying AI/ML without SDAIA AI governance frameworks
   - No audit trail for model decisions
   - Bias testing and ethical AI compliance ignored

---

## Decision

**Build vs. Buy: Strategic Platform Selection**

After evaluating **CISO Assistant (Community)**, **eramba**, and **Enterprise GRC platforms** (OpenPages, ServiceNow, Archer, MetricStream), we selected a **three-tier strategy**:

### ✅ Tier 1: Internal Operations (CISO Assistant Community Edition)
- **Use Case**: Zain internal GRC operations
- **Rationale**: 
  - Open-source, Saudi data residency compliant
  - Extendable for ECC/CCC/PDPL packs
  - Zero licensing cost for internal deployment
  - Full control over data and customization

### ✅ Tier 2: SMB & Mid-Market (SICO Packs on eramba/CISO Assistant)
- **Use Case**: Saudi SMBs and regulated mid-market clients
- **Rationale**:
  - Pre-packaged compliance accelerators (SICO Packs)
  - 70% faster deployment vs. building from scratch
  - SAR 150K-300K total cost (vs. SAR 800K+ for Archer)

### ✅ Tier 3: Enterprise Clients (Consult + Integrate)
- **Use Case**: Banks, telecom, government entities with existing GRC platforms
- **Rationale**:
  - Most enterprises already committed to OpenPages/ServiceNow/Archer
  - Sell **SICO Packs** (ECC/CCC/PDPL control libraries) as data imports
  - Sell **SOC-GRC Bridge** as integration middleware
  - Sell **AI/RAG** as bilingual compliance assistant

---

## 90-Day Outputs

### Month 1: Foundation (Weeks 1-4)

#### Week 1-2: Core Platform + Security Baseline
**Deliverables:**
- ✅ RBAC/ABAC authentication + authorization (OAuth2/Azure AD)
- ✅ TLS/HTTPS enforcement + field-level encryption (AES-256)
- ✅ Structured audit logging (7-year retention per NCA)
- ✅ Input validation + rate limiting (brute force protection)
- ✅ Secrets management (Azure Key Vault integration)

**KPIs:**
- Authentication uptime: 99.9%
- Audit log completeness: 100% of API calls
- Failed login lockout: <5 attempts

#### Week 3-4: Control Library Foundation
**Deliverables:**
- ✅ ECC baseline controls (114 controls) ingested
- ✅ CCC cloud controls (175 controls) ingested
- ✅ PDPL privacy controls (29 articles) ingested
- ✅ ECC↔CCC mapping engine (identify 78% overlap)
- ✅ Evidence catalog (400+ evidence templates)

**KPIs:**
- Control coverage: 100% of NCA frameworks
- Mapping accuracy: 95%+ validated by compliance officers
- Evidence template completeness: 80% of controls linked

---

### Month 2: Integration + Automation (Weeks 5-8)

#### Week 5-6: SOC-GRC Bridge MVP
**Deliverables:**
- ✅ SIEM incident ingestion (Splunk, QRadar, Sentinel connectors)
- ✅ Automated incident-to-control mapping (MITRE ATT&CK → ECC controls)
- ✅ Risk scoring engine (severity + control weakness → risk rating)
- ✅ Automated ticket creation in GRC for control violations

**KPIs:**
- Mean Time to Alert (MTTA): <15 minutes from SIEM event
- Mapping accuracy: 85%+ incidents correctly mapped to controls
- False positive rate: <10%

#### Week 7-8: Reporting Engine
**Deliverables:**
- ✅ Executive dashboard (compliance status, risk heatmap, audit readiness)
- ✅ Control compliance reports (by framework: ECC/CCC/PDPL)
- ✅ Evidence overdue alerts (automatically track collection deadlines)
- ✅ Audit readiness scorecard (0-100 scale)

**KPIs:**
- Report generation time: <30 seconds for full compliance report
- Dashboard refresh rate: Real-time (WebSocket updates)
- Evidence overdue detection: 100% accuracy

---

### Month 3: AI Enhancement + Delivery Readiness (Weeks 9-12)

#### Week 9-10: AI/RAG Bilingual Compliance Assistant
**Deliverables:**
- ✅ `POST /api/v1/rag/query` endpoint (Arabic + English queries)
- ✅ Mandatory citation tracking (doc_id + section + chunk_id)
- ✅ Refusal policy: No answer without source document
- ✅ RBAC-aware retrieval (only return documents user has access to)
- ✅ Prompt injection defense (unit tests + guardrails)

**KPIs:**
- Citation rate: 100% of answers include source reference
- Query response time: <3 seconds (p95)
- Retrieval precision: 90%+ (relevant documents retrieved)
- Refusal rate: <5% for valid queries (avoid over-blocking)

#### Week 11-12: Delivery Factory + Documentation
**Deliverables:**
- ✅ Onboarding playbook (client setup in 2 days)
- ✅ Evidence collection workshop templates
- ✅ QA checklists for deployment validation
- ✅ Training materials (Arabic + English)
- ✅ SICO Packs packaging (ECC baseline, CCC cloud, PDPL privacy)

**KPIs:**
- Time to first evidence collected: <4 hours post-deployment
- Client onboarding duration: <3 days (vs. 2-4 weeks industry standard)
- Training completion rate: 90% of client users

---

## Risks & Mitigation

### Risk 1: Operational Deployment Complexity
**Risk:** Docker/Kubernetes deployment failures in client environments (firewall, network policies, skill gaps)

**Mitigation:**
- ✅ Provide Docker Compose for simple deployments (single-node)
- ✅ Include troubleshooting playbook in `docs/deployment/`
- ✅ Offer managed cloud deployment option (Azure Saudi region)
- ✅ 24/7 deployment support during first 90 days

**Fallback:** Pre-configured VM images (OVA/QCOW2) for air-gapped environments

---

### Risk 2: AGPL Licensing Constraints (CISO Assistant)
**Risk:** CISO Assistant Community uses AGPL, requiring source disclosure if modified and distributed

**Mitigation:**
- ✅ Use CISO Assistant as-is for internal Zain operations (no distribution = no AGPL trigger)
- ✅ Build **SICO Packs** as data files (YAML/JSON) under proprietary license (not code modifications)
- ✅ SOC-GRC Bridge and AI/RAG as separate microservices (MIT/Apache licensed)
- ✅ Enterprise clients: Sell SICO Packs as imports, not modified CISO Assistant

**Legal Review:** Engage legal counsel to confirm licensing strategy (completed in Week 1)

---

### Risk 3: Integration with Legacy GRC Systems
**Risk:** Enterprise clients (OpenPages, ServiceNow) have complex APIs; integration may take >90 days

**Mitigation:**
- ✅ Focus 90-day plan on **SICO Packs export** (YAML/JSON) for manual import
- ✅ API integrations as Phase 2 (beyond 90 days)
- ✅ Provide import scripts for common formats (CSV, Excel, REST API examples)
- ✅ Partner with GRC platform vendors for certified integrations

**Success Criteria:** 80% of controls importable via standard CSV upload

---

### Risk 4: Data Quality & Arabic Translation Accuracy
**Risk:** Control descriptions, evidence templates may have translation errors or inconsistencies

**Mitigation:**
- ✅ Engage certified Arabic translators (native Saudi) for NCA content
- ✅ Implement QA review: Native Arabic speaker + cybersecurity expert dual review
- ✅ Use AI-assisted translation (GPT-4 + human validation) for faster throughput
- ✅ Maintain glossary of Arabic cybersecurity terms (consistency enforcement)

**KPI:** Translation accuracy >98% (measured by compliance officer feedback)

---

### Risk 5: AI Hallucination & Compliance Liability
**Risk:** RAG system provides incorrect compliance guidance, causing audit failures

**Mitigation:**
- ✅ **Mandatory citations:** Every AI answer includes source control ID
- ✅ **Refusal policy:** If no confident source found, RAG refuses to answer
- ✅ **Human-in-the-loop:** AI responses labeled "AI-Generated - Validate with Compliance Officer"
- ✅ **Audit trail:** Log every RAG query + retrieved docs + generated answer
- ✅ **Prompt guardrails:** Block queries attempting to override policies

**Legal Disclaimer:** Include Terms of Use: "AI assistant is advisory only; consult compliance professionals for final decisions"

---

## Pricing per Pack

### SICO Pack 1: ECC Baseline (Essential Cybersecurity)
**Target:** Organizations needing NCA ECC compliance (all sectors)

**Includes:**
- 114 ECC controls (Arabic + English)
- 280+ evidence templates
- Audit test procedures for all controls
- Executive compliance dashboard

**Pricing:**
- **One-time license:** SAR 120,000
- **Annual support:** SAR 24,000 (20% of license)
- **Deployment services:** SAR 30,000-50,000 (optional)

**ROI Justification:**
- Replaces 1,200+ hours of manual control development (SAR 800/hour consultant rate = SAR 960K)
- Saves SAR 840K vs. building from scratch

---

### SICO Pack 2: CCC Cloud (Cloud Cybersecurity)
**Target:** Cloud service providers, SaaS vendors, cloud-heavy organizations

**Includes:**
- 175 CCC controls (Arabic + English)
- Cloud-specific evidence templates (AWS/Azure audit logs, config snapshots)
- CCC↔ECC unified baseline (eliminate 78% duplication)
- Cloud security posture dashboard

**Pricing:**
- **One-time license:** SAR 150,000
- **Annual support:** SAR 30,000
- **Deployment services:** SAR 40,000-60,000 (optional)

**Bundle Discount:** ECC + CCC = SAR 240,000 (save SAR 30K vs. individual purchase)

**ROI Justification:**
- Avoids duplicate evidence collection for overlapping controls (saves 600+ hours/year)
- Pre-mapped to AWS/Azure security controls (saves 200 hours of mapping work)

---

### SICO Pack 3: PDPL Privacy (Personal Data Protection)
**Target:** Organizations processing personal data (e-commerce, healthcare, fintech)

**Includes:**
- 29 PDPL articles mapped to operational controls
- Privacy registers (RoPA, DSAR, Breach Notification, Consent Management)
- Data flow mapping templates
- Subject rights management workflows

**Pricing:**
- **One-time license:** SAR 100,000
- **Annual support:** SAR 20,000
- **Deployment services:** SAR 25,000-40,000 (optional)

**ROI Justification:**
- PDPL fines up to SAR 3M or 5% revenue - compliance is mandatory
- Replaces 800+ hours of manual privacy control development

---

### Add-On 1: SOC-GRC Bridge
**Target:** Organizations with active SOC/SIEM (Splunk, QRadar, Sentinel)

**Includes:**
- SIEM incident ingestion (pre-built connectors)
- Automated incident-to-control mapping (MITRE ATT&CK → ECC/CCC)
- Risk scoring engine
- Automated GRC ticket creation

**Pricing:**
- **One-time license:** SAR 80,000
- **Annual support:** SAR 16,000
- **Integration services:** SAR 20,000-35,000 (per SIEM platform)

**ROI Justification:**
- Reduces Mean Time to Respond (MTTR) by 60% (auto-map incidents to compliance gaps)
- Saves 40+ hours/month of manual SOC-GRC reconciliation (SAR 25K/month value)

---

### Add-On 2: AI Bilingual Compliance Assistant
**Target:** Organizations needing bilingual compliance guidance (Arabic + English)

**Includes:**
- RAG-powered Q&A (citation-backed answers)
- Bilingual knowledge base (NCA regulations, ISO standards)
- Client-specific dictionary engine (custom terminology)
- Audit-grade logging (query + source tracking)

**Pricing:**
- **One-time license:** SAR 60,000
- **Annual support:** SAR 12,000
- **Custom BERT adapter (Premium):** SAR 40,000 per client (optional)

**ROI Justification:**
- Replaces 20+ hours/week of manual compliance research (SAR 40K/month value)
- Instant bilingual answers vs. waiting for consultant responses

---

### Enterprise Bundle (Full Stack)
**Includes:** ECC + CCC + PDPL + SOC Bridge + AI Assistant

**Pricing:**
- **One-time license:** SAR 450,000 (save SAR 60K vs. individual purchase)
- **Annual support:** SAR 90,000 (20%)
- **Full deployment + training:** SAR 100,000-150,000

**Total First-Year Cost:** SAR 550,000-600,000

**Enterprise ROI:**
- Replaces SAR 2M+ in consultant fees (manual control development, evidence collection, audit prep)
- Reduces audit preparation time from 6 months to 6 weeks
- Continuous compliance monitoring (vs. annual audit scramble)

---

## What We Will NOT Do in 90 Days (Out of Scope)

### ❌ Not in Scope - Phase 1 (90 Days)

1. **Advanced AI Features**
   - ❌ Per-client BERT fine-tuning (requires 3-6 months data collection per client)
   - ❌ Automated policy generation from controls (Phase 2)
   - ❌ Predictive compliance risk scoring (Phase 3)

2. **Enterprise GRC Platform Integrations**
   - ❌ Native API integrations with ServiceNow, Archer, OpenPages (Phase 2-3)
   - ✅ **Instead:** Provide export formats (CSV, JSON, REST API) for manual/scripted import

3. **Mobile Applications**
   - ❌ iOS/Android native apps (Phase 3)
   - ✅ **Instead:** Responsive web interface works on mobile browsers

4. **On-Premise Hardware Appliances**
   - ❌ Physical appliances with pre-installed software
   - ✅ **Instead:** Docker/VM images for on-prem deployment

5. **Multi-Tenancy SaaS Platform**
   - ❌ Public SaaS offering (requires 6+ months of hardening, pen testing, certification)
   - ✅ **Instead:** Single-tenant deployments (per client)

6. **Real-Time SIEM Log Analysis**
   - ❌ Replace SIEM functionality (not our core competency)
   - ✅ **Instead:** Integrate with existing SIEM, map incidents to GRC

7. **Regulatory Change Monitoring Service**
   - ❌ Automated scraping of NCA/SAMA/CITC websites for regulation updates
   - ✅ **Instead:** Quarterly manual updates to control library

---

## Evidence-Based Assurance

**How We Prove Our Claims: CI/CD Artifacts + Transparency**

To build trust with clients and auditors, we commit to **verifiable, evidence-based claims** for all platform capabilities:

### 1. Security Claims → SARIF Reports
**Claim:** "Platform passes SAST, dependency scanning, and secret detection"

**Evidence:**
- ✅ CodeQL SARIF reports (uploaded to GitHub Security tab)
- ✅ Bandit SARIF reports (Python SAST)
- ✅ Gitleaks secret scan reports
- ✅ npm audit + Safety dependency reports

**Access:** All reports downloadable from GitHub Actions artifacts (public or client-shared)

---

### 2. Supply Chain Security → SBOM (Software Bill of Materials)
**Claim:** "Zero critical vulnerabilities in dependencies"

**Evidence:**
- ✅ CycloneDX SBOM (JSON format) for Python + Node.js
- ✅ Automated vulnerability scanning of SBOM (Grype, Trivy)
- ✅ SBOM versioning (track dependency changes over time)

**Access:** SBOM published with every release (GitHub Releases page)

---

### 3. Compliance Coverage → Control Library JSON Export
**Claim:** "100% coverage of ECC/CCC/PDPL controls"

**Evidence:**
- ✅ Machine-readable control library (JSON/YAML)
- ✅ Each control includes: ID, description (AR/EN), evidence types, audit procedures
- ✅ Mapping files (ECC↔CCC) with traceability

**Access:** Public GitHub repository (`data/controls/`, `data/mappings/`)

---

### 4. AI Accuracy → Citation Validation Reports
**Claim:** "100% of AI answers include verifiable citations"

**Evidence:**
- ✅ RAG query logs (anonymized): query → retrieved docs → generated answer
- ✅ Citation validation tests (automated test suite)
- ✅ Monthly accuracy reports (% of answers with valid citations)

**Access:** Test results in GitHub Actions + monthly reports to clients

---

### 5. Performance → Load Testing Reports
**Claim:** "API responds in <3 seconds (p95) under 100 concurrent users"

**Evidence:**
- ✅ Locust/k6 load testing reports (RPS, latency, error rate)
- ✅ Grafana dashboards (real-time performance metrics)
- ✅ SLA monitoring (uptime, response time)

**Access:** Performance test results in GitHub Actions artifacts

---

### 6. Audit Logging → Log Samples + Retention Proof
**Claim:** "7-year audit log retention per NCA ECC-IS-4"

**Evidence:**
- ✅ Sample audit logs (sanitized) showing structure (JSON format)
- ✅ Retention policy documentation (automated archival to S3/Azure Blob)
- ✅ Log integrity verification (hash chaining for tamper detection)

**Access:** Sample logs in `docs/audit/`, retention policy in `docs/compliance/`

---

### 7. Deployment Success → Client Onboarding Metrics
**Claim:** "Clients onboarded in <3 days"

**Evidence:**
- ✅ Deployment playbook execution times (tracked per client)
- ✅ QA checklist completion rates
- ✅ Client satisfaction surveys (post-deployment)

**Access:** Aggregated metrics dashboard (internal), case studies (public)

---

## Success Metrics (90-Day Checkpoint)

### Technical Metrics
- [ ] **Security:** Zero High/Critical findings in SAST + dependency scans
- [ ] **Performance:** API p95 latency <3 seconds under 100 concurrent users
- [ ] **Uptime:** 99.9% availability (excluding planned maintenance)
- [ ] **Test Coverage:** >80% code coverage for backend + AI modules

### Business Metrics
- [ ] **Pilot Deployments:** 3-5 clients successfully deployed
- [ ] **Time to Value:** <3 days from contract to first evidence collected
- [ ] **Client Satisfaction:** NPS >50 (Net Promoter Score)
- [ ] **Revenue:** SAR 1M+ in signed contracts (licenses + services)

### Compliance Metrics
- [ ] **Control Coverage:** 100% of NCA ECC/CCC/PDPL controls implemented
- [ ] **Audit Readiness:** 90%+ controls with linked evidence templates
- [ ] **SOC Integration:** 85%+ incident-to-control mapping accuracy
- [ ] **AI Citation Rate:** 100% of RAG answers include valid source references

---

## Governance & Decision Authority

### Steering Committee
- **Executive Sponsor:** [VP Technology/CISO]
- **Product Owner:** [GRC Product Manager]
- **Engineering Lead:** [Principal Engineer]
- **Compliance Lead:** [Chief Compliance Officer]

### Decision Framework
- **Go/No-Go Gate:** End of Week 4 (Foundation complete)
- **Monthly Reviews:** Weeks 4, 8, 12 (executive steering committee)
- **Risk Escalation:** High risks escalated to sponsor within 24 hours

### Change Control
- **In-Scope Changes:** Approved by Product Owner (minor features, bug fixes)
- **Out-of-Scope Requests:** Require steering committee approval + timeline impact analysis

---

**Last Updated:** 2026-02-10  
**Version:** 1.0  
**Owner:** SICO GRC Platform Team
