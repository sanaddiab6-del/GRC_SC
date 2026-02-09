# Module 1: Information Security Basics
## 30-Minute Security Awareness Training

**Course Code**: TRAIN-AWARE-001  
**Category**: Security Awareness (Mandatory)  
**Duration**: 30 minutes  
**Passing Score**: 80% (8/10 questions)  
**Recertification**: Annually

---

## Learning Objectives

By the end of this module, you will be able to:
1. Explain the CIA triad (Confidentiality, Integrity, Availability)
2. Identify common cyber threats (phishing, malware, social engineering)
3. Apply password security best practices
4. Recognize physical security risks
5. Report security incidents promptly

---

## Section 1: The CIA Triad (5 minutes)

### What is Information Security?

Information security protects SICO's most valuable asset: **information**. We protect three key properties:

#### 🔒 **Confidentiality**
- **Definition**: Only authorized people can access information
- **Examples**: Customer data, trade secrets, employee records
- **Threats**: Data breaches, unauthorized access, insider threats
- **Your Role**: Lock your screen, don't share passwords, encrypt sensitive emails

#### ✅ **Integrity**
- **Definition**: Information is accurate and hasn't been tampered with
- **Examples**: Financial records, audit logs, compliance reports
- **Threats**: Malware, unauthorized changes, system errors
- **Your Role**: Verify data accuracy, report suspicious changes, use change management

#### ⚡ **Availability**
- **Definition**: Information is accessible when needed
- **Examples**: SICO GRC Platform uptime, customer access to dashboards
- **Threats**: DDoS attacks, ransomware, hardware failures, natural disasters
- **Your Role**: Follow backup procedures, report outages immediately, test DR plans

---

## Section 2: Common Cyber Threats (8 minutes)

### 🎣 Phishing Attacks

**What is Phishing?**
Fraudulent emails/messages pretending to be from legitimate sources to steal credentials or install malware.

**Warning Signs:**
- ⚠️ Urgent language: "Your account will be suspended!"
- ⚠️ Suspicious sender: look-alike domains (sic0company.sa vs sicocompany.sa)
- ⚠️ Generic greetings: "Dear User" instead of your name
- ⚠️ Unexpected attachments or links
- ⚠️ Requests for passwords or personal information

**Example Phishing Email:**
```
From: IT-Support@sic0company.sa  ⚠️ (Note the zero instead of 'o')
Subject: URGENT: Verify Your Account Now!

Dear Employee,

Your email account will be suspended in 24 hours due to suspicious activity.
Click here to verify: [Malicious Link]

IT Support Team
```

**What to Do:**
1. ❌ **DO NOT CLICK** links or open attachments
2. ✅ **REPORT** using "Report Phishing" button in Outlook
3. ✅ **VERIFY** by contacting sender via known phone number (not email)
4. ✅ **DELETE** the email after reporting

### 🦠 Malware

**Types:**
- **Virus**: Spreads by attaching to files
- **Ransomware**: Encrypts your files and demands payment (CRITICAL THREAT)
- **Trojan**: Looks legitimate but contains malicious code
- **Spyware**: Secretly monitors your activity

**How Malware Spreads:**
- Phishing email attachments (.exe, .zip, .doc with macros)
- Infected USB drives
- Malicious websites
- Software vulnerabilities (unpatched systems)

**Protection:**
- Keep Windows Defender updated (automatic)
- Don't disable antivirus
- Only download software from approved sources
- Report suspicious pop-ups or slow computer performance

### 👤 Social Engineering

**Definition**: Manipulating people into giving up confidential information or access.

**Common Tactics:**
1. **Pretexting**: Impersonating IT support ("I need your password to fix your account")
2. **Baiting**: Leaving infected USB drives labeled "Employee Salaries 2026"
3. **Tailgating**: Following authorized person through secure door without badge
4. **Quid Pro Quo**: Offering something in exchange ("Free iPad if you complete this survey")

**Real SICO Example:**
Attacker calls reception: "Hi, this is Ahmed from IT. We're having network issues. Can you tell me what your screen shows right now? Also, what's your Windows login so I can check remotely?"

**Red Flags:**
- Urgency or pressure
- Too good to be true offers
- Requests for confidential information
- Bypassing normal procedures

**Defense:** When in doubt, verify identity through official channels (IT help desk ticket, call back on known number)

---

## Section 3: Password Security (7 minutes)

### 🔑 SICO Password Requirements

**Minimum Standards (POL-AC-002):**
- ✅ 12 characters minimum (14 for admin accounts)
- ✅ 3 of 4 types: Uppercase, lowercase, numbers, special characters
- ✅ Cannot reuse last 10 passwords
- ✅ Expires every 90 days (60 for admins)
- ✅ **Multi-Factor Authentication (MFA) REQUIRED**

**FORBIDDEN:**
- ❌ Company name, username, or personal info (birthdate, phone)
- ❌ Dictionary words or common patterns
- ❌ Sequential characters (123456, abcdef)
- ❌ Sharing passwords with anyone (even IT support)
- ❌ Writing passwords on sticky notes or notebooks
- ❌ Reusing work passwords for personal accounts

