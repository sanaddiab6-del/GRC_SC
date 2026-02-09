# Audit Policy | سياسة المراجعة

## POL-CM-002

---

## Document Control | التحكم في الوثيقة

| **Field** | **English** | **العربية** |
|-----------|-------------|--------------|
| **Policy Number** | POL-CM-002 | رقم السياسة: POL-CM-002 |
| **Version** | 1.0 | الإصدار: 1.0 |
| **Effective Date** | 2026-03-01 | تاريخ السريان: 1 مارس 2026 |

---

## 1. Purpose | الغرض

### English
Establish requirements for internal and external audits of SICO's Information Security Management System (ISMS), ensuring compliance with ISO 27001 Clause 9.2 and providing independent assurance to management and stakeholders.

### العربية
وضع متطلبات للمراجعات الداخلية والخارجية لنظام إدارة أمن المعلومات (ISMS) الخاص بسيكو، وضمان الامتثال لـ ISO 27001 البند 9.2 وتوفير ضمان مستقل للإدارة وأصحاب المصلحة.

---

## 2. Scope | النطاق

### English

**Audit Types:**

| **Audit Type** | **Scope** | **Auditor** | **Frequency** |
|---------------|-----------|------------|---------------|
| **Internal Audit** | Full ISMS (ISO 27001, NCA ECC, CCC, PDPL) | Internal Audit Team | Annually |
| **External Certification Audit** | ISO 27001:2022 + ISO 27017/27018/27701 | Accredited Certification Body | Initial + Annual Surveillance |
| **Regulatory Audit** | NCA ECC, NCA CCC, PDPL compliance | Regulatory Authority (NCA/SDAIA) | As required |
| **Customer Audit** | Contractual security requirements | Customer audit team | Per contract (typically annual) |
| **Third-Party Risk Audit** | Vendor security assessment | SICO Security Team | Annual (critical vendors) |
| **SOC 2 Type II** | Service Organization Controls | Independent CPA Firm | Annual |

**ISMS Scope for Certification:**
- **Systems**: SICO GRC Platform (frontend, backend, AI/RAG engine, databases)
- **Infrastructure**: Azure cloud environment (Riyadh primary, Jeddah DR)
- **Locations**: Riyadh headquarters + remote workforce
- **Processes**: All ISMS processes (risk management, incident response, access control, etc.)
- **Exclusions**: (None - full scope certification)

### العربية

**أنواع المراجعة:**

تشمل المراجعة الداخلية (ISMS الكامل، سنويًا، فريق المراجعة الداخلي)، مراجعة الشهادات الخارجية (ISO 27001:2022، سنويًا، جهة التصديق المعتمدة)، المراجعة التنظيمية (NCA ECC/CCC، PDPL، حسب الحاجة، السلطة التنظيمية)، مراجعة العملاء (متطلبات الأمن التعاقدية، سنويًا عادةً، فريق مراجعة العملاء)، مراجعة مخاطر الطرف الثالث (تقييم أمن البائع، سنويًا، فريق أمن سيكو)، SOC 2 Type II (ضوابط منظمة الخدمة، سنويًا، شركة CPA مستقلة).

**نطاق ISMS للشهادة:**
- **الأنظمة**: منصة SICO GRC (الواجهة الأمامية، الخلفية، محرك AI/RAG، قواعد البيانات)
- **البنية التحتية**: بيئة السحابة Azure (الرياض الأساسي، جدة DR)
- **المواقع**: مقر الرياض + القوى العاملة عن بُعد
- **العمليات**: جميع عمليات ISMS (إدارة المخاطر، الاستجابة للحوادث، التحكم في الوصول، إلخ.)
- **الاستثناءات**: (لا شيء - شهادة النطاق الكامل)

---

## 3. Internal Audit Program | برنامج المراجعة الداخلية

### English

**Annual Audit Plan:**

**Q1 (Jan-Mar):**
- Audit area: Risk Management, Governance (ISO 27001 Clauses 4, 5, 6)
- Controls: Risk assessment, ISMS scope, management commitment
- Deliverable: Q1 audit report

**Q2 (Apr-Jun):**
- Audit area: Support and Operation (ISO 27001 Clauses 7, 8)
- Controls: Resource management, awareness/training, operational controls
- Deliverable: Q2 audit report

