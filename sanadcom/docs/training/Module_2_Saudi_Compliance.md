# Module 2: Saudi Regulatory Compliance
## 20-Minute Compliance Awareness Training

**Course Code**: TRAIN-COMP-001  
**Category**: Compliance (Mandatory)  
**Duration**: 20 minutes  
**Passing Score**: 80% (8/10 questions)  
**Recertification**: Annually

---

## Learning Objectives

1. Understand Saudi Arabia's key cybersecurity and data protection regulations
2. Recognize SICO's obligations under NCA ECC, PDPL, and SDAIA AI frameworks
3. Identify your role in maintaining regulatory compliance
4. Report potential compliance violations

---

## Section 1: National Cybersecurity Authority (NCA) (8 minutes)

### What is NCA?

**National Cybersecurity Authority** (الهيئة الوطنية للأمن السيبراني) is Saudi Arabia's regulatory body responsible for cybersecurity across all sectors.

**Established**: 2017 by Royal Decree  
**Mission**: Enhance cybersecurity posture, protect critical infrastructure, regulate cybersecurity practices

### Essential Cybersecurity Controls (ECC) v1.0

**Purpose**: Minimum cybersecurity baseline for all Saudi organizations

**When Applies**: Mandatory for:
- Government entities
- Critical infrastructure (energy, finance, telecom)
- Organizations handling sensitive data (like SICO)

**5 Domains - 114 Controls:**

1. **Cybersecurity Governance (18 controls)**
   - Establish ISMS framework
   - Information security policies
   - Risk management
   - Compliance monitoring
   - **Your Role**: Follow policies, participate in risk assessments, complete training

2. **Cybersecurity Defense (35 controls)**
   - Access control
   - Network security
   - Malware protection
   - Vulnerability management
   - **Your Role**: Use strong passwords+MFA, report suspicious activity, don't disable antivirus

3. **Cybersecurity Resilience (22 controls)**
   - Backup and recovery
   - Business continuity
   - Disaster recovery
   - **Your Role**: Follow backup procedures, test DR plans, know emergency contacts

4. **Third-Party Cybersecurity (12 controls)**
   - Vendor risk assessment
   - Supplier agreements
   - **Your Role**: Only work with approved vendors, report vendor security incidents

5. **Cybersecurity Incident Management (6 controls)**
   - Detection and response
   - Reporting to NCA (critical incidents within 72 hours)
   - **Your Role**: Report ALL incidents immediately (we handle NCA notification)

**Consequences of Non-Compliance:**
- Financial penalties up to SAR 2 million per violation
- Service suspension or license revocation
- Criminal prosecution for willful violations
- Reputational damage

### Cloud Cybersecurity Controls (CCC) v1.0

**Purpose**: Additional controls for cloud service providers and users

**Applies to**: SICO (we use Azure cloud) + our cloud-based GRC Platform

**183 Controls** across 10 domains:
- Identity and Access Management (IAM)
- Data Security and Encryption
- Cloud Infrastructure Security
- Incident Response and Security Events
- Compliance and Audit

**Key Requirements for SICO:**
- ✅ Data residency in Saudi Arabia (Azure Riyadh/Jeddah regions)
- ✅ Encryption in transit (TLS 1.3) and at rest (AES-256)
- ✅ Cloud service provider security certifications (Azure ISO 27001, SOC 2)
- ✅ Regular audit and compliance assessment

**Your Role:**
- Store SICO data only in approved cloud services (Azure, OneDrive, SharePoint)
- DON'T upload work data to personal cloud (Dropbox, Google Drive, iCloud)
- Report cloud security concerns (suspicious access, misconfigured permissions)

---

## Section 2: Personal Data Protection Law (PDPL) (7 minutes)

### What is PDPL?

**Personal Data Protection Law** (نظام حماية البيانات الشخصية) - Saudi Arabia's data privacy law, similar to EU's GDPR

**Effective**: September 2021  
**Regulatory Authority**: Saudi Data & AI Authority (SDAIA)

### What is Personal Data?

**Personal Data**: Any information relating to an identified or identifiable person

**Examples:**
- ✅ Name, national ID, phone number, email
- ✅ Location data, IP address
- ✅ Financial information, health records
- ✅ Photos, videos, voice recordings
- ✅ Online identifiers (username, device ID)

**Sensitive Personal Data** (extra protection required):
- Religious beliefs, political opinions
- Health/genetic data
- Biometric data (fingerprints, facial recognition)
- Criminal history
- Financial information

### PDPL Principles

1. **Lawfulness**: Process personal data only with legal basis (consent, contract, legal obligation)
2. **Purpose Limitation**: Collect for specific, explicit purposes only
3. **Data Minimization**: Collect only what's necessary
4. **Accuracy**: Keep personal data accurate and up to date
5. **Storage Limitation**: Retain only as long as needed
6. **Security**: Implement appropriate technical and organizational measures

