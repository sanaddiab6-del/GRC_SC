# Module 3: Data Protection & Privacy
## 30-Minute Privacy Training (PDPL Compliance)

**Course Code**: TRAIN-PRIV-001  
**Category**: Privacy/Data Protection (Mandatory)  
**Duration**: 30 minutes  
**Passing Score**: 80% (8/10 questions)  
**Recertification**: Annually

---

## Learning Objectives

1. Understand data protection principles and PDPL requirements
2. Identify and classify personal data correctly
3. Handle data subject access requests (DSAR)
4. Recognize and report personal data breaches
5. Apply privacy-by-design in daily work

---

## Section 1: Data Classification (7 minutes)

### SICO Data Classification Framework

| **Level** | **Definition** | **Examples** | **Handling Requirements** |
|-----------|----------------|--------------|--------------------------|
| **🔴 Restricted** | Extremely sensitive, severe harm if disclosed | Customer passwords, payment card data (PAN), health records, biometric data | Encryption required (rest+transit), access logged, no email transmission, annual access review |
| **🟠 Confidential** | Sensitive business/personal data, significant harm | Customer contracts, employee salaries, PII (names+IDs+phones), audit reports, source code | Encryption recommended, authorized access only, secure file transfer, quarterly review |
| **🟡 Internal** | Internal use only, moderate harm | Internal policies, organizational charts, project plans, non-PII operational data | Access controls, no public sharing, can email internally |
| **🟢 Public** | Approved for public release, no harm | Marketing materials, public website content, press releases | No restrictions, but verify approval before external sharing |

### Quick Classification Guide

**Is it Personal Data?** (Can it identify a person?) → Yes = Confidential minimum

**Contains:**
- Health/biometric/financial data → **Restricted**
- Name + ID/phone/address → **Confidential**
- Employee work email only → **Internal**
- Published on sicocompany.sa → **Public**

**When in Doubt:** Treat as Confidential

---

## Section 2: Handling Personal Data (8 minutes)

### Collection: Get Consent

**Before collecting personal data:**