### Creating Strong Passwords

**Method 1: Passphrase** (Recommended)
- Think of a sentence: "I started at SICO in January 2025!"
- Take first letters: `IsaSiJ2025!`
- Add random characters: `IsaSiJ2025!#7x`

**Method 2: Random Generator**
- Use SICO-approved password manager: **1Password Enterprise**
- Generates: `Tr7$mK9@pL2nQ5vX`
- Automatically saved and synced

### 1Password Usage (MANDATORY)

**Why Use Password Manager:**
- Generates strong, unique passwords for every account
- Encrypted vault (even SICO can't see your passwords)
- Auto-fills credentials (prevents keyloggers)
- Secure sharing with team members (no email/chat)

**How to Use:**
1. Install 1Password from Company Portal
2. Sign in with your SICO email
3. Set strong master password (you'll need to remember this one!)
4. Enable MFA (Microsoft Authenticator)
5. Save all work passwords in vault

**DO NOT** store passwords in:
- ❌ Excel files
- ❌ Notepad documents
- ❌ Browser password managers (Chrome, Edge)
- ❌ Sticky notes, notebooks

### Multi-Factor Authentication (MFA)

**What is MFA?**
Two or more verification methods:
1. **Something you know**: Password
2. **Something you have**: Phone with authenticator app
3. **Something you are**: Fingerprint (future)

**SICO MFA Setup:**
- Download: Microsoft Authenticator app
- Scan QR code during first login
- Enter 6-digit code each login
- Approve push notification (faster)

**What if I lose my phone?**
- Contact IT help desk: +966-XX-XXXX-XXXX
- Temporary code issued after identity verification
- Register new device

---

## Section 4: Physical Security (5 minutes)

### 🏢 Office Security

**Badge Access:**
- ✅ Wear badge visibly at all times
- ✅ Badge swipe required for all entries (don't hold doors)
- ✅ Report lost badge immediately (24/7 hotline)
- ❌ Never lend badge to anyone (even colleagues)

**Visitor Management:**
- All visitors sign in at reception
- Escort visitors at all times
- Visitors wear temporary badges
- Challenge unescorted visitors politely: "Hi, can I help you find someone?"

**Anti-Tailgating:**
- One person per badge swipe
- Close door behind you (don't hold for strangers)
- If someone tailgates, politely ask them to use their badge

### 🖥️ Clean Desk Policy (POL-PS-002)

**When leaving your desk:**
- ✅ Lock screen (Windows + L)
- ✅ Lock documents in drawer
- ✅ Turn monitor away from public view
- ✅ Don't leave sensitive info on printer

**Document Disposal:**
- Use cross-cut shredders (not recycling bin)
- Shred anything with names, account numbers, confidential data
- Shredding bins located on each floor

### 📱 Mobile Device Security

**Laptops:**
- Enable BitLocker encryption (automatic on company laptops)
- Use cable lock in public spaces (library, café)
- Never leave unattended (even for 2 minutes)
- Report lost/stolen immediately (remote wipe activated)

**Smartphones/Tablets:**
- Enroll in Microsoft Intune (MDM)
- Set 6-digit PIN minimum
- Enable biometric unlock (fingerprint/face)
- Don't access work email on personal devices (use Outlook mobile on enrolled devices only)

**Working Remotely:**
- Use VPN for all work access (GlobalProtect)
- Secure home Wi-Fi (WPA3 encryption, strong password)
- Privacy screen on laptop (prevent shoulder surfing)
- Lock devices when stepping away

---

## Section 5: Incident Reporting (5 minutes)

### 🚨 What is a Security Incident?

Any event that compromises confidentiality, integrity, or availability:
- Lost laptop or USB drive
- Malware infection
- Unauthorized access attempt
- Data breach or leak
- Suspicious email (phishing)
- Physical security breach (tailgating, lost badge)

### Reporting Process

**When to Report:** IMMEDIATELY upon discovery (within 1 hour)

**How to Report:**
1. 📧 **Email**: security@sicocompany.sa
2. ☎️ **24/7 Hotline**: +966-XX-XXXX-XXXX
3. 🌐 **Portal**: https://security.sicocompany.sa/report
4. 💬 **Teams**: #security-incidents channel

**What to Include:**
- Date/time of incident
- What happened (be specific)
- Systems or data affected
- Actions you've taken
- Your contact information

**Example Report:**
```
Subject: Potential Phishing Email

- When: Feb 9, 2026 at 10:30 AM
- What: Received email claiming to be from CEO asking for urgent wire transfer
- Affected: My email account (ahmed@sicocompany.sa)
- Actions: Did not click link, did not reply
- Status: Email quarantined

Contact: Ahmed Al-Mutairi, ext. 1234
```

### What Happens Next?

1. **Acknowledgment**: Security Team responds within 1 hour
2. **Investigation**: Severity assessed (Critical/High/Medium/Low)
3. **Containment**: Affected systems isolated if needed
4. **Resolution**: Issue fixed, lessons learned
5. **Follow-up**: You'll receive update email

### ⚠️ NEVER Delay Reporting

**Common Fears Why People Don't Report:**
- ❌ "I'll get in trouble" → ✅ **NO PENALTIES for good-faith reporting**
- ❌ "It's probably nothing" → ✅ **Better safe than sorry - let experts decide**
- ❌ "I can fix it myself" → ✅ **Security Team has tools and authority**
- ❌ "I don't want to bother anyone" → ✅ **This is our job - report 24/7**

**Remember:** Early reporting prevents small issues from becoming major breaches.

---

## Quiz: 10 Questions (80% passing)

### Question 1
**Which of the following is an example of maintaining CONFIDENTIALITY?**

A. Backing up files daily  
B. Locking your screen when away from desk ✅  
C. Verifying data accuracy before submission  
D. Reporting system outages  

**Explanation**: Confidentiality means preventing unauthorized access. Locking your screen prevents others from viewing sensitive information.

---

### Question 2
**You receive an urgent email from "IT Support" asking for your password to fix a network issue. What should you do?**

A. Reply with your password (they're IT support)  
B. Call the IT help desk to verify the request ✅  
C. Ignore the email  
D. Forward to your manager  

**Explanation**: Legitimate IT staff NEVER ask for passwords. This is a phishing attempt. Always verify through official channels.

---

### Question 3
**Which statement about passwords is TRUE?**

A. Writing passwords on a sticky note under keyboard is acceptable if office is locked  
B. Sharing password with trusted colleague speeds up work  
C. Using the same strong password for multiple accounts is efficient  
D. A password manager generates and stores unique passwords securely ✅  

**Explanation**: 1Password (mandatory at SICO) solves the problem of remembering multiple strong passwords safely.

---

### Question 4
**What is tailgating in physical security?**

A. Following someone closely in traffic  
B. Walking through a secure door without using your own badge ✅  
C. Sending a follow-up email  
D. Monitoring someone's computer usage  

**Explanation**: Tailgating is entering a secured area by following an authorized person without proper authentication. Always badge swipe individually.

---

### Question 5
**You find a USB drive labeled "Confidential - Employee Bonuses 2026" in the parking lot. What should you do?**

A. Plug it into your computer to find the owner  
B. Take it home for safekeeping  
C. Report it to Security Team without plugging it in ✅  
D. Throw it away  

**Explanation**: This is classic "baiting" social engineering. USB drives can contain malware. Never plug unknown devices into company computers.

---

### Question 6
**Multi-Factor Authentication (MFA) requires:**

A. A very long password only  
B. Password + something you have (phone/token) ✅  
C. Two different passwords  
D. Biometric scan only  

**Explanation**: MFA combines multiple verification methods. At SICO, it's password + Microsoft Authenticator code (required for all accounts).

---

### Question 7
**When working remotely, you should:**

A. Use public Wi-Fi at cafes for convenience  
B. Connect via VPN before accessing company resources ✅  
C. Disable firewall to improve connection speed  
D. Share laptop with family members  

**Explanation**: VPN (GlobalProtect) encrypts your connection and is REQUIRED for remote access to SICO systems.

---

### Question 8
**Which is a red flag for phishing emails?**

A. Personalized greeting using your name  
B. Urgent language like "Account suspended in 24 hours!" ✅  
C. Sender from known company domain  
D. Professional formatting and logo  

**Explanation**: Phishing uses urgency to bypass critical thinking. Legitimate companies don't threaten immediate account suspension via email.

---

### Question 9
**Under SICO's Clean Desk Policy, you should:**

A. Lock confidential documents in drawer when leaving desk ✅  
B. Leave printed reports on desk if returning within 10 minutes  
C. Stack documents neatly on desk overnight  
D. Recycle sensitive documents in regular trash  

**Explanation**: Clean desk prevents unauthorized viewing. Lock/shred sensitive documents. Use cross-cut shredders, not recycling bins.

---

### Question 10
**When should you report a security incident?**

A. After trying to fix it yourself  
B. Only if you're certain it's a real incident  
C. Immediately upon discovery (within 1 hour) ✅  
D. During business hours (9 AM - 5 PM)  

**Explanation**: Report immediately to security@sicocompany.sa or 24/7 hotline. No penalties for good-faith reporting. Early detection prevents escalation.

---

## Certificate of Completion

**Congratulations!** You have completed Module 1: Information Security Basics.

**Your Results:**
- Score: [X]/10 ([X]%)
- Status: [PASS/FAIL]
- Completion Date: [DATE]
- Certificate Number: TRAIN-001-[USER_ID]-[DATE]

**Next Steps:**
- Module 2: Saudi Regulatory Compliance (20 min)
- Module 3: Data Protection & Privacy (30 min)

**Recertification Required**: February 2027 (12 months)

---

**Course Developer**: SICO Security Team  
**Version**: 1.0 (February 2026)  
**Policy Reference**: POL-HR-002 Security Awareness Training Policy
