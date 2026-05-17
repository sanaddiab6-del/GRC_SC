# Sanadcom GRC Platform — Academic & Standards Review Package

**Prepared for:** GRC Scholars, Compliance Researchers, Academic Reviewers  
**Prepared by:** Sanadcom Engineering & Compliance Team  
**Classification:** Confidential — Shared Under NDA  
**Date:** May 2026  
**Revision:** 1.0

---

## 1. Executive Summary

Sanadcom is an open-architecture, multi-framework GRC platform that implements **108+ international compliance standards** through a unified, decoupled control model. Built on the CISO Assistant community engine, the platform advances the academic discourse on GRC by operationalizing the theoretical separation between *compliance tracking* and *control implementation* — a distinction increasingly recognized in ISO, NIST, and ENISA guidance but rarely implemented in commercial tools.

This document presents:
- The complete framework library with standards lineage
- The methodology underpinning the compliance model
- Design decisions referenced to published standards
- Areas open for scholarly critique and improvement

---

## 2. Supported Compliance Frameworks

### 2.1 Framework Library — Complete Mapping

The platform loads frameworks via a **YAML-based library system** (`StoredLibrary → LoadedLibrary → Framework`). Each framework is versioned, attributed, and internationally standardized.

#### International / Global Standards

| # | Framework | Version | Domain | Geographic Scope |
|---|-----------|---------|--------|-----------------|
| 1 | ISO/IEC 27001 | 2022 + 2013 (legacy) | Information Security Management | Global |
| 2 | ISO/IEC 42001 | 2023 | AI Management System | Global |
| 3 | ISO 22301 | 2019 | Business Continuity Management | Global |
| 4 | NIST Cybersecurity Framework | v1.1 + v2.0 | Cyber Risk Management | Global (US-origin) |
| 5 | NIST SP 800-53 | Rev 5 | Security & Privacy Controls | US Federal / Global |
| 6 | NIST SP 800-171 | Rev 2 (2021) + Rev 3 (2024) | CUI Protection | US Federal Supply Chain |
| 7 | NIST SP 800-218 (SSDF) | Current | Secure Software Development | Global |
| 8 | NIST AI RMF | Current | AI Risk Management | Global |
| 9 | NIST Privacy Framework | Current | Privacy Risk Management | Global |
| 10 | NIST SP 800-66 (HIPAA) | Current | Healthcare Privacy | US Healthcare |
| 11 | SOC 2 | TSC 2017 | Service Organization Controls | Global (AICPA) |
| 12 | PCI DSS | 4.0.1 | Payment Card Security | Global (PCI SSC) |
| 13 | CIS Controls | v8 | Cybersecurity Controls | Global |
| 14 | MITRE ATT&CK | v18.1 | Threat Catalog | Global |
| 15 | MITRE D3FEND | Current | Defensive Controls Reference | Global |
| 16 | OWASP ASVS | v4 + v5 | Application Security | Global |
| 17 | OWASP MASVS | Current | Mobile App Security | Global |
| 18 | OWASP Top 10 Web | Current | Web Threat Catalog | Global |
| 19 | OWASP LLM Governance | Current | AI/LLM Security | Global |
| 20 | CSA CCM | Current | Cloud Security | Global |
| 21 | Secure Controls Framework (SCF) | Current | Unified Controls | Global |
| 22 | Adobe CCF | v5 | Common Controls Framework | Global |
| 23 | Cisco CCF | v3.0 | Cloud Controls | Global |
| 24 | Google SAIF | Current | AI Security | Global |
| 25 | ITIL 4 Management Practices | Current | IT Service Management | Global |
| 26 | Vendor Due Diligence Baseline | intuitem | Third-Party Risk | Global |

#### European Union Frameworks