✅ **DO:**
- Obtain explicit consent (opt-in, not pre-checked boxes)
- Explain purpose clearly (why you need the data)
- Specify retention period (how long you'll keep it)
- Inform about disclosure (who else will see it)
- Document consent (timestamp, IP address, consent text)

❌ **DON'T:**
- Use pre-ticked consent boxes
- Collect "just in case" (data minimization principle)
- Force consent for unrelated services (consent bundling)
- Use confusing language or hide in terms & conditions

**Example Good Consent:**
```
☐ I consent to SICO collecting and processing my name, email, and 
   company information for the purpose of providing GRC compliance 
   services. Data will be retained for the duration of our service 
   contract plus 7 years for regulatory compliance. Data will be 
   shared with our cloud provider (Microsoft Azure, Saudi Arabia 
   regions only). I can withdraw consent at any time by emailing 
   privacy@sicocompany.sa.
```

### Processing: Purpose Limitation

**Process personal data ONLY for:**
- Original purpose stated during collection
- Legal obligation (e.g., tax records)
- Legitimate interest (with documented assessment)

**Example VIOLATION:**
- Collected email for "compliance reports" → Used for marketing newsletters ❌
- Solution: Obtain separate consent for marketing ✅

### Storage: Data Minimization

**Collect and retain ONLY what's necessary:**

✅ **Necessary:** Customer name, company, email (to provide service)  
❌ **Excessive:** Customer spouse name, children's ages, hobbies

**Retention Periods (SICO):**
- Customer contracts/data: 7 years after termination (regulatory requirement)
- Employee records: 7 years after termination
- Audit logs: 1 year (NCA requirement)
- Marketing consent: Until withdrawn + 30 days
- CCTV footage: 90 days

**Automatic Deletion:**
- SICO GRC Platform has automated deletion jobs
- Expired data flagged and purged monthly
- Manual deletion requests processed within 30 days

### Disclosure: Third-Party Sharing

**When sharing personal data with third parties:**

✅ **Requirements:**
1. Data Processing Agreement (DPA) signed before sharing
2. Recipient has adequate security (vendor assessment)
3. Purpose limitation (only for specified reason)
4. Data subject informed (in privacy notice)
5. Transfer outside Saudi Arabia only with safeguards (Standard Contractual Clauses)

**SICO Approved Third Parties:**
- Microsoft Azure (cloud hosting - DPA signed, data residency Saudi Arabia)
- Microsoft 365 (email, collaboration - DPA signed)
- Background check vendor (for HR screening - DPA signed)

❌ **NEVER share personal data:**
- With unapproved vendors
- For purposes beyond original consent
- Via insecure channels (unencrypted email, personal cloud)
- Outside Saudi Arabia without proper safeguards

---

## Section 3: Data Subject Rights (DSAR) (7 minutes)

### The 8 Rights Under PDPL

#### 1. Right to Access
**What:** Copy of their personal data  
**Timeline:** 30 days  
**Process:** Submit request to privacy@sicocompany.sa → DPO reviews → Provide data in PDF format

#### 2. Right to Correction
**What:** Fix inaccurate data  
**Timeline:** 14 days  
**Process:** Verify identity → Update in systems → Notify data subject

#### 3. Right to Deletion ("Right to be Forgotten")
**What:** Delete personal data  
**Exceptions:** Cannot delete if needed for legal obligations (tax, audit, ongoing contract)  
**Timeline:** 30 days  
**Process:** Assess exceptions → Delete from active systems + backups → Confirm to data subject

#### 4. Right to Objection
**What:** Object to processing (e.g., marketing)  
**Timeline:** Immediate (stop processing upon receipt)  
**Process:** Honor immediately unless legal obligation requires continuation

#### 5. Right to Data Portability
**What:** Receive data in machine-readable format (CSV, JSON)  
**Timeline:** 30 days  
**Process:** Export structured data → Provide securely

#### 6. Right to Restrict Processing
**What:** Temporarily halt processing (during dispute)  
**Timeline:** Immediate  
**Process:** Flag account, pause processing, investigate

#### 7. Right to Withdraw Consent
**What:** Revoke previously given consent  
**Timeline:** Immediate  
**Effect:** Stop processing for that purpose (cannot affect past processing)

#### 8. Right to Complain
**What:** File complaint with SDAIA  
**Your Role:** Cooperate with investigation, provide evidence

### Handling DSAR at SICO

**Step 1: Receive Request**
- Requests come to: privacy@sicocompany.sa  
- Forward immediately to DPO (do NOT handle yourself)
- Valid methods: Email, written letter, online form

**Step 2: Identity Verification**
- DPO verifies identity (to prevent data disclosure to wrong person)
- Government ID, security questions, or account verification

**Step 3: Search Systems**
- DPO searches all systems: databases, emails, file shares, backups
- Assistance from IT and department heads

**Step 4: Review and Redact**
- Remove other people's personal data (only requestor's data)
- Apply legal exemptions (if applicable)

**Step 5: Deliver Response**
- Free of charge (first request; fee for excessive/repetitive)
- Secure delivery (encrypted email, password-protected portal)
- Within 30 days (extension if complex, with notification)

**Example DSAR Response:**
```
Subject: Your Data Subject Access Request - Reference DSAR-2026-0042

Dear [Name],

Thank you for your request dated February 5, 2026. Please find attached 
your personal data held by SICO in the following categories:

1. Account Information (name, email, phone, company)
2. Service Usage Logs (login history, feature usage)
3. Support Tickets (3 tickets from 2024-2025)

If you have questions or wish to exercise other rights (correction, 
deletion), please contact privacy@sicocompany.sa.

Best regards,
SICO Data Protection Officer
```

---

## Section 4: Personal Data Breaches (5 minutes)

### What Counts as a Breach?

**Any unauthorized or unlawful:**
- Access (hacker views customer database)
- Disclosure (email to wrong recipient)
- Loss (lost unencrypted laptop)
- Destruction (ransomware deletes backups)
- Alteration (unauthorized modification of records)

### Real Examples