**Q3 (Jul-Sep):**
- Audit area: Performance Evaluation (ISO 27001 Clause 9)
- Controls: Monitoring, measurement, internal audit, management review
- Deliverable: Q3 audit report

**Q4 (Oct-Dec):**
- Audit area: Improvement + Full Annex A Controls (ISO 27001 Clause 10 + A.5-A.8)
- Controls: Nonconformity, corrective action, all 93 Annex A controls
- Deliverable: Q4 audit report + Annual audit summary

**Audit Methodology:**

1. **Planning (4 weeks before audit)**
   - Define audit scope and objectives
   - Select audit team (min 2 auditors, independent from auditee department)
   - Develop audit checklist based on control requirements
   - Schedule audit with department heads
   - Request documentation in advance

2. **Opening Meeting (Day 1)**
   - Introductions and audit objectives
   - Confirm scope and schedule
   - Explain audit process
   - Address questions

3. **Fieldwork (1-2 weeks)**
   - **Document Review**: Policies, procedures, evidence artifacts
   - **Interviews**: Staff at all levels (exec, management, operational)
   - **Observations**: Physical security, workstations, data center
   - **Testing**: Sample transactions, log reviews, config checks
   - **Evidence Collection**: Screenshots, reports, signed documents

4. **Findings Classification**
   - **Major Nonconformity**: Critical control missing or ineffective, high risk
   - **Minor Nonconformity**: Control partially implemented or single lapse
   - **Observation**: Potential improvement area, not yet non-compliant
   - **Best Practice**: Positive noteworthy practice

5. **Closing Meeting (Last day)**
   - Present findings to auditee management
   - Discuss root causes
   - Agree on corrective actions and timelines
   - Final questions and clarifications

6. **Audit Report (Within 2 weeks)**
   - Executive summary
   - Audit scope and methodology
   - Detailed findings with evidence
   - Recommendations
   - Management response and corrective action plan (CAP)

### العربية

**الخطة السنوية للمراجعة:**

**الربع الأول (يناير-مارس):**
- منطقة المراجعة: إدارة المخاطر، الحوكمة (ISO 27001 البنود 4، 5، 6)
- الضوابط: تقييم المخاطر، نطاق ISMS، التزام الإدارة
- التسليم: تقرير مراجعة الربع الأول

**الربع الثاني (أبريل-يونيو):**
- منطقة المراجعة: الدعم والتشغيل (ISO 27001 البنود 7، 8)
- الضوابط: إدارة الموارد، التوعية/التدريب، الضوابط التشغيلية
- التسليم: تقرير مراجعة الربع الثاني

**الربع الثالث (يوليو-سبتمبر):**
- منطقة المراجعة: تقييم الأداء (ISO 27001 البند 9)
- الضوابط: المراقبة، القياس، المراجعة الداخلية، مراجعة الإدارة
- التسليم: تقرير مراجعة الربع الثالث

**الربع الرابع (أكتوبر-ديسمبر):**
- منطقة المراجعة: التحسين + جميع ضوابط الملحق أ (ISO 27001 البند 10 + A.5-A.8)
- الضوابط: عدم المطابقة، الإجراء التصحيحي، جميع 93 ضوابط الملحق أ
- التسليم: تقرير مراجعة الربع الرابع + ملخص المراجعة السنوي

**منهجية المراجعة:**

1. **التخطيط** (4 أسابيع قبل المراجعة)
2. **الاجتماع الافتتاحي** (اليوم الأول)
3. **العمل الميداني** (1-2 أسابيع)
4. **تصنيف النتائج**
5. **الاجتماع الختامي** (اليوم الأخير)
6. **تقرير المراجعة** (خلال أسبوعين)

---

## 4. External Certification Audits | مراجعات الشهادات الخارجية

### English

**ISO 27001 Certification Process:**

**Stage 1 Audit (Document Review):**
- **Timing**: 3 months before Stage 2
- **Duration**: 2 days
- **Focus**: ISMS documentation completeness
  - Policies and procedures
  - Risk assessment and treatment plan
  - Statement of Applicability (SOA)
  - Internal audit and management review evidence
  - ISMS Manual
- **Outcome**: Gaps identified, corrective actions required before Stage 2

