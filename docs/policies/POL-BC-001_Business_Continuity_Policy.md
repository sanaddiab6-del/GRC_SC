# Business Continuity Policy | سياسة استمرارية الأعمال

## POL-BC-001

---

## Document Control | التحكم في الوثيقة

| **Field** | **English** | **العربية** |
|-----------|-------------|--------------|
| **Policy Number** | POL-BC-001 | رقم السياسة: POL-BC-001 |
| **Version** | 1.0 | الإصدار: 1.0 |
| **Effective Date** | 2026-03-01 | تاريخ السريان: 1 مارس 2026 |

---

## 1. Purpose | الغرض

### English
Ensure SICO can continue critical business operations during and after disruptive events, protecting stakeholders' interests and maintaining service delivery in compliance with ISO 27001 A.5.29-A.5.30 and NCA ECC-BC requirements.

### العربية
ضمان قدرة سيكو على مواصلة العمليات التجارية الحرجة أثناء وبعد الأحداث المعطلة، وحماية مصالح أصحاب المصلحة والحفاظ على تقديم الخدمة بما يتوافق مع ISO 27001 A.5.29-A.5.30 ومتطلبات NCA ECC-BC.

---

## 2. Scope | النطاق

### English

**In Scope:**
- Critical business processes supporting customer-facing services
- IT infrastructure and applications (SICO GRC Platform)
- Data centers (primary and DR site)
- Key personnel and suppliers
- Communication systems

**Business Continuity Objectives:**

| **Metric** | **Target** | **Definition** |
|------------|-----------|----------------|
| **RTO** (Recovery Time Objective) | 4 hours | Maximum acceptable downtime |
| **RPO** (Recovery Point Objective) | 1 hour | Maximum acceptable data loss |
| **MTD** (Maximum Tolerable Downtime) | 24 hours | Point of unacceptable business impact |

### العربية

**في النطاق:**
- العمليات التجارية الحرجة التي تدعم الخدمات المواجهة للعملاء
- البنية التحتية لتقنية المعلومات والتطبيقات (منصة SICO GRC)
- مراكز البيانات (الموقع الأساسي وموقع DR)
- الموظفون والموردون الرئيسيون
- أنظمة الاتصالات

**أهداف استمرارية الأعمال:**

| **المقياس** | **الهدف** | **التعريف** |
|-------------|----------|-------------|
| **RTO** (هدف وقت الاسترداد) | 4 ساعات | الوقت الأقصى المقبول للتعطل |
| **RPO** (هدف نقطة الاسترداد) | 1 ساعة | الحد الأقصى المقبول لفقدان البيانات |
| **MTD** (الوقت الأقصى المسموح به للتعطل) | 24 ساعة | نقطة التأثير التجاري غير المقبول |

---

## 3. Business Impact Analysis (BIA) | تحليل أثر الأعمال

### English

**Critical Business Processes:**

| **Process** | **Impact if Unavailable** | **RTO** | **RPO** | **Priority** |
|------------|---------------------------|---------|---------|--------------|
| SICO GRC Platform (customer access) | Revenue loss, SLA breach, reputational damage | 4 hours | 1 hour | 1 (Critical) |
| Compliance reporting | Regulatory penalties, audit failure | 8 hours | 4 hours | 2 (High) |
| Customer support | Customer dissatisfaction, contract breach | 8 hours | N/A | 2 (High) |
| Email and communications | Operational delays, coordination issues | 12 hours | 4 hours | 3 (Medium) |
| Payroll and HR systems | Employee dissatisfaction, legal compliance | 3 days | 24 hours | 4 (Low) |

**Risk Scenarios:**

1. **Natural Disasters**: Earthquake, flood, fire at primary data center
2. **Cyber Attacks**: Ransomware, DDoS, data breach causing system shutdown
3. **Infrastructure Failures**: Power outage, network failure, hardware failure
4. **Pandemics**: Staff unavailability, office closure
5. **Supplier Failures**: Cloud provider outage, critical vendor bankruptcy

### العربية

**العمليات التجارية الحرجة:**

تشمل منصة SICO GRC (وصول العملاء) بأولوية حرجة (RTO: 4 ساعات، RPO: 1 ساعة)، التقارير الامتثالية (RTO: 8 ساعات)، دعم العملاء (RTO: 8 ساعات)، البريد الإلكتروني والاتصالات (RTO: 12 ساعة)، الرواتب وأنظمة الموارد البشرية (RTO: 3 أيام).