**Example 1: Lost Device ✅ REPORT**
- Employee loses laptop with customer list (500 records, names + emails)
- **Even if encrypted** → Report immediately (assess risk)

**Example 2: Misdirected Email ⚠️ REPORT**
- Sent email with 10 employee salary details to wrong person
- Personal data exposed → Report to security + privacy immediately

**Example 3: Ransomware Attack 🚨 CRITICAL REPORT**
- Ransomware encrypts server with 10,000 customer records
- Availability breach → Report immediately (72-hour SDAIA deadline)

**Example 4: Secure Safe (No Breach)**
- Attempted phishing email sent but no one clicked
- No personal data accessed → Log but may not trigger breach notification

### Breach Response Timeline

**T+0 (Immediate):** Discover + Report Internally
- Report to security@sicocompany.sa AND privacy@sicocompany.sa
- Include: What happened, data involved, number of people affected

**T+1 hour:** DPO + CISO Assess Severity
- Low risk → Internal documentation only
- Medium/High risk → SDAIA notification required

**T+72 hours:** SDAIA Notification (if required)
- DPO submits via SDAIA portal
- Details: Nature, scope, consequences, mitigation

**T+0 (No undue delay):** Data Subject Notification (if high risk)
- Plain Arabic communication
- What happened, what we're doing, how to protect yourself

### Breach Prevention

**Technical Controls:**
- Encryption (BitLocker on laptops, TLS for email)
- Access controls (RBAC, least privilege)
- DLP (Data Loss Prevention) blocks sensitive data in emails
- MFA prevents account compromises

**Your Responsibilities:**
- Lock screen when away (Windows + L)
- Don't email sensitive data (use secure file share)
- Report lost devices immediately
- Complete security training (phishing awareness)

---

## Section 5: Privacy by Design (3 minutes)

### Build Privacy In, Not Bolt On

**What is Privacy by Design?**
Embedding privacy into systems and processes from the start, not as an afterthought.

**7 Principles:**

1. **Proactive not Reactive** → Prevent privacy issues before they occur
2. **Privacy as Default** → Maximum privacy is the default setting (opt-in, not opt-out)
3. **Privacy Embedded** → Built into systems, not add-on
4. **Full Functionality** → Win-win, not zero-sum (privacy AND business goals)
5. **End-to-End** → Lifecycle protection (collection → deletion)
6. **Visibility and Transparency** → Clear privacy notices, open about practices
7. **Respect for User Privacy** → User-centric approach

### Privacy by Design at SICO

**In Software Development:**
- Privacy Impact Assessment (PIA) for new features
- Data minimization in database design (collect only needed fields)
- Encryption by default (no unencrypted databases)
- Secure defaults (opt-in consent, MFA required)

**Example:**
- ❌ **Bad:** Store full credit card numbers in database (not needed)
- ✅ **Good:** Store last 4 digits only (sufficient for support)