| # | Framework | Domain | Scope |
|---|-----------|--------|-------|
| 27 | NIS2 Directive | Network & Information Security | EU |
| 28 | NIS2 Technical Requirements (2024/2690) | NIS2 Implementation | EU |
| 29 | GDPR (Full Text + GDPR.EU Checklist) | Data Protection | EU |
| 30 | DORA (Act + RTS + ITS + GL) | Digital Operational Resilience (Finance) | EU |
| 31 | EU AI Act | Artificial Intelligence Regulation | EU |
| 32 | Cyber Resilience Act (CRA) | Product Cybersecurity | EU |
| 33 | TIBER-EU | Threat-Led Pen Testing (Finance) | EU |
| 34 | ENISA 5G Security Controls Matrix | 5G Infrastructure | EU |
| 35 | ECB Cyber Resilience Oversight | Financial Market Infrastructure | EU |
| 36 | European Sustainability Reporting Standards (ESRS) | ESG Reporting | EU |
| 37 | Cloud Sovereignty Framework | v1.2.1 | EU |
| 38 | NOREA DORA in Control Framework | v3.0 | EU (Netherlands) |

#### Saudi Arabia & MENA Region

| # | Framework | Domain | Scope |
|---|-----------|--------|-------|
| 39 | Essential Cybersecurity Controls (ECC) | National Cybersecurity | Saudi Arabia |
| 40 | SAMA Cybersecurity Framework | Financial Sector Security | Saudi Arabia |
| 41 | Operational Technology Cybersecurity Controls (OTCC) | OT/ICS Security | Saudi Arabia |

#### United Kingdom

| # | Framework | Domain |
|---|-----------|--------|
| 42 | NCSC Cyber Assessment Framework (CAF) | National Cyber Assessment |
| 43 | NCSC Cyber Essentials | SME Baseline Security |

#### North America

| # | Framework | Domain | Jurisdiction |
|---|-----------|--------|-------------|
| 44 | CMMC v2 | Defense Supply Chain | US DoD |
| 45 | NYDFS 500 (2023 Amendment) | Financial Cybersecurity | US/NY |
| 46 | GSA FedRAMP | Cloud for Federal Agencies | US Federal |
| 47 | FBI CJIS | Criminal Justice Information | US Federal |
| 48 | CCPA + CCPA Regulations | Consumer Privacy | US/CA |
| 49 | FTC Safeguarding Customer Information | Financial Privacy | US Federal |
| 50 | ITAR | Defense Export Controls | US Federal |
| 51 | CISA CPG | v2.0 | US |
| 52 | CISA SCRM Template | Supply Chain Risk | US Federal |
| 53 | ITSP.10.171 | Government Info Protection | Canada |

#### Other National Frameworks

| # | Framework | Country |
|---|-----------|---------|
| 54 | PSPF (Protective Security Policy Framework) | Australia |
| 55 | Essential Eight | Australia |
| 56 | APRA CPS 230 (Operational Risk) | Australia |
| 57 | APRA CPS 234 (Information Security) | Australia |
| 58 | TISAX (VDA ISA) | v5.1 + v6.0 | Germany/Auto industry |
| 59 | BSI IT-Grundschutz Kompendium | Germany |
| 60 | BSI C5 (Cloud Compliance Criteria Catalogue) | Germany |
| 61 | BSI Minimum Standard for External Cloud | Germany |
| 62 | FADP (Federal Act on Data Protection) | Switzerland |
| 63 | Swiss ICT Minimum Standard | Switzerland |
| 64 | FINMA Circular 2023/01 | Switzerland |
| 65 | ENS (Esquema Nacional de Seguridad) | Spain |
| 66 | Korea ISA ISMS-P | South Korea |
| 67 | DNSSI | Morocco |
| 68 | RNSI (Référentiel National SI) | Algeria |
| 69 | E-ITS | Estonia |
| 70 | BIO2 (Baseline Informatiebeveiliging Overheid) | Netherlands |
| 71 | De tekniske minimumskrav for statslige myndigheder | Denmark |
| 72 | PSSIE du Bénin | Benin |
| 73 | India DPDPA 2023 | India |
| 74 | RBI Master Direction 2023 | India |
| 75 | Loi 05-20 Cybersécurité | Morocco |
| 76 | Misure minime ICT (AGID) | Italy |
| 77 | Framework Nazionale Cybersecurity v2 | Italy |
| 78 | NZISM (NZ Information Security Manual) | New Zealand |
| 79 | Lithuanian NIS2 Law | Lithuania |
| 80 | Swift CSCF | v2025 | Global (Finance) |
| 81 | RBI Master Direction 2023 | India |
| 82 | Post-Quantum Cryptography Migration | NIST/May 2025 | Global |