**سيناريوهات المخاطر:**

الكوارث الطبيعية، الهجمات السيبرانية، فشل البنية التحتية، الأوبئة، فشل الموردين.

---

## 4. Business Continuity Strategies | استراتيجيات استمرارية الأعمال

### English

**Technology Resilience:**

1. **High Availability Architecture**
   - Active-active configuration across availability zones
   - Load balancing with automatic failover
   - Database replication (synchronous to DR site)
   - 99.9% uptime SLA

2. **Disaster Recovery Site**
   - Secondary data center in different city (>200km from primary)
   - Hot standby with continuous replication
   - Failover time: <2 hours (automated)
   - Monthly DR testing

3. **Backup Strategy**
   - Hourly incremental backups (RPO: 1 hour)
   - Daily full backups (retained 30 days)
   - Weekly backups (retained 1 year)
   - Offsite backup storage (cloud + tape)
   - Backup encryption (AES-256)
   - Monthly restore tests

**People Resilience:**

1. **Work from Home Capability**
   - VPN access for all staff
   - Cloud-based collaboration tools (Microsoft 365)
   - Laptops and mobile devices for all employees
   - Remote work policy and emergency authorization

2. **Cross-Training**
   - Key roles have designated backups
   - Competency matrix maintained
   - Quarterly knowledge transfer sessions

3. **Crisis Management Team**
   - CEO, COO, CISO, Legal, HR, Communications
   - Defined roles and contact tree
   - Emergency communication plan

**Supplier Resilience:**

1. **Critical Vendor Assessment**
   - Annual BCP capability review
   - SLA requirements for backup and recovery
   - Alternative suppliers identified

2. **Cloud Provider Resilience**
   - Multi-region deployment (primary: Riyadh, DR: Jeddah)
   - Azure/AWS SLA: 99.99% uptime
   - Contractual failover commitments

### العربية

**مرونة التكنولوجيا:**

1. **بنية عالية التوافر**
   - تكوين نشط-نشط عبر مناطق التوافر
   - موازنة الحمل مع التبديل التلقائي
   - نسخ قاعدة البيانات المتماثل (متزامن إلى موقع DR)
   - 99.9٪ وقت التشغيل SLA

2. **موقع التعافي من الكوارث**
   - مركز بيانات ثانوي في مدينة مختلفة (>200 كم من الأساسي)
   - الاستعداد الساخن مع النسخ المستمر
   - وقت التبديل: <2 ساعات (تلقائي)
   - اختبار DR شهري

3. **استراتيجية النسخ الاحتياطي**
   - نسخ احتياطية تزايدية ساعية (RPO: 1 ساعة)
   - نسخ احتياطية كاملة يومية (الاحتفاظ بها لمدة 30 يومًا)
   - نسخ احتياطية أسبوعية (الاحتفاظ بها لمدة سنة)
   - تخزين النسخ الاحتياطي خارج الموقع (السحابة + الشريط)
   - تشفير النسخ الاحتياطي (AES-256)
   - اختبارات الاستعادة الشهرية

**مرونة الأشخاص:**

العمل من المنزل (VPN للجميع)، التدريب المتقاطع (احتياطيات للأدوار الرئيسية)، فريق إدارة الأزمات (الرئيس التنفيذي، COO، CISO، القانوني، الموارد البشرية، الاتصالات).

**مرونة الموردين:**

تقييم البائعين الحرجة، مرونة مزود السحابة (نشر متعدد المناطق: الرياض الأساسي، جدة DR).

---

## 5. Disaster Recovery Plan (DRP) | خطة التعافي من الكوارث

### English

**DR Activation Criteria:**
- Primary data center unavailable >2 hours
- Catastrophic event (fire, natural disaster)
- Cyber attack rendering primary site unusable
- Management decision based on threat assessment

**DR Procedures:**

**Phase 1: Activation (0-30 minutes)**
1. Declare disaster by Crisis Management Team
2. Notify all stakeholders via emergency contact tree
3. Initiate failover to DR site (automated)
4. Verify DR site systems operational

**Phase 2: Operations (30 minutes - recovery complete)**
1. All traffic routed to DR site
2. Continuous monitoring for stability
3. Customer communication (status page, email)
4. Log all actions and decisions

**Phase 3: Failback (When primary site restored)**
1. Verify primary site fully operational
2. Sync data from DR to primary
3. Schedule maintenance window for failback
4. Reverse DNS and routing to primary
5. Post-recovery validation