**Stage 2 Audit (Implementation Review):**
- **Timing**: After Stage 1 gaps resolved
- **Duration**: 3-5 days (depends on organization size)
- **Focus**: Control implementation effectiveness
  - Interview staff (20+ people)
  - Observe operations
  - Test controls (sampling)
  - Verify evidence for all 93 Annex A controls
- **Outcome**: 
  - **Certification Granted**: Zero major NCs, <5 minor NCs
  - **Conditional Certification**: Minor NCs must be resolved within 90 days
  - **Certification Denied**: Major NCs present, re-audit required

**Surveillance Audits (Annual):**
- **Duration**: 1-2 days
- **Focus**: Sample of ISMS controls (typically 30-40%)
- **Rotation**: Different controls each year to cover full ISMS over 3 years
- **Requirements**: 
  - Internal audit completed within 12 months
  - Management review completed within 12 months
  - No major nonconformities open
  - Evidence of continual improvement

**Recertification Audit (Every 3 years):**
- **Duration**: Similar to Stage 2 (3-5 days)
- **Focus**: Full ISMS re-assessment
- **Requirements**: Same as initial certification

**Certification Body Selection:**
- Accredited by IAF (International Accreditation Forum) member
- Recognized in Saudi Arabia
- Experience with cloud/SaaS companies
- Arabic-speaking auditors (preferred)
- Competitive pricing
- Shortlist: BSI, DNV, SGS, Bureau Veritas, LRQA

### العربية

**عملية شهادة ISO 27001:**

**مراجعة المرحلة الأولى (مراجعة الوثائق):**
- **التوقيت**: 3 أشهر قبل المرحلة الثانية
- **المدة**: يومان
- **التركيز**: اكتمال وثائق ISMS (السياسات، الإجراءات، تقييم المخاطر، SOA، المراجعة الداخلية، دليل ISMS)
- **النتيجة**: تحديد الفجوات، الإجراءات التصحيحية المطلوبة قبل المرحلة الثانية

**مراجعة المرحلة الثانية (مراجعة التنفيذ):**
- **التوقيت**: بعد حل فجوات المرحلة الأولى
- **المدة**: 3-5 أيام
- **التركيز**: فعالية تنفيذ الضوابط (مقابلة الموظفين، مراقبة العمليات، اختبار الضوابط، التحقق من الأدلة لجميع 93 ضابط الملحق أ)
- **النتيجة**: منح الشهادة (صفر NCs رئيسية، <5 NCs ثانوية)، شهادة مشروطة (يجب حل NCs الثانوية خلال 90 يومًا)، رفض الشهادة (NCs رئيسية موجودة)

**مراجعات المراقبة (سنوية):**
- **المدة**: 1-2 يوم
- **التركيز**: عينة من ضوابط ISMS (عادة 30-40٪)
- **التناوب**: ضوابط مختلفة كل عام لتغطية ISMS الكامل على مدى 3 سنوات
- **المتطلبات**: إكمال المراجعة الداخلية خلال 12 شهرًا، مراجعة الإدارة خلال 12 شهرًا، لا NCs رئيسية مفتوحة، دليل على التحسين المستمر

**مراجعة إعادة الشهادة (كل 3 سنوات):**
- **المدة**: مشابهة للمرحلة الثانية (3-5 أيام)
- **التركيز**: إعادة تقييم ISMS الكامل

**اختيار جهة الشهادات:**
معتمدة من قبل عضو IAF، معترف بها في المملكة العربية السعودية، خبرة في شركات السحابة/SaaS، مدققون ناطقون بالعربية (مفضل)، أسعار تنافسية، القائمة المختصرة: BSI، DNV، SGS، Bureau Veritas، LRQA.

---

## 5. Auditee Responsibilities | مسؤوليات المدقق عليه

### English

**Before Audit:**
✅ Provide requested documentation in advance  
✅ Ensure staff availability for interviews  
✅ Prepare evidence artifacts (logs, reports, approvals)  
✅ Arrange physical access (office, data center if needed)  
✅ Assign audit liaison from department  

**During Audit:**
✅ Respond to auditor questions honestly and completely  
✅ Provide additional evidence as requested  
✅ Do NOT hide or misrepresent information  
✅ Take notes of findings and recommendations  