**In Business Processes:**
- Limit access (RBAC, need-to-know)
- Short retention periods (auto-delete after regulatory period)
- Data masking in non-production (test databases use synthetic data)
- Privacy training (what you're completing now!)

**Your Role:**
- Ask "Do we really need this data?" before collecting
- Design forms with minimal fields
- Default to most private option
- Question "why" when asked to collect personal data

---

## Quiz: 10 Questions (80% passing)

### Question 1
**A customer emails you asking for a copy of all their personal data SICO holds. What should you do?**

A. Send them their data immediately  
B. Forward the request to privacy@sicocompany.sa ✅  
C. Ignore (too much work)  
D. Ask them to submit a ticket  

**Explanation**: This is a Data Subject Access Request (DSAR). Only the DPO handles DSARs to ensure proper verification, search, and legal compliance (30-day deadline).

---

### Question 2
**You need to classify a spreadsheet containing customer names, email addresses, and company names. What classification level?**

A. Public  
B. Internal  
C. Confidential ✅  
D. Restricted  

**Explanation**: Name + email = Personal Data under PDPL. Personal data is always Confidential minimum (unless also health/biometric/financial = Restricted).

---

### Question 3
**Under PDPL, personal data breaches must be reported to SDAIA within:**

A. 24 hours  
B. 48 hours  
C. 72 hours ✅  
D. 1 week  

**Explanation**: If breach likely poses risk to data subjects, PDPL requires SDAIA notification within 72 hours (similar to GDPR). DPO handles submission.

---

### Question 4
**You accidentally send an email containing 20 employee ID numbers to an external recipient. What should you do?**

A. Recall the email and hope they didn't open it  
B. Ask recipient to delete (honor system)  
C. Immediately report to security@sicocompany.sa AND privacy@sicocompany.sa ✅  
D. Tell only your manager  

**Explanation**: This is a personal data breach (unauthorized disclosure of PII). Immediate reporting required so DPO can assess and meet 72-hour SDAIA deadline if applicable.

---

### Question 5
**A customer requests deletion of their personal data. However, we need their contract for tax audit (7-year retention). What should SICO do?**

A. Delete immediately (customer right)  
B. Refuse deletion and explain legal obligation exception ✅  
C. Anonymize the data  
D. Charge a fee for keeping the data  

**Explanation**: Right to deletion has exceptions. Legal obligations (tax, audit) override deletion requests. DPO documents exception and informs data subject.

---

### Question 6
**When collecting personal data from website visitors, SICO must:**

A. Assume consent (they voluntarily visited)  
B. Obtain explicit opt-in consent with clear purpose ✅  
C. Use pre-checked consent boxes  
D. Collect first, ask later  

**Explanation**: PDPL requires explicit consent. Must explain purpose, retention, disclosure BEFORE collection. Pre-checked boxes invalid (must be opt-in).

---

### Question 7
**What is the maximum time to respond to a Data Subject Access Request (DSAR)?**

A. 7 days  
B. 14 days  
C. 30 days ✅  
D. 90 days  

**Explanation**: PDPL requires response within 30 days. Can extend if complex, but must notify data subject within initial 30 days.

---

### Question 8
**You want to use customer email list collected for "compliance reports" to send marketing newsletters. Is this allowed?**

A. Yes (they're existing customers)  
B. Yes (it's the same company)  
C. No, need separate consent for marketing ✅  
D. Yes, but include unsubscribe link  

**Explanation**: Purpose limitation principle. Cannot use data for purposes beyond original consent. Must obtain separate opt-in consent for marketing.

---

### Question 9
**Privacy by Design means:**

A. Adding privacy features after system is built  
B. Embedding privacy into systems from the start ✅  
C. Hiring a data protection officer  
D. Encrypting databases only  

**Explanation**: Privacy by Design = proactive, default privacy, embedded from the beginning (not bolt-on). Includes technical (encryption) + organizational (policies) measures.

---

### Question 10
**SICO stores customer data in Microsoft Azure. To comply with data residency requirements, data must be in:**

A. Any Azure global region  
B. Europe (close to Middle East)  
C. Saudi Arabia regions (Riyadh/Jeddah) ✅  
D. USA (Azure headquarters)  

**Explanation**: NCA CCC and PDPL prefer data residency in Saudi Arabia. SICO uses Azure Riyadh (primary) and Jeddah (DR) for compliance.

---

## Certificate of Completion

**Excellent Work!** You now understand data protection principles and SICO's privacy obligations.

**Your Results:**
- Score: [X]/10 ([X]%)
- Status: [PASS/FAIL]
- Completion Date: [DATE]
- Certificate Number: TRAIN-003-[USER_ID]-[DATE]

**Key Takeaways:**
- Classify data correctly: PII = Confidential minimum
- Get explicit consent before collection, honor data subject rights
- Report breaches immediately (security + privacy)
- DSAR forwarded to DPO (30-day response)
- Privacy by Design: build privacy in from the start

**Next Module**: Module 4: Physical Security (15 min)

---

**Course Developer**: SICO Data Protection Officer  
**Version**: 1.0 (February 2026)  
**Policy Reference**: POL-PV-001 Privacy Policy, POL-PV-002 Data Subject Rights
