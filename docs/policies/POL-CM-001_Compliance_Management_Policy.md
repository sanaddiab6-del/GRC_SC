# Compliance Management Policy | سياسة إدارة الامتثال

## POL-CM-001

---

## Document Control | التحكم في الوثيقة

| **Field** | **English** | **العربية** |
|-----------|-------------|--------------|
| **Policy Number** | POL-CM-001 | رقم السياسة: POL-CM-001 |
| **Version** | 1.0 | الإصدار: 1.0 |
| **Effective Date** | 2026-03-01 | تاريخ السريان: 1 مارس 2026 |

---

## 1. Purpose | الغرض

### English
Establish a comprehensive compliance management framework ensuring SICO meets all applicable regulatory, legal, contractual, and industry standard requirements, particularly Saudi regulatory obligations (NCA ECC, NCA CCC, PDPL, SDAIA AI) and international standards (ISO 27001:2022).

### العربية
وضع إطار شامل لإدارة الامتثال لضمان وفاء سيكو بجميع المتطلبات التنظيمية والقانونية والتعاقدية ومعايير الصناعة المطبقة، وخاصة الالتزامات التنظيمية السعودية (NCA ECC، NCA CCC، PDPL، SDAIA AI) والمعايير الدولية (ISO 27001:2022).

---

## 2. Scope | النطاق

### English

**Applicable Frameworks:**

| **Framework** | **Description** | **Authority** | **Review Frequency** |
|--------------|-----------------|--------------|----------------------|
| **NCA ECC** | Essential Cybersecurity Controls v1.0 (2018) | National Cybersecurity Authority | Annual |
| **NCA CCC** | Cloud Cybersecurity Controls v1.0 (2020) | National Cybersecurity Authority | Annual |
| **PDPL** | Personal Data Protection Law (2021) | Saudi Data & AI Authority (SDAIA) | Continuous |
| **SDAIA AI** | AI Ethics Principles & Responsible AI Framework | SDAIA | Semi-annual |
| **ISO 27001:2022** | Information Security Management System | International (certification body) | Annual |
| **ISO 27017** | Cloud security controls | International | Annual |
| **ISO 27018** | Cloud privacy | International | Annual |
| **ISO 27701** | Privacy Information Management System | International | Annual |
| **NIST CSF 2.0** | Cybersecurity Framework | National Institute of Standards & Technology (US) | Annual |

**Scope Coverage:**
- All SICO information systems and services
- Third-party service providers handling SICO/customer data
- All employees, contractors, and temporary staff
- All geographic locations (Saudi Arabia offices, cloud infrastructure)

### العربية

**الأطر المطبقة:**

تشمل NCA ECC (الضوابط السيبرانية الأساسية)، NCA CCC (ضوابط الأمن السيبراني السحابي)، PDPL (قانون حماية البيانات الشخصية)، SDAIA AI (مبادئ أخلاقيات الذكاء الاصطناعي)، ISO 27001:2022 (نظام إدارة أمن المعلومات)، ISO 27017/27018/27701، NIST CSF 2.0 (إطار الأمن السيبراني).

**تغطية النطاق:**
جميع أنظمة وخدمات سيكو، مقدمي الخدمات الخارجيين، جميع الموظفين، جميع المواقع الجغرافية.

---

## 3. Compliance Governance | حوكمة الامتثال

### English

**Organizational Roles:**

| **Role** | **Responsibilities** | **Reports To** |
|----------|---------------------|----------------|
| **Board of Directors** | Oversee compliance strategy, approve policies, review audit reports | Shareholders |
| **Chief Executive Officer (CEO)** | Ultimate accountability for compliance, resource allocation | Board |
| **Chief Information Security Officer (CISO)** | Lead ISMS, manage security compliance, coordinate audits | CEO |
| **Data Protection Officer (DPO)** | PDPL compliance, DPIA oversight, SDAIA liaison | CEO |
| **Compliance Manager** | Day-to-day compliance operations, regulatory monitoring, reporting | CISO |
| **Legal Counsel** | Interpret regulations, contract compliance, regulatory filings | CEO |
| **Internal Audit** | Independent compliance assessments, control testing | Board Audit Committee |
| **Department Heads** | Ensure team compliance, implement controls, report issues | Executive Team |

