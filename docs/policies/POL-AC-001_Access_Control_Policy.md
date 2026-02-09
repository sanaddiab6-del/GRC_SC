# Access Control Policy | سياسة التحكم في الوصول

## POL-AC-001

---

## Document Control | التحكم في الوثيقة

| **Field** | **English** | **العربية** |
|-----------|-------------|--------------|
| **Policy Number** | POL-AC-001 | رقم السياسة: POL-AC-001 |
| **Version** | 1.0 | الإصدار: 1.0 |
| **Effective Date** | 2026-03-01 | تاريخ السريان: 1 مارس 2026 |
| **Review Date** | 2027-03-01 | تاريخ المراجعة: 1 مارس 2027 |
| **Policy Owner** | CISO | مالك السياسة: مدير أمن المعلومات |
| **Approval Authority** | CEO | سلطة الاعتماد: الرئيس التنفيذي |

---

## 1. Purpose | الغرض

### English
This Access Control Policy establishes requirements for granting, managing, reviewing, and revoking access to SICO's information systems and data. The policy ensures that only authorized personnel have appropriate access based on business need, implementing least privilege and segregation of duties principles.

### العربية
تضع سياسة التحكم في الوصول هذه المتطلبات لمنح وإدارة ومراجعة وإلغاء الوصول إلى أنظمة المعلومات والبيانات الخاصة بسيكو. تضمن السياسة أن الموظفين المصرح لهم فقط لديهم وصول مناسب بناءً على احتياجات العمل، مع تطبيق مبادئ الحد الأدنى من الصلاحيات والفصل بين الواجبات.

---

## 2. Scope | النطاق

### English
Applies to all access to:
- Information systems (on-premise and cloud)
- Applications and databases
- Network resources
- Physical facilities
- Customer data and corporate information

Covers all users: employees, contractors, third parties, administrators.

### العربية
ينطبق على جميع الوصول إلى:
- أنظمة المعلومات (محلية وسحابية)
- التطبيقات وقواعد البيانات
- موارد الشبكة
- المرافق المادية
- بيانات العملاء ومعلومات الشركة

يشمل جميع المستخدمين: الموظفين، المقاولين، الأطراف الثالثة، المسؤولين.

---

## 3. Policy Statement | بيان السياسة

### English

**Access Control Principles:**

1. **Least Privilege**: Users granted minimum access required for job functions
2. **Need to Know**: Access based on business justification only
3. **Segregation of Duties**: Conflicting roles separated to prevent fraud
4. **Defense in Depth**: Multiple layers of access controls
5. **Regular Reviews**: Quarterly access reviews by data owners

**Access Requirements:**

✅ **Authentication**: Multi-factor authentication (MFA) required for all systems  
✅ **Authorization**: Role-based access control (RBAC) implemented  
✅ **Provisioning**: Formal approval workflow via ticketing system  
✅ **Review**: Quarterly access certification by managers  
✅ **Revocation**: Immediate revocation upon termination  

### العربية

**مبادئ التحكم في الوصول:**

1. **الحد الأدنى من الصلاحيات**: منح المستخدمين الحد الأدنى من الوصول المطلوب للوظائف
2. **الحاجة إلى المعرفة**: الوصول بناءً على المبرر التجاري فقط
3. **الفصل بين الواجبات**: فصل الأدوار المتعارضة لمنع الاحتيال
4. **الدفاع المتعمق**: طبقات متعددة من ضوابط الوصول
5. **المراجعات المنتظمة**: مراجعات الوصول الربع سنوية من قبل مالكي البيانات

**متطلبات الوصول:**

✅ **المصادقة**: مصادقة متعددة العوامل (MFA) مطلوبة لجميع الأنظمة  
✅ **التفويض**: تطبيق التحكم في الوصول على أساس الدور (RBAC)  
✅ **التوفير**: سير عمل الموافقة الرسمي عبر نظام التذاكر  
✅ **المراجعة**: اعتماد الوصول الربع سنوي من قبل المديرين  
✅ **الإلغاء**: الإلغاء الفوري عند الإنهاء  

---

## 4. Compliance | الامتثال

### English