### Your PDPL Responsibilities

**DO:**
- ✅ Obtain consent before collecting personal data from data subjects
- ✅ Process personal data only for authorized business purposes
- ✅ Protect personal data from unauthorized access (encryption, access controls)
- ✅ Report personal data breaches immediately (PDPL requires notification within 72 hours)
- ✅ Respect data subject rights (access, correction, deletion requests)

**DON'T:**
- ❌ Collect more personal data than necessary
- ❌ Use personal data for purposes other than originally specified
- ❌ Share personal data with unauthorized third parties
- ❌ Transfer personal data outside Saudi Arabia without proper safeguards
- ❌ Retain personal data longer than required (check retention policy)

### Data Subject Rights (DSAR)

Individuals have the right to:
1. **Access**: Request copy of their personal data
2. **Correction**: Fix inaccurate data
3. **Deletion**: "Right to be forgotten" (with exceptions)
4. **Objection**: Object to data processing
5. **Portability**: Receive data in machine-readable format

**Process at SICO:**
- Data subjects submit requests via privacy@sicocompany.sa
- DPO (Data Protection Officer) reviews within 5 business days
- Response provided within 30 days
- **Your Role**: Forward any DSAR to privacy@sicocompany.sa immediately

### Personal Data Breach Notification

**What is a Breach?**
Unauthorized access, loss, destruction, alteration, or disclosure of personal data

**Examples:**
- Lost unencrypted laptop with customer data
- Ransomware encrypting database with personal information
- Email sent to wrong recipient containing employee records
- Hacked account exposing personal data

**SICO's 3-Step Process:**

1. **Internal Notification (IMMEDIATE)**
   - Report to security@sicocompany.sa + privacy@sicocompany.sa
   - DPO and CISO notified within 1 hour

2. **SDAIA Notification (72 HOURS)**
   - If breach likely to result in risk to data subjects
   - DPO submits notification to SDAIA portal
   - Includes: nature of breach, data subjects affected, mitigation measures

3. **Data Subject Notification (WITHOUT UNDUE DELAY)**
   - If breach likely to result in high risk to rights and freedoms
   - Plain Arabic language communication
   - Describes breach, consequences, remedial actions, DPO contact

**Penalties for Non-Compliance:**
- Fines up to SAR 5 million
- Imprisonment up to 2 years
- Compensation to affected individuals

---

## Section 3: SDAIA AI Ethics Principles (5 minutes)

### What is SDAIA?

**Saudi Data & AI Authority** (الهيئة السعودية للبيانات والذكاء الاصطناعي)

**Mission**: Drive digital transformation, govern data, regulate AI

### AI Ethics Principles for SICO

SICO GRC Platform uses AI/RAG (Retrieval-Augmented Generation) for compliance queries. We must ensure:

1. **Transparency**
   - Users know when interacting with AI
   - AI decisions are explainable
   - **SICO Implementation**: AI responses include source citations (control IDs)

2. **Fairness and Non-Discrimination**
   - AI doesn't discriminate based on protected characteristics
   - Equal treatment regardless of user attributes
   - **SICO Implementation**: Bias testing in AI models, diverse training data

3. **Accountability**
   - Clear ownership of AI systems
   - Human oversight of AI decisions
   - **SICO Implementation**: AI Governance Committee, human review of flagged responses

4. **Privacy**
   - AI respects personal data protection
   - Minimize data collection, secure storage
   - **SICO Implementation**: No PII in AI training data, encrypted embeddings

5. **Security and Safety**
   - AI systems protected from attacks (adversarial inputs, prompt injection)
   - Safe failure modes (graceful degradation)
   - **SICO Implementation**: Input validation, rate limiting, monitoring

6. **Societal and Environmental Well-Being**
   - AI benefits society, doesn't cause harm
   - Energy-efficient AI models
   - **SICO Implementation**: AI assists compliance (public good), sustainable computing

### Your Role with AI Systems