**Compliance Committee:**
- **Members**: CISO (Chair), DPO, Compliance Manager, Legal, Internal Audit, IT Manager
- **Meeting Frequency**: Monthly
- **Responsibilities**:
  - Review compliance status across all frameworks
  - Assess new regulatory requirements
  - Approve compliance initiatives
  - Escalate critical issues to executive team
  - Review audit findings and corrective actions

### العربية

**الأدوار التنظيمية:**

يشمل مجلس الإدارة (الإشراف على استراتيجية الامتثال)، الرئيس التنفيذي (المساءلة النهائية)، مدير أمن المعلومات (قيادة ISMS)، مسؤول حماية البيانات (امتثال PDPL)، مدير الامتثال (العمليات اليومية)، المستشار القانوني (تفسير اللوائح)، المدقق الداخلي (تقييمات مستقلة)، رؤساء الأقسام (امتثال الفريق).

**لجنة الامتثال:**
- **الأعضاء**: مدير أمن المعلومات (الرئيس)، DPO، مدير الامتثال، القانوني، المدقق الداخلي، مدير تقنية المعلومات
- **تكرار الاجتماع**: شهريًا
- **المسؤوليات**: مراجعة حالة الامتثال، تقييم المتطلبات التنظيمية الجديدة، الموافقة على مبادرات الامتثال، تصعيد القضايا الحرجة، مراجعة نتائج المراجعة والإجراءات التصحيحية

---

## 4. Compliance Monitoring and Measurement | مراقبة وقياس الامتثال

### English

**Compliance Assessment Methodology:**

1. **Control Mapping** (Quarterly)
   - Map SICO controls to each framework requirement
   - Maintain compliance matrix in SICO GRC Platform
   - Document evidence for each control
   - Gap analysis: identify non-compliant controls

2. **Control Testing** (Continuous)
   - Automated compliance scans (daily)
   - Manual control reviews (quarterly)
   - Sampling methodology for evidence validation
   - Test results documented with evidence

3. **Compliance Scoring**
   - Formula: (Compliant Controls / Total Controls) × 100
   - Target: ≥95% across all frameworks
   - Red flag: <90% triggers management escalation
   - Compliance dashboard updated real-time

**Key Performance Indicators (KPIs):**

| **KPI** | **Target** | **Measurement** | **Frequency** |
|---------|-----------|-----------------|---------------|
| **Overall Compliance Score** | ≥95% | Weighted average across frameworks | Monthly |
| **Critical Control Compliance** | 100% | P0/P1 controls fully implemented | Weekly |
| **Audit Findings (Open)** | <5 | Number of unresolved findings | Weekly |
| **Policy Acknowledgement Rate** | 100% | % of employees acknowledged current policies | Monthly |
| **Training Completion Rate** | 100% | % of employees completed security training | Monthly |
| **Third-Party Compliance** | 100% | % of critical vendors assessed | Quarterly |
| **Incident Response Time** | <1 hour | Average time to respond to incidents | Monthly |
| **Patch Compliance** | 95% | % of systems with current patches | Weekly |

### العربية

**منهجية تقييم الامتثال:**

1. **تعيين الضوابط** (ربع سنوي)
   - تعيين ضوابط سيكو لكل متطلب إطار
   - الحفاظ على مصفوفة الامتثال في منصة SICO GRC
   - توثيق الأدلة لكل ضابط
   - تحليل الفجوات: تحديد الضوابط غير المتوافقة

2. **اختبار الضوابط** (مستمر)
   - فحوصات الامتثال الآلية (يومياً)
   - مراجعات الضوابط اليدوية (ربع سنوي)
   - منهجية أخذ العينات للتحقق من الأدلة
   - توثيق نتائج الاختبار مع الأدلة

3. **تسجيل الامتثال**
   - الصيغة: (الضوابط المتوافقة / إجمالي الضوابط) × 100
   - الهدف: ≥95٪ عبر جميع الأطر
   - علامة حمراء: <90٪ تؤدي إلى تصعيد الإدارة
   - يتم تحديث لوحة معلومات الامتثال في الوقت الفعلي

**مؤشرات الأداء الرئيسية (KPIs):**

تشمل درجة الامتثال الإجمالية (≥95٪)، امتثال الضوابط الحرجة (100٪)، نتائج المراجعة المفتوحة (<5)، معدل الإقرار بالسياسة (100٪)، معدل إكمال التدريب (100٪)، امتثال الطرف الثالث (100٪)، وقت الاستجابة للحوادث (<1 ساعة)، امتثال التصحيح (95٪).

---

## 5. Regulatory Change Management | إدارة التغيير التنظيمي