#### French National Frameworks (ANSSI)

| Framework | Domain |
|-----------|--------|
| LPM/OIV Rules | Critical Infrastructure |
| ANSSI Hygiene Guide | Baseline Security Hygiene |
| ANSSI SecNumCloud | Cloud Security Qualification |
| ANSSI AI Security Recommendations | Generative AI Systems |
| RGS v2.0 | Administrative Systems |
| 3CF v1 + v2 | Aviation Compliance |
| ANSSI AI Management Crisis Tool | Cyber Crisis Management |
| ANSSI AD Security Controls | Active Directory Hardening |
| ANSSI TLS Recommendations | Transport Layer Security |
| ANSSI IPSec Recommendations | Network Flow Protection |
| ANSSI SSH Recommendations | Secure Remote Access |
| ANSSI System Logging Architecture | Log Infrastructure |
| ANSSI Internet Interconnection | Network Security |
| ANSSI Cryptographic Mechanisms | Cryptography Guidance |
| ANSSI Sensitive SI Architectures | Classified Systems |
| ANSSI Secure System Administration | Admin Security |
| ANSSI MonAideCyber Questionnaire | SME Self-Assessment |
| PGSSI-S (Healthcare SI Security) | Healthcare |
| PDIS (Incident Detection Service Providers) | SOC Requirements |
| NIS-1 Transposition FR | Legacy NIS Implementation |
| PSSI État | French Government Security Policy |
| Checklist Dossier d'Homologation | Accreditation |
| HDS/HDH | Health Data Hosting |
| Cahier des charges Label EBIOS RM | Risk Methodology Certification |
| SecNumCloud v3.2 Annexe 2 | Cloud Commanditaires |
| DGA Maturité Fondamentale | DGA Maturity Assessment |
| CNIL Guide de Sécurité des Données | Data Security |
| IGI 1300 / II 901 | Classified SI Requirements |
| RGS 2.0 Annexe B2 | Security Reference Framework |
| CCB CyberFundamentals Physical Security | Physical + Video Protection |

#### Threat Catalogs (for Risk Assessment)

| Catalog | Source |
|---------|--------|
| MITRE ATT&CK v18.1 | MITRE Corporation |
| MITRE D3FEND | MITRE Corporation |
| OWASP Top 10 Web | OWASP Foundation |
| OWASP MAS Threat Modelling Guide | OWASP Foundation |

---

## 3. Compliance Methodology White Paper

### 3.1 The Decoupling Principle

**Core Thesis:** Compliance tracking and control implementation are conceptually distinct activities that most GRC tools incorrectly conflate. Sanadcom operationalizes their separation.

**Academic Foundation:**
- ISO/IEC 27001:2022 distinguishes between *requirements* (Annex A controls) and *implementation guidance* (ISO 27002). Sanadcom reifies this distinction as: `RequirementNode` (the standard's requirement) ↔ `AppliedControl` (the organization's implementation).
- NIST CSF v2.0's introduction of the *Govern* function (CSF 2.0 §2) recognizes that governance of cybersecurity programs differs from operational execution of controls. The platform models these as separate domain entities with distinct workflows.
- ENISA's 2023 guidelines on NIS2 implementation explicitly recommend decoupled control libraries to support cross-framework reuse — a design pattern built into the platform's `ReferenceControl` model.