**DO:**
- ✅ Use AI responsibly (don't try to manipulate or trick system)
- ✅ Verify AI-generated content (especially for critical decisions)
- ✅ Report AI errors or biased outputs
- ✅ Protect AI system credentials (same security standards)

**DON'T:**
- ❌ Input confidential/sensitive data into unauthorized AI tools (ChatGPT, Claude, etc.)
- ❌ Rely solely on AI without human judgment
- ❌ Share AI-generated content without verification
- ❌ Use AI for unethical purposes (deception, discrimination)

**Approved AI Tools at SICO:**
- ✅ SICO GRC Platform AI/RAG (internal compliance queries)
- ✅ Microsoft Copilot (commercial data protection)
- ✅ GitHub Copilot (code suggestions)
- ❌ Public ChatGPT, Claude, Gemini (prohibited for work data)

---

## Quiz: 10 Questions (80% passing)

### Question 1
**What is the NCA's Essential Cybersecurity Controls (ECC)?**

A. Optional guidelines for large enterprises  
B. Minimum cybersecurity requirements for Saudi organizations ✅  
C. International standard (not Saudi-specific)  
D. Only applies to government agencies  

**Explanation**: NCA ECC v1.0 establishes mandatory baseline controls for all Saudi organizations handling sensitive data or critical infrastructure.

---

### Question 2
**Under NCA ECC, critical security incidents must be reported to NCA within:**

A. 24 hours  
B. 48 hours  
C. 72 hours ✅  
D. 1 week  

**Explanation**: NCA requires notification of critical cybersecurity incidents within 72 hours. SICO Security Team handles this notification (you report to us immediately).

---

### Question 3
**Which of the following is personal data under PDPL?**

A. Company name  
B. Employee email address ✅  
C. Public IP address range  
D. Industry statistics  

**Explanation**: Personal data is any information relating to an identified or identifiable person. Employee email (name@company.sa) identifies a specific person.

---

### Question 4
**PDPL requires personal data breach notification to SDAIA within:**

A. 24 hours  
B. 48 hours  
C. 72 hours ✅  
D. Not required  

**Explanation**: Similar to GDPR, PDPL mandates breach notification to SDAIA within 72 hours if breach likely poses risk to data subjects.

---

### Question 5
**You accidentally send an email containing 50 customer names and phone numbers to the wrong recipient. What should you do?**

A. Recall the email and hope recipient didn't open it  
B. Do nothing (only 50 people affected)  
C. Immediately report to security@sicocompany.sa and privacy@sicocompany.sa ✅  
D. Report next week during weekly team meeting  

**Explanation**: This is a personal data breach under PDPL. Immediate reporting required (within 1 hour internally) so DPO can assess and meet 72-hour SDAIA notification deadline if applicable.

---

### Question 6
**Under PDPL, data subjects have the right to:**

A. Request deletion of their personal data ✅  
B. Demand unlimited storage of their data  
C. Access anyone else's personal data  
D. Change their data without verification  

**Explanation**: PDPL grants data subjects rights including access, correction, deletion ("right to be forgotten"), and objection to processing.

---

### Question 7
**SICO stores customer data in Azure cloud. According to NCA CCC, this data must be:**

A. Stored in any global Azure region  
B. Stored in Saudi Arabia regions (Riyadh/Jeddah) ✅  
C. Stored on-premise only  
D. Stored without encryption (cloud is secure)  

**Explanation**: NCA CCC requires data residency in Saudi Arabia. SICO uses Azure Riyadh (primary) and Jeddah (DR) regions for compliance.

---

### Question 8
**You want to use ChatGPT to help draft a compliance report. What should you do?**

A. Copy-paste SICO customer data into ChatGPT for analysis  
B. Use ChatGPT freely (it's a productivity tool)  
C. Don't use ChatGPT for SICO work data (not approved) ✅  
D. Use it only for non-confidential work  

**Explanation**: Public AI tools like ChatGPT are NOT approved for SICO work data (PDPL violation, NDA breach). Use approved tools: SICO GRC AI/RAG, Microsoft Copilot.

---

### Question 9
**What is SDAIA's role in Saudi Arabia?**

A. Cybersecurity incident response  
B. Data protection and AI regulation ✅  
C. Cloud service provider  
D. Internet service provider  

**Explanation**: SDAIA (Saudi Data & AI Authority) regulates data protection (enforces PDPL) and AI ethics, while NCA focuses on cybersecurity.

---

### Question 10
**SICO's AI/RAG system provides compliance answers with citations. This demonstrates which AI ethics principle?**

A. Environmental well-being  
B. Transparency (explainability) ✅  
C. Fairness  
D. Privacy  

**Explanation**: Transparency requires AI systems to be explainable. SICO's AI provides source citations (control IDs) so users understand how answers were generated.

---

## Certificate of Completion

**Well Done!** You understand Saudi Arabia's key regulations and SICO's compliance obligations.

**Your Results:**
- Score: [X]/10 ([X]%)
- Status: [PASS/FAIL]
- Completion Date: [DATE]
- Certificate Number: TRAIN-002-[USER_ID]-[DATE]

**Key Takeaways:**
- NCA ECC: 114 controls, report critical incidents within 72h
- PDPL: Protect personal data, report breaches immediately
- SDAIA AI: Transparency, accountability, approved tools only
- YOUR ROLE: Follow policies, report incidents, respect privacy

**Next Module**: Module 3: Data Protection & Privacy (30 min)

---

**Course Developer**: SICO Compliance Team  
**Version**: 1.0 (February 2026)  
**Policy Reference**: POL-CM-001 Compliance Management Policy