**After Audit:**
✅ Review audit report for factual accuracy  
✅ Develop corrective action plan (CAP) for findings  
✅ Implement corrective actions within agreed timeline  
✅ Submit evidence of remediation to Internal Audit  
✅ Follow up on observations for continuous improvement  

**Prohibited Actions:**
❌ Refusing to cooperate with auditors  
❌ Providing false or misleading information  
❌ Withholding evidence  
❌ Retaliating against audit team  
❌ Ignoring audit findings  

### العربية

**قبل المراجعة:**
✅ تقديم الوثائق المطلوبة مسبقًا  
✅ ضمان توفر الموظفين للمقابلات  
✅ إعداد أدلة الأدلة (السجلات، التقارير، الموافقات)  
✅ ترتيب الوصول المادي (المكتب، مركز البيانات إذا لزم الأمر)  
✅ تعيين منسق المراجعة من القسم  

**أثناء المراجعة:**
✅ الرد على أسئلة المدقق بصدق وبشكل كامل  
✅ تقديم أدلة إضافية حسب الطلب  
✅ لا تخفي أو تشوه المعلومات  
✅ تدوين النتائج والتوصيات  

**بعد المراجعة:**
✅ مراجعة تقرير المراجعة للدقة الواقعية  
✅ تطوير خطة إجراء تصحيحية (CAP) للنتائج  
✅ تنفيذ الإجراءات التصحيحية خلال الجدول الزمني المتفق عليه  
✅ تقديم دليل على المعالجة إلى المراجعة الداخلية  
✅ متابعة الملاحظات للتحسين المستمر  

**الإجراءات الممنوعة:**
❌ رفض التعاون مع المدققين  
❌ تقديم معلومات كاذبة أو مضللة  
❌ حجب الأدلة  
❌ الانتقام من فريق المراجعة  
❌ تجاهل نتائج المراجعة  

---

## 6. Corrective Action Process | عملية الإجراء التصحيحي

### English

**Corrective Action Plan (CAP) Requirements:**

**For Each Finding:**
1. **Root Cause Analysis**
   - Why did the nonconformity occur?
   - Contributing factors (process, technology, people, policy)
   - 5 Whys technique or fishbone diagram

2. **Corrective Actions**
   - Specific actions to address root cause (not just symptoms)
   - Responsible person assigned
   - Target completion date (within 90 days for external audit findings)
   - Resources required

3. **Preventive Measures**
   - How to prevent recurrence?
   - Process improvements, training, additional controls

4. **Verification**
   - How will effectiveness be verified?
   - Evidence required (e.g., updated policy, training completion, test results)

**Tracking:**
- All findings logged in SICO GRC Platform
- Status dashboard: Open, In Progress, Pending Verification, Closed
- Weekly status reviews by Compliance Manager
- Overdue findings escalated to CISO

**Verification:**
- Internal Audit verifies corrective actions before closing
- For external audit findings: Certification body verifies during next surveillance
- Evidence retained for 7 years

### العربية

**متطلبات خطة الإجراء التصحيحي (CAP):**

**لكل نتيجة:**
1. **تحليل السبب الجذري**
   - لماذا حدث عدم المطابقة؟
   - العوامل المساهمة (العملية، التكنولوجيا، الأشخاص، السياسة)
   - تقنية 5 لماذا أو مخطط عظم السمكة

2. **الإجراءات التصحيحية**
   - إجراءات محددة لمعالجة السبب الجذري (وليس فقط الأعراض)
   - الشخص المسؤول المعين
   - تاريخ الإنجاز المستهدف (خلال 90 يومًا لنتائج المراجعة الخارجية)
   - الموارد المطلوبة

3. **التدابير الوقائية**
   - كيفية منع التكرار؟
   - تحسينات العملية، التدريب، الضوابط الإضافية

4. **التحقق**
   - كيف سيتم التحقق من الفعالية؟
   - الأدلة المطلوبة (مثل السياسة المحدثة، إكمال التدريب، نتائج الاختبار)

**التتبع:**
- يتم تسجيل جميع النتائج في منصة SICO GRC
- لوحة معلومات الحالة: مفتوح، قيد التنفيذ، في انتظار التحقق، مغلق
- مراجعات الحالة الأسبوعية من قبل مدير الامتثال
- يتم تصعيد النتائج المتأخرة إلى مدير أمن المعلومات