**DR Testing Schedule:**
- **Monthly**: Backup restoration test (sample data)
- **Quarterly**: Application-level failover test (non-production)
- **Annually**: Full DR exercise with simulated disaster scenario
- Test reports reviewed by executive team

### العربية

**معايير تفعيل DR:**
- مركز البيانات الأساسي غير متاح >2 ساعات
- حدث كارثي (حريق، كارثة طبيعية)
- هجوم سيبراني يجعل الموقع الأساسي غير قابل للاستخدام
- قرار الإدارة بناءً على تقييم التهديد

**إجراءات DR:**

**المرحلة 1: التفعيل (0-30 دقيقة)**
1. إعلان الكارثة من قبل فريق إدارة الأزمات
2. إخطار جميع أصحاب المصلحة عبر شجرة الاتصال الطارئة
3. بدء التبديل إلى موقع DR (تلقائي)
4. التحقق من تشغيل أنظمة موقع DR

**المرحلة 2: العمليات (30 دقيقة - الاسترداد الكامل)**
1. يتم توجيه جميع حركة المرور إلى موقع DR
2. المراقبة المستمرة للاستقرار
3. اتصالات العملاء (صفحة الحالة، البريد الإلكتروني)
4. تسجيل جميع الإجراءات والقرارات

**المرحلة 3: العودة (عند استعادة الموقع الأساسي)**
1. التحقق من تشغيل الموقع الأساسي بالكامل
2. مزامنة البيانات من DR إلى الأساسي
3. جدولة نافذة الصيانة للعودة
4. عكس DNS والتوجيه إلى الأساسي
5. التحقق بعد الاسترداد

**جدول اختبار DR:**
- **شهريًا**: اختبار استعادة النسخ الاحتياطي (بيانات عينة)
- **ربع سنوي**: اختبار التبديل على مستوى التطبيق (غير الإنتاج)
- **سنويًا**: تمرين DR كامل مع سيناريو كارثة محاكاة
- تتم مراجعة تقارير الاختبار من قبل الفريق التنفيذي

---

## 6. Communication Plan | خطة الاتصال

### English

**Internal Communication:**
- Emergency contact tree (phone, SMS, email)
- Microsoft Teams for coordination
- Status updates every 2 hours during incident
- All-hands meeting when normal operations resume

**External Communication:**

| **Stakeholder** | **Method** | **Timing** | **Responsible** |
|----------------|-----------|-----------|-----------------|
| Customers | Status page, email, in-app notification | Within 1 hour of disruption | Customer Success |
| Regulators (SDAIA, NCA) | Official notification via portal | If required by incident type | Legal/DPO |
| Media | Press release (if public interest) | As approved by CEO | Communications |
| Partners/Suppliers | Email, phone | Within 4 hours | Procurement |
| Board of Directors | Executive briefing | Within 24 hours | CEO |

### العربية

**الاتصال الداخلي:**
- شجرة الاتصال الطارئة (الهاتف، الرسائل النصية، البريد الإلكتروني)
- Microsoft Teams للتنسيق
- تحديثات الحالة كل ساعتين أثناء الحادثة
- اجتماع شامل عند استئناف العمليات العادية

**الاتصال الخارجي:**

يشمل العملاء (صفحة الحالة، البريد الإلكتروني، إشعار داخل التطبيق)، الجهات التنظيمية (الإخطار الرسمي عبر البوابة)، وسائل الإعلام (بيان صحفي)، الشركاء/الموردين (البريد الإلكتروني، الهاتف)، مجلس الإدارة (إحاطة تنفيذية).

---

## 7. Compliance | الامتثال

### English

| **Framework** | **Control** | **Requirement** |
|---------------|-------------|-----------------|
| ISO 27001 | A.5.29, A.5.30 | Business continuity and ICT readiness |
| NCA ECC | ECC-BC-1 through ECC-BC-5 | Business continuity planning |
| NCA CCC | CCC-BCM-1 through CCC-BCM-4 | Business continuity management |
| NIST CSF 2.0 | RC.RP, RC.IM, RC.CO | Recover function |

### العربية
يدعم ISO 27001 (A.5.29-A.5.30)، NCA ECC (BC-1 إلى BC-5)، NCA CCC (BCM-1 إلى BCM-4)، NIST CSF 2.0 (RC.RP-RC.CO).

---

*Related Policies: POL-BC-002 (Disaster Recovery), POL-IM-001 (Incident Response), POL-OP-002 (Backup Management)*