**Framework Mappings:**

| **Framework** | **Control ID** | **Description** |
|---------------|----------------|-----------------|
| ISO 27001 | A.5.15, A.5.16, A.5.18, A.8.2, A.8.3 | Access control policy and procedures |
| NCA ECC | ECC-AC-1 through ECC-AC-8 | Access control domain |
| NCA CCC | CCC-IAM-1 through CCC-IAM-7 | Identity and access management |
| PDPL | Article 6 | Access to personal data |
| NIST CSF 2.0 | PR.AC | Identity management and access control |

### العربية

**تعيينات الأطر:**

يدعم ISO 27001 (A.5.15-A.5.18، A.8.2-A.8.3)، NCA ECC (AC-1 إلى AC-8)، NCA CCC (IAM-1 إلى IAM-7)، PDPL (المادة 6)، NIST CSF 2.0 (PR.AC).

---

## 5. Access Provisioning Process | عملية توفير الوصول

### English

**Step 1: Request**
- User submits access request via ServiceNow ticketing system
- Business justification required
- Manager approval required

**Step 2: Approval**
- Line manager reviews and approves
- Data owner approves for sensitive data access
- Security team reviews for compliance

**Step 3: Provisioning**
- IT provisions access within 24 hours
- User receives credentials securely
- Access logged in Identity Management System

**Step 4: Verification**
- IT verifies access granted correctly
- User confirms access working
- Ticket closed with documentation

### العربية

**الخطوة 1: الطلب**
- يقدم المستخدم طلب الوصول عبر نظام التذاكر
- مطلوب مبرر تجاري
- مطلوب موافقة المدير

**الخطوة 2: الموافقة**
- يراجع المدير المباشر ويوافق
- يوافق مالك البيانات للوصول إلى البيانات الحساسة
- يراجع فريق الأمن للامتثال

**الخطوة 3: التوفير**
- توفر تقنية المعلومات الوصول خلال 24 ساعة
- يتلقى المستخدم بيانات الاعتماد بشكل آمن
- يتم تسجيل الوصول في نظام إدارة الهوية

**الخطوة 4: التحقق**
- تتحقق تقنية المعلومات من منح الوصول بشكل صحيح
- يؤكد المستخدم عمل الوصول
- يتم إغلاق التذكرة مع التوثيق

---

## 6. Access Review | مراجعة الوصول

### English

**Quarterly Reviews:**
- All user access reviewed every 90 days
- Managers certify access still required
- Unused access removed automatically
- Review reports to CISO

**Privileged Access Reviews:**
- Monthly reviews for administrator accounts
- Documented business justification required
- CISO approval for continued access

### العربية

**المراجعات الربع سنوية:**
- تتم مراجعة جميع وصول المستخدمين كل 90 يومًا
- يصدق المديرون على أن الوصول لا يزال مطلوبًا
- إزالة الوصول غير المستخدم تلقائيًا
- تقارير المراجعة لمدير أمن المعلومات

**مراجعات الوصول المميز:**
- مراجعات شهرية لحسابات المسؤولين
- مطلوب مبرر تجاري موثق
- موافقة مدير أمن المعلومات للوصول المستمر

---

## 7. Access Revocation | إلغاء الوصول

### English

**Immediate Revocation:**
- Termination (voluntary or involuntary)
- Security incident involvement
- Policy violation
- Extended leave (>30 days)

**HR Notification:**
- HR notifies IT within 2 hours of termination
- All access disabled immediately
- Physical access cards deactivated
- Equipment retrieved

### العربية

**الإلغاء الفوري:**
- الإنهاء (طوعي أو غير طوعي)
- المشاركة في حادثة أمنية
- انتهاك السياسة
- إجازة ممتدة (>30 يومًا)

**إشعار الموارد البشرية:**
- تخطر الموارد البشرية تقنية المعلومات خلال ساعتين من الإنهاء
- تعطيل جميع الوصول فوراً
- إلغاء تنشيط بطاقات الوصول المادي
- استرجاع المعدات

---

*Related Policies: POL-AC-002 (Password), POL-AC-003 (Privileged Access), POL-HR-001 (HR Security)*