**Implemented Model:**

```
Framework (Standard)
    └── RequirementNode (e.g., "ISO 27001 A.8.1 — Asset Management")
            └── RequirementAssessment (per-scope evaluation)
                    ├── Linked AppliedControls (organization's actual controls)
                    └── Evidence (artifacts proving control operation)
```

The `AppliedControl` can satisfy requirements across **multiple frameworks simultaneously**, enabling cross-framework mapping without duplicating control data.

### 3.2 Risk Assessment Methodologies Implemented

#### EBIOS Risk Manager (EBIOS RM — ANSSI, 2018)

Full implementation of the French national risk methodology, covering all five workshops:

| Workshop | Entity | Description |
|----------|--------|-------------|
| 1 — Scope & Security Baseline | `EbiosStudy`, `FearedEvent` | Scope definition, feared events, severity scoring |
| 2 — Risk Origins | `RoStakeholder`, `RiskOrigin` | Stakeholder and threat actor mapping |
| 3 — Strategic Scenarios | `StrategicScenario` | High-level attack paths |
| 4 — Operational Scenarios | `OperationalScenario`, `AttackPath` | Detailed kill chains |
| 5 — Risk Treatment | `SecurityMeasure`, treatment plans | Residual risk and controls |

**References:** ANSSI, *La méthode EBIOS Risk Manager*, version 1.5, 2023.

#### Quantitative Risk (CRQ Module)

- Probabilistic risk quantification (Monte Carlo-compatible input structure)
- Scenario-based loss estimation: `CrqStudy` → `CrqScenario` → `CrqHypothesis`
- Financial impact modeling aligned with FAIR (Factor Analysis of Information Risk) principles

**References:** Open FAIR Body of Knowledge, The Open Group, 2017.

#### Qualitative Risk Assessment (Core Module)

- Configurable risk matrices (3x3 to 5x5 scales)
- Probability × Impact scoring with custom severity thresholds
- Inherent vs. residual risk tracking with treatment plan linkage
- Risk acceptance workflow with validation flow gating

**References:** ISO 31000:2018, *Risk management — Guidelines*; NIST SP 800-30 Rev 1, *Guide for Conducting Risk Assessments*.

### 3.3 Evidence Model — Chain of Custody

The platform implements a custody-preserving evidence model:

```
Evidence (logical record)
    ├── EvidenceRevision (versioned file or URL)
    │       ├── uploaded_by (User, timestamped)
    │       ├── collected_at (server-side timestamp — client cannot forge)
    │       ├── expires_at (retention policy enforcement)
    │       └── file_hash (SHA-256 integrity check)
    └── Linked RequirementAssessments (showing which requirements this satisfies)
```

**Methodological Alignment:**
- ISO/IEC 27001:2022 Clause 9.1 requires documented evidence of monitoring and measurement.
- SOC 2 Type II requires time-bounded evidence samples across the examination period — supported via `collected_at` + `expires_at` range queries.
- GDPR Article 5(2) accountability principle requires provable data handling — evidenced via audit trail integration with `django-auditlog`.

### 3.4 Validation Workflow Model

Multi-step approval processes for high-stakes GRC decisions:

```
ValidationFlow
    ├── FlowEvent: "submitted" (by analyst)
    ├── FlowEvent: "reviewed" (by manager)
    └── FlowEvent: "approved" (by CISO) → triggers status change
```

**Alignment with standards:**
- ISO/IEC 27001:2022 Clause 6.1.3 requires documented Statement of Applicability with named approvers.
- DORA Article 5 requires ICT risk management approval by the management body.
- SOC 2 Change Management requires documented authorization for control changes.

### 3.5 Third-Party Risk Management (TPRM) Model

Implements a structured vendor assessment lifecycle:

