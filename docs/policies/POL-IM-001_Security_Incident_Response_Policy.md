# Security Incident Response Policy | سياسة الاستجابة للحوادث الأمنية

## POL-IM-001

---

## Document Control | التحكم في الوثيقة

| **Field** | **English** | **العربية** |
|-----------|-------------|--------------|
| **Policy Number** | POL-IM-001 | رقم السياسة: POL-IM-001 |
| **Version** | 1.0 | الإصدار: 1.0 |
| **Effective Date** | 2026-03-01 | تاريخ السريان: 1 مارس 2026 |

---

## 1. Purpose | الغرض

### English
Establish procedures for detecting, reporting, assessing, responding to, and recovering from security incidents in compliance with ISO 27001 A.5.24-A.5.28, NCA ECC-IM, and PDPL Article 20 breach notification requirements.

### العربية
وضع إجراءات لاكتشاف والإبلاغ عن وتقييم والاستجابة والتعافي من الحوادث الأمنية بما يتوافق مع ISO 27001 A.5.24-A.5.28، NCA ECC-IM، ومتطلبات إشعار الانتهاك PDPL المادة 20.

---

## 2. Incident Definition and Classification | تعريف الحادثة وتصنيفها

### English

**Security Incident:** Any event that compromises confidentiality, integrity, or availability of information assets.

**Severity Levels:**

| **Severity** | **Description** | **Examples** | **Response Time** |
|--------------|-----------------|--------------|-------------------|
| **Critical (P0)** | Severe business impact, active threat | Ransomware, data breach >10,000 records, system compromise | Immediate (15 min) |
| **High (P1)** | Significant impact, data exposure | Malware outbreak, unauthorized access, DDOS attack | 1 hour |
| **Medium (P2)** | Moderate impact, contained threat | Failed intrusion attempt, policy violation, suspicious activity | 4 hours |
| **Low (P3)** | Minor impact, limited scope | Lost device (encrypted), phishing email (no click), security misconfiguration | 24 hours |

**Personal Data Breach:** Any incident involving unauthorized access, disclosure, loss, or destruction of personal data regulated under PDPL.

### العربية

**الحادثة الأمنية:** أي حدث يعرض سرية أو سلامة أو توفر أصول المعلومات للخطر.

**مستويات الخطورة:**

| **الخطورة** | **الوصف** | **أمثلة** | **وقت الاستجابة** |
|-------------|-----------|----------|-------------------|
| **حرج (P0)** | تأثير شديد على العمل، تهديد نشط | برامج الفدية، اختراق البيانات >10,000 سجل، اختراق النظام | فوري (15 دقيقة) |
| **عالي (P1)** | تأثير كبير، كشف البيانات | تفشي البرامج الضارة، الوصول غير المصرح به، هجوم DDOS | 1 ساعة |
| **متوسط (P2)** | تأثير معتدل، تهديد محتوى | محاولة اختراق فاشلة، انتهاك السياسة، نشاط مشبوه | 4 ساعات |
| **منخفض (P3)** | تأثير بسيط، نطاق محدود | جهاز مفقود (مشفر)، بريد إلكتروني تصيّدي (لا نقر)، خطأ في التكوين الأمني | 24 ساعة |

**انتهاك البيانات الشخصية:** أي حادثة تنطوي على وصول أو إفصاح أو فقدان أو تدمير غير مصرح به للبيانات الشخصية المنظمة بموجب PDPL.

---

## 3. Incident Reporting | الإبلاغ عن الحوادث

### English

**Reporting Channels:**

📧 **Email**: security@sicocompany.sa  
☎️ **Phone**: +966-XX-XXXX-XXXX (24/7 Security Hotline)  
🌐 **Portal**: https://security.sicocompany.sa/report-incident  
💬 **Teams/Slack**: #security-incidents channel  

**Mandatory Reporting Requirements:**

✅ **Who Must Report**: All employees, contractors, third parties  
✅ **What to Report**: Suspected or confirmed security incidents  
✅ **When to Report**: Immediately upon discovery (within 1 hour)  
✅ **What Information**: Date/time, description, systems affected, data involved, actions taken  

**Anonymous Reporting:**
- Ethics Hotline: 1-800-XXX-XXXX
- No retaliation for good-faith reporting
- Confidentiality maintained

**Penalties for Non-Reporting:**
- Failure to report = policy violation
- Disciplinary action up to termination
- Legal liability for damages caused by delayed reporting

### العربية

**قنوات الإبلاغ:**

📧 **البريد الإلكتروني**: security@sicocompany.sa  
☎️ **الهاتف**: +966-XX-XXXX-XXXX (الخط الساخن للأمن 24/7)  
🌐 **البوابة**: https://security.sicocompany.sa/report-incident  
💬 **Teams/Slack**: قناة #security-incidents  

**متطلبات الإبلاغ الإلزامي:**