**التحقق:**
- تتحقق المراجعة الداخلية من الإجراءات التصحيحية قبل الإغلاق
- لنتائج المراجعة الخارجية: تتحقق جهة الشهادات أثناء المراقبة التالية
- الاحتفاظ بالأدلة لمدة 7 سنوات

---

## 7. Management Review | مراجعة الإدارة

### English

**Frequency**: At least annually (typically Q4)

**Participants:**
- CEO (Chair)
- Executive team (COO, CFO, CISO, DPO)
- Compliance Manager
- Internal Audit Lead
- Legal Counsel

**Agenda Items (ISO 27001 Clause 9.3):**

1. **Status of actions from previous management reviews**
2. **Changes in external/internal issues affecting ISMS**
3. **Feedback on information security performance:**
   - Compliance scores and trends
   - Incident statistics
   - Audit findings and corrective actions
4. **Feedback from stakeholders** (customers, regulators, employees)
5. **Results of risk assessment and status of risk treatment plan**
6. **Opportunities for continual improvement**
7. **Need for changes to ISMS** (policies, objectives, resources)

**Outputs (Documented):**
- Decisions related to continual improvement opportunities
- Decisions related to ISMS changes
- Resource allocation decisions
- Actions assigned with owners and deadlines

**Follow-Up:**
- Management review minutes distributed within 1 week
- Actions tracked in SICO GRC Platform
- Progress reviewed in next management review

### العربية

**التكرار**: مرة واحدة على الأقل سنويًا (عادة الربع الرابع)

**المشاركون:**
- الرئيس التنفيذي (الرئيس)
- الفريق التنفيذي (COO، CFO، CISO، DPO)
- مدير الامتثال
- قائد المراجعة الداخلية
- المستشار القانوني

**بنود جدول الأعمال (ISO 27001 البند 9.3):**

1. **حالة الإجراءات من مراجعات الإدارة السابقة**
2. **التغييرات في القضايا الخارجية/الداخلية التي تؤثر على ISMS**
3. **التغذية الراجعة حول أداء أمن المعلومات:**
   - درجات الامتثال والاتجاهات
   - إحصائيات الحوادث
   - نتائج المراجعة والإجراءات التصحيحية
4. **التغذية الراجعة من أصحاب المصلحة** (العملاء، الجهات التنظيمية، الموظفون)
5. **نتائج تقييم المخاطر وحالة خطة معالجة المخاطر**
6. **فرص التحسينالمستمر**
7. **الحاجة إلى التغييرات في ISMS** (السياسات، الأهداف، الموارد)

**المخرجات (الموثقة):**
- القرارات المتعلقة بفرص التحسين المستمر
- القرارات المتعلقة بتغييرات ISMS
- قرارات تخصيص الموارد
- الإجراءات المعينة مع المالكين والمواعيد النهائية

**المتابعة:**
- يتم توزيع محاضر مراجعة الإدارة خلال أسبوع واحد
- يتم تتبع الإجراءات في منصة SICO GRC
- تتم مراجعة التقدم في مراجعة الإدارة التالية

---

## 8. Compliance | الامتثال

### English

| **Framework** | **Control** | **Requirement** |
|---------------|-------------|-----------------|
| ISO 27001 | Clause 9.2 | Internal audit program |
| ISO 27001 | Clause 9.3 | Management review |
| ISO 27001 | Clause 10.1 | Nonconformity and corrective action |
| NCA ECC | ECC-GV-4 | Compliance assessment and monitoring |
| NIST CSF 2.0 | GV.OV | Organizational oversight |

### العربية
يدعم ISO 27001 (البند 9.2 برنامج المراجعة الداخلية، البند 9.3 مراجعة الإدارة، البند 10.1 عدم المطابقة والإجراء التصحيحي)، NCA ECC (GV-4 تقييم الامتثال والمراقبة)، NIST CSF 2.0 (GV.OV الإشراف التنظيمي).

---

*Related Policies: POL-CM-001 (Compliance Management), POL-CM-003 (Records Management), POL-IS-001 (Information Security)*