```
Entity (vendor/supplier)
    └── EntityAssessment (periodic assessment)
            ├── Solutions (services/products provided)
            ├── Representatives (named contacts)
            └── Contracts (legal agreements)
```

**Alignment:**
- ISO/IEC 27001:2022 Annex A 5.19–5.22: Supplier relationships.
- NIST CSF v2.0 GV.SC (Supply Chain Risk Management).
- CISA SCRM Template — directly available as a loadable library.

---

## 4. Methodology Design Decisions — Citations

| Design Decision | Rationale | Standards Reference |
|----------------|-----------|-------------------|
| Framework library as YAML artifacts (not database-only) | Enables community contribution, versioning, and offline validation | Inspired by NIST's OSCAL (Open Security Controls Assessment Language) design philosophy |
| Decoupled `ReferenceControl` from `AppliedControl` | Allows one implementation to satisfy N frameworks | ISO 27001:2022 §6.1.3; ISO 27002:2022 §4 |
| Server-side timestamps on evidence | Prevents backdated evidence submissions | ISO/IEC 17000:2020 conformity assessment principles; SOC 2 examination standards |
| Folder-based multi-tenancy (not row-level security) | Maps to organizational hierarchy; simpler to reason about | NIST SP 800-53 AC-2 Account Management; GDPR Art. 25 data minimization |
| Audit log on every model change | Provides non-repudiable audit trail | ISO 27001:2022 A.8.15; DORA Art. 12; SOC 2 CC7.2 |
| Bilingual Arabic/English support | Operational requirement for MENA compliance reporting | Saudi NCA ECC §6; SAMA CSF documentation requirements |
| EBIOS RM as first-class methodology | French national methodology with growing EU adoption | ANSSI EBIOS RM v1.5; EU NIS2 risk assessment guidance (ENISA, 2023) |

---

## 5. Areas Open for Scholarly Review

We invite critique and engagement on the following open research questions embedded in the platform's design:

1. **Cross-Framework Control Mapping Completeness:** The platform allows one `AppliedControl` to satisfy requirements across multiple frameworks. The *degree* to which controls in different frameworks are semantically equivalent (versus superficially similar) is an active research problem. How should equivalence be formally defined and measured?

2. **Risk Aggregation Across Frameworks:** When the same organization runs a NIST CSF assessment and an ISO 27001 assessment simultaneously, how should risk scores be aggregated? The platform currently treats assessments independently.

3. **Quantitative vs. Qualitative Alignment:** The CRQ (quantitative) and core (qualitative) modules produce incommensurable outputs. Bridging FAIR-based financial loss estimates with qualitative risk matrices remains an unsolved methodology problem.

4. **Evidence Sufficiency Standards:** When is evidence "sufficient"? The platform tracks evidence existence but not sufficiency judgements. Formalizing a sufficiency model (perhaps borrowing from audit standards ISA 500) is a future direction.

5. **Automated Compliance Inference:** The Kafka dispatcher ingests signals from tools like Prowler (cloud posture). Mapping raw technical observations to compliance requirement satisfaction automatically — without human review — raises questions of audit defensibility.

---

## 6. Demo Walkthrough Reference Points

For platform demonstrations, the following workflows illustrate academic concepts:

| Concept | Where to See It |
|---------|----------------|
| Decoupling principle | Navigate: Compliance → Assessment → Requirement → Applied Controls |
| Cross-framework reuse | Load ISO 27001 + NIST CSF; observe shared `AppliedControl` entries |
| Evidence chain of custody | Evidence module → revision history → timestamp audit |
| Validation workflow | Risk Assessment → submit for review → approve flow |
| EBIOS RM methodology | EBIOS RM → Studies → Workshop walkthrough |
| Framework library system | Libraries → Browse → Load/Unload frameworks |
| Audit trail | Admin → Audit Logs → filter by object |

---

*Document prepared by Sanadcom Compliance Team — May 2026*  
*All information is confidential and shared under NDA.*