✅ **من يجب أن يبلغ**: جميع الموظفين، المقاولين، الأطراف الثالثة  
✅ **ما يجب الإبلاغ عنه**: الحوادث الأمنية المشتبه بها أو المؤكدة  
✅ **متى يبلغ**: فورًا عند الاكتشاف (خلال ساعة واحدة)  
✅ **ما المعلومات**: التاريخ/الوقت، الوصف، الأنظمة المتأثرة، البيانات المعنية، الإجراءات المتخذة  

**الإبلاغ المجهول:**
- الخط الساخن للأخلاقيات: 1-800-XXX-XXXX
- لا انتقام للإبلاغ بحسن نية
- الحفاظ على السرية

**عقوبات عدم الإبلاغ:**
- الفشل في الإبلاغ = انتهاك السياسة
- إجراء تأديبي حتى الإنهاء
- المسؤولية القانونية عن الأضرار الناجمة عن التأخير في الإبلاغ

---

## 4. Incident Response Process | عملية الاستجابة للحوادث

### English

**Phase 1: Detection and Reporting (0-1 hour)**
1. Incident detected via SIEM, user report, monitoring alert
2. Initial report logged in incident tracking system
3. CSIRT (Computer Security Incident Response Team) notified
4. Preliminary assessment: severity, scope, affected systems

**Phase 2: Containment (Immediate)**
1. **Short-term containment**: Isolate affected systems
   - Disconnect from network if necessary
   - Disable compromised user accounts
   - Block malicious IPs/domains at firewall
2. **Evidence preservation**: Take forensic images, preserve logs
3. **Communication**: Notify stakeholders per communication plan

**Phase 3: Eradication (Within 24-72 hours)**
1. Remove malware, backdoors, unauthorized access
2. Patch vulnerabilities exploited
3. Reset compromised credentials
4. Rebuild/restore systems from clean backups if needed

**Phase 4: Recovery (Within 1 week)**
1. Restore systems to normal operations
2. Enhanced monitoring for re-infection
3. Validate system integrity
4. User communication and training as needed

**Phase 5: Post-Incident (Within 2 weeks)**
1. Root cause analysis
2. Lessons learned meeting
3. Update incident response procedures
4. Implement preventive measures
5. Final incident report to management

### العربية

**المرحلة 1: الكشف والإبلاغ (0-1 ساعة)**
1. الكشف عن الحادثة عبر SIEM، تقرير المستخدم، تنبيه المراقبة
2. تسجيل التقرير الأولي في نظام تتبع الحوادث
3. إخطار CSIRT (فريق الاستجابة للحوادث الأمنية الحاسوبية)
4. التقييم الأولي: الخطورة، النطاق، الأنظمة المتأثرة

**المرحلة 2: الاحتواء (فوري)**
1. **الاحتواء قصير الأجل**: عزل الأنظمة المتأثرة
   - قطع الاتصال بالشبكة إذا لزم الأمر
   - تعطيل حسابات المستخدمين المخترقة
   - حظر عناوين IP/المجالات الخبيثة في جدار الحماية
2. **الحفاظ على الأدلة**: أخذ صور الطب الشرعي، الحفاظ على السجلات
3. **الاتصال**: إخطار أصحاب المصلحة وفقًا لخطة الاتصال

**المرحلة 3: الاستئصال (خلال 24-72 ساعة)**
1. إزالة البرامج الضارة، الأبواب الخلفية، الوصول غير المصرح به
2. تصحيح الثغرات المستغلة
3. إعادة تعيين بيانات الاعتماد المخترقة
4. إعادة بناء/استعادة الأنظمة من النسخ الاحتياطية النظيفة إذا لزم الأمر

**المرحلة 4: الاسترداد (خلال أسبوع واحد)**
1. استعادة الأنظمة إلى العمليات العادية
2. المراقبة المحسّنة لإعادة العدوى
3. التحقق من سلامة النظام
4. اتصالات المستخدم والتدريب حسب الحاجة

**المرحلة 5: ما بعد الحادثة (خلال أسبوعين)**
1. تحليل السبب الجذري
2. اجتماع الدروس المستفادة
3. تحديث إجراءات الاستجابة للحوادث
4. تنفيذ التدابير الوقائية
5. تقرير الحادثة النهائي للإدارة

---

## 5. PDPL Breach Notification | إخطار انتهاك PDPL

### English

**Personal Data Breach Requirements (PDPL Article 20):**

**Internal Notification (Immediate):**
- DPO (Data Protection Officer) notified within 1 hour
- CISO and Legal Counsel notified
- Impact assessment: number of data subjects, data types, harm potential

**SDAIA Notification (72 hours):**
- If breach likely to result in risk to data subjects' rights and freedoms
- Notification via SDAIA National Data Management Office portal
- Information required:
  - Nature of breach
  - Categories and approximate number of data subjects
  - Categories and approximate number of records
  - Likely consequences
  - Measures taken or proposed to mitigate
  - Contact details of DPO

**Data Subject Notification (Without undue delay):**
- Required when breach likely to result in high risk to rights and freedoms
- Plain language communication in Arabic
- Information: nature of breach, consequences, measures taken, DPO contact
- Method: Email, postal mail, or public announcement if impractical to notify individually