### English

**Monitoring Process:**

1. **Sources Monitored** (Daily)
   - NCA website and portals
   - SDAIA announcements
   - ISO standard updates
   - Industry publications (cybersecurity, privacy)
   - Legal/regulatory databases

2. **Impact Assessment** (Within 5 days of regulatory change)
   - Compliance Manager reviews new/updated regulations
   - Gap analysis: current state vs. new requirements
   - Impact assessment: systems, processes, policies affected
   - Cost-benefit analysis for implementation options

3. **Implementation Planning** (Within 30 days)
   - Project plan with timeline, resources, responsibilities
   - Policy/procedure updates required
   - Training and awareness activities
   - Technical control implementations
   - Budget approval if needed

4. **Execution and Validation** (Per project plan)
   - Implement required changes
   - Update compliance documentation
   - Staff training and communication
   - Control testing and validation
   - Update compliance matrix

5. **Regulatory Reporting** (As required by regulation)
   - Annual compliance reports to NCA (ECC/CCC)
   - PDPL breach notifications to SDAIA (within 72 hours)
   - ISO certification surveillance audits (annually)
   - Ad-hoc regulatory inquiries (within response deadline)

### العربية

**عملية المراقبة:**

1. **المصادر المراقبة** (يومياً)
   - موقع NCA والبوابات
   - إعلانات SDAIA
   - تحديثات معايير ISO
   - منشورات الصناعة (الأمن السيبراني، الخصوصية)
   - قواعد البيانات القانونية/التنظيمية

2. **تقييم الأثر** (خلال 5 أيام من التغيير التنظيمي)
   - يراجع مدير الامتثال اللوائح الجديدة/المحدثة
   - تحليل الفجوات: الحالة الحالية مقابل المتطلبات الجديدة
   - تقييم الأثر: الأنظمة والعمليات والسياسات المتأثرة
   - تحليل التكلفة والعائد لخيارات التنفيذ

3. **التخطيط للتنفيذ** (خلال 30 يومًا)
   - خطة المشروع مع الجدول الزمني والموارد والمسؤوليات
   - تحديثات السياسة/الإجراء المطلوبة
   - أنشطة التدريب والتوعية
   - تطبيقات الضوابط التقنية
   - الموافقة على الميزانية إذا لزم الأمر

4. **التنفيذ والتحقق** (وفقًا لخطة المشروع)
   - تنفيذ التغييرات المطلوبة
   - تحديث وثائق الامتثال
   - تدريب الموظفين والاتصال
   - اختبار الضوابط والتحقق منها
   - تحديث مصفوفة الامتثال

5. **الإبلاغ التنظيمي** (حسب ما تتطلبه اللوائح)
   - تقارير الامتثال السنوية لـ NCA (ECC/CCC)
   - إشعارات انتهاك PDPL لـ SDAIA (خلال 72 ساعة)
   - عمليات تدقيق المراقبة لشهادة ISO (سنويًا)
   - الاستفسارات التنظيمية المخصصة (خلال الموعد النهائي للاستجابة)

---

## 6. Third-Party Compliance | امتثال الطرف الثالث

### English

**Vendor Due Diligence:**

**Pre-Engagement (Before contracting):**
1. Security questionnaire completion
2. Compliance certifications review (ISO 27001, SOC 2)
3. Data processing agreement (DPA) if handling PII
4. NCA CCC compliance assessment (for cloud providers)
5. Risk rating: Critical, High, Medium, Low
6. Management approval required for Critical/High risk vendors

**Contract Requirements:**
- Compliance with SICO security policies
- Right to audit clause
- Incident notification within 24 hours
- Data protection obligations (PDPL)
- Subcontractor disclosure and approval
- Insurance requirements (cyber liability)
- Termination rights for non-compliance

**Ongoing Monitoring:**
- Annual compliance re-assessment
- Critical vendors: quarterly review
- Continuous monitoring via security ratings services
- Incident tracking and performance reviews
- Contract renewal re-assessment

**Vendor Non-Compliance:**
- Warning letter and corrective action plan
- Escalation to executive team
- Contract suspension or termination
- Data retrieval and secure deletion
- Alternative vendor activation

### العربية

**العناية الواجبة للبائع:**