**Exemptions from Data Subject Notification:**
- Technical protection measures applied (e.g., encryption)
- Subsequent measures ensure high risk no longer likely
- Disproportionate effort (must inform via public communication)

### العربية

**متطلبات انتهاك البيانات الشخصية (PDPL المادة 20):**

**الإخطار الداخلي (فوري):**
- إخطار DPO (مسؤول حماية البيانات) خلال ساعة واحدة
- إخطار مدير أمن المعلومات والمستشار القانوني
- تقييم الأثر: عدد أصحاب البيانات، أنواع البيانات، إمكانية الضرر

**إخطار SDAIA (72 ساعة):**
- إذا كان الانتهاك من المحتمل أن يؤدي إلى خطر على حقوق وحريات أصحاب البيانات
- الإخطار عبر بوابة المكتب الوطني لإدارة البيانات SDAIA
- المعلومات المطلوبة:
  - طبيعة الانتهاك
  - فئات وعدد تقريبي لأصحاب البيانات
  - فئات وعدد تقريبي للسجلات
  - العواقب المحتملة
  - التدابير المتخذة أو المقترحة للتخفيف
  - تفاصيل الاتصال بـ DPO

**إخطار أصحاب البيانات (دون تأخير لا مبرر له):**
- مطلوب عندما يكون الانتهاك من المحتمل أن يؤدي إلى مخاطر عالية على الحقوق والحريات
- التواصل بلغة واضحة بالعربية
- المعلومات: طبيعة الانتهاك، العواقب، التدابير المتخذة، اتصال DPO
- الطريقة: البريد الإلكتروني، البريد العادي، أو الإعلان العام إذا كان من غير العملي الإخطار بشكل فردي

**الاستثناءات من إخطار أصحاب البيانات:**
- تطبيق تدابير الحماية التقنية (مثل التشفير)
- التدابير اللاحقة تضمن أن المخاطر العالية لم تعد محتملة
- جهد غير متناسب (يجب الإبلاغ عبر التواصل العام)

---

## 6. CSIRT (Computer Security Incident Response Team) | فريق CSIRT

### English

**Team Structure:**

| **Role** | **Responsibilities** | **24/7 Contact** |
|----------|---------------------|------------------|
| **Incident Commander** | Overall coordination, decision authority | CISO or Deputy |
| **Technical Lead** | Forensics, malware analysis, system recovery | Senior Security Engineer |
| **Communications Lead** | Stakeholder notifications, media relations | Legal/Communications |
| **Legal Advisor** | Regulatory compliance, law enforcement liaison | General Counsel |
| **DPO** | PDPL breach assessment and notification | Data Protection Officer |
| **IT Operations** | System isolation, restoration, infrastructure | IT Manager |
| **HR Representative** | Insider threat investigations, employee communications | HR Director |

**Escalation Matrix:**

- **P3 (Low)**: Security Analyst handles
- **P2 (Medium)**: Security Team + IT Operations
- **P1 (High)**: CSIRT activated, CISO notified
- **P0 (Critical)**: Full CSIRT + CEO + Board notification

### العربية

**هيكل الفريق:**

يتضمن قائد الحادثة (CISO)، القائد التقني (مهندس الأمن الأول)، قائد الاتصالات (القانوني)، المستشار القانوني (المستشار العام)، DPO (مسؤول حماية البيانات)، عمليات تقنية المعلومات (مدير تقنية المعلومات)، ممثل الموارد البشرية (مدير الموارد البشرية).

**مصفوفة التصعيد:**

- **P3 (منخفض)**: محلل الأمن يتعامل
- **P2 (متوسط)**: فريق الأمن + عمليات تقنية المعلومات
- **P1 (عالي)**: تفعيل CSIRT، إخطار مدير أمن المعلومات
- **P0 (حرج)**: CSIRT كامل + إخطار الرئيس التنفيذي + المجلس

---

## 7. Compliance | الامتثال

### English

| **Framework** | **Control** | **Requirement** |
|---------------|-------------|-----------------|
| ISO 27001 | A.5.24-A.5.28 | Incident management and response |
| NCA ECC | ECC-IM-1 through ECC-IM-6 | Incident management domain |
| NCA CCC | CCC-IRS-1 through CCC-IRS-5 | Incident response and security events |
| PDPL | Article 20 | Personal data breach notification |
| NIST CSF 2.0 | RS.MA, RS.AN, RS.MI, RS.IM | Respond function |

### العربية
يدعم ISO 27001 (A.5.24-A.5.28)، NCA ECC (IM-1 إلى IM-6)، NCA CCC (IRS-1 إلى IRS-5)، PDPL (المادة 20)، NIST CSF 2.0 (RS.MA-RS.IM).

---

*Related Policies: POL-IM-002 (Vulnerability Management), POL-BC-001 (Business Continuity), POL-PV-001 (Privacy)*