**ما قبل المشاركة (قبل التعاقد):**
1. إكمال استبيان الأمن
2. مراجعة شهادات الامتثال (ISO 27001، SOC 2)
3. اتفاقية معالجة البيانات (DPA) إذا كانت تتعامل مع PII
4. تقييم امتثال NCA CCC (لمقدمي السحابة)
5. تصنيف المخاطر: حرج، عالي، متوسط، منخفض
6. موافقة الإدارة مطلوبة للبائعين ذوي المخاطر الحرجة/العالية

**متطلبات العقد:**
- الامتثال لسياسات أمن سيكو
- بند الحق في المراجعة
- إشعار الحادثة خلال 24 ساعة
- التزامات حماية البيانات (PDPL)
- الإفصاح عن المقاول من الباطن والموافقة عليه
- متطلبات التأمين (المسؤولية السيبرانية)
- حقوق الإنهاء لعدم الامتثال

**المراقبة المستمرة:**
- إعادة تقييم الامتثال السنوي
- البائعون الحرجون: مراجعة ربع سنوية
- المراقبة المستمرة عبر خدمات تقييم الأمن
- تتبع الحوادث ومراجعات الأداء
- إعادة تقييم تجديد العقد

**عدم امتثال البائع:**
- خطاب تحذير وخطة إجراء تصحيحية
- تصعيد إلى الفريق التنفيذي
- تعليق أو إنهاء العقد
- استرجاع البيانات والحذف الآمن
- تنشيط البائع البديل

---

## 7. Compliance Reporting | الإبلاغ عن الامتثال

### English

**Internal Reporting:**

| **Report** | **Audience** | **Frequency** | **Content** |
|-----------|-------------|--------------|-------------|
| **Compliance Dashboard** | CISO, Compliance Manager | Real-time | Overall score, control status, open findings |
| **Monthly Compliance Report** | Executive Team | Monthly | Compliance scores, KPIs, trend analysis, risks |
| **Quarterly Board Report** | Board of Directors | Quarterly | Executive summary, major initiatives, audit results |
| **Annual Compliance Review** | Board, Executives | Annually | Comprehensive review, strategic recommendations |

**External Reporting:**

| **Report** | **Recipient** | **Frequency** | **Regulation** |
|-----------|--------------|--------------|---------------|
| **NCA ECC Compliance** | National Cybersecurity Authority | Annually | ECC Article 5 |
| **NCA CCC Compliance** | National Cybersecurity Authority | Annually | CCC Article 4 |
| **PDPL Breach Notification** | SDAIA | Within 72 hours (if applicable) | PDPL Article 20 |
| **ISO Surveillance Audit** | Certification Body | Annually | ISO 27001 Clause 9.2 |
| **Customer Compliance Reports** | Enterprise Customers | Quarterly or on-demand | Contractual |

### العربية

**الإبلاغ الداخلي:**

يشمل لوحة معلومات الامتثال (في الوقت الفعلي لمدير أمن المعلومات، مدير الامتثال)، تقرير الامتثال الشهري (للفريق التنفيذي)، تقرير المجلس الربع سنوي (لمجلس الإدارة)، مراجعة الامتثال السنوية (المجلس، التنفيذيين).

**الإبلاغ الخارجي:**

يشمل امتثال NCA ECC (سنويًا إلى الهيئة الوطنية للأمن السيبراني)، امتثال NCA CCC (سنويًا)، إشعار انتهاك PDPL (خلال 72 ساعة إذا كان ذلك ممكنًا إلى SDAIA)، تدقيق المراقبة ISO (سنويًا إلى جهة الشهادات)، تقارير امتثال العملاء (ربع سنوي أو حسب الطلب).

---

## 8. Compliance | الامتثال

### English

| **Framework** | **Control** | **Requirement** |
|---------------|-------------|-----------------|
| ISO 27001 | A.5.31-A.5.36, Clause 4-10 | Legal and contractual requirements, compliance management |
| NCA ECC | ECC-GV-3, ECC-GV-4 | Compliance management and monitoring |
| NCA CCC | CCC-GOV-3 | Compliance with laws and regulations |
| PDPL | Articles 1-42 | All provisions of PDPL |
| NIST CSF 2.0 | GV.PO, GV.OV | Governance and oversight |

### العربية
يدعم ISO 27001 (A.5.31-A.5.36، البند 4-10)، NCA ECC (GV-3، GV-4)، NCA CCC (GOV-3)، PDPL (المواد 1-42)، NIST CSF 2.0 (GV.PO، GV.OV).

---

*Related Policies: POL-CM-002 (Audit), POL-CM-003 (Records Management), POL-IS-001 (Information Security)*
