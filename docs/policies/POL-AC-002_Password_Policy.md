# Password Policy | سياسة كلمات المرور

## POL-AC-002

---

## Document Control | التحكم في الوثيقة

| **Field** | **English** | **العربية** |
|-----------|-------------|--------------|
| **Policy Number** | POL-AC-002 | رقم السياسة: POL-AC-002 |
| **Version** | 1.0 | الإصدار: 1.0 |
| **Effective Date** | 2026-03-01 | تاريخ السريان: 1 مارس 2026 |

---

## 1. Purpose | الغرض

### English
Establish password requirements to protect SICO systems from unauthorized access through strong authentication practices compliant with NCA ECC-AC-2 and ISO 27001 A.5.17.

### العربية
وضع متطلبات كلمات المرور لحماية أنظمة سيكو من الوصول غير المصرح به من خلال ممارسات المصادقة القوية المتوافقة مع NCA ECC-AC-2 وISO 27001 A.5.17.

---

## 2. Password Requirements | متطلبات كلمات المرور

### English

**Minimum Standards:**

✅ **Length**: 12 characters minimum (14 for privileged accounts)  
✅ **Complexity**: 3 of 4 character types (uppercase, lowercase, number, special)  
✅ **History**: Cannot reuse last 10 passwords  
✅ **Expiry**: 90 days for users, 60 days for administrators  
✅ **Lockout**: 5 failed attempts = 30-minute lockout  

**Prohibited Practices:**
❌ Company name, username in password  
❌ Dictionary words or common patterns  
❌ Sequential characters (123, abc)  
❌ Sharing passwords  
❌ Writing passwords down  
❌ Storing passwords in browsers (use password manager)  

**Multi-Factor Authentication (MFA):**
- **Required** for all remote access
- **Required** for privileged accounts
- **Required** for access to production systems
- **Required** for customer data access
- SMS, authenticator app, or hardware token

### العربية

**الحد الأدنى من المعايير:**

✅ **الطول**: 12 حرفًا كحد أدنى (14 للحسابات المميزة)  
✅ **التعقيد**: 3 من 4 أنواع أحرف (كبيرة، صغيرة، رقمية، خاصة)  
✅ **السجل**: لا يمكن إعادة استخدام آخر 10 كلمات مرور  
✅ **الانتهاء**: 90 يومًا للمستخدمين، 60 يومًا للمسؤولين  
✅ **القفل**: 5 محاولات فاشلة = قفل لمدة 30 دقيقة  

**الممارسات الممنوعة:**
❌ اسم الشركة، اسم المستخدم في كلمة المرور  
❌ كلمات القاموس أو الأنماط الشائعة  
❌ الأحرف المتسلسلة (123، abc)  
❌ مشاركة كلمات المرور  
❌ كتابة كلمات المرور  
❌ تخزين كلمات المرور في المتصفحات (استخدم مدير كلمات المرور)  

**المصادقة متعددة العوامل (MFA):**
- **مطلوبة** لجميع الوصول عن بُعد
- **مطلوبة** للحسابات المميزة
- **مطلوبة** للوصول إلى أنظمة الإنتاج
- **مطلوبة** للوصول إلى بيانات العملاء
- رسالة نصية، تطبيق المصادقة، أو رمز الأجهزة

---

## 3. Password Management | إدارة كلمات المرور

### English

**Password Manager (Required):**
- SICO-approved: 1Password Enterprise
- All work passwords must be stored in password manager
- Generates strong random passwords
- Encrypted vault with master password + MFA
- Share credentials via secure vault sharing (not email/chat)

**Service Accounts:**
- 24+ character random passwords
- Stored in privileged access management (PAM) system
- Automatic rotation every 90 days
- Access logged and monitored

**Initial Passwords:**
- Temporary password sent via separate channel (not email)
- User forced to change on first login
- Temporary password expires in 24 hours

### العربية

**مدير كلمات المرور (مطلوب):**
- معتمد من سيكو: 1Password Enterprise
- يجب تخزين جميع كلمات مرور العمل في مدير كلمات المرور
- يولد كلمات مرور عشوائية قوية
- خزنة مشفرة بكلمة مرور رئيسية + MFA
- مشاركة بيانات الاعتماد عبر مشاركة الخزنة الآمنة (وليس البريد الإلكتروني/الدردشة)

**حسابات الخدمة:**
- كلمات مرور عشوائية بطول 24+ حرف
- مخزنة في نظام إدارة الوصول المميز (PAM)
- التدوير التلقائي كل 90 يومًا
- الوصول مسجل ومراقب

**كلمات المرور الأولية:**
- كلمة مرور مؤقتة مرسلة عبر قناة منفصلة (وليس البريد الإلكتروني)
- يجبر المستخدم على التغيير عند تسجيل الدخول الأول
- كلمة المرور المؤقتة تنتهي في 24 ساعة

---

## 4. Compliance | الامتثال

### English

**Framework Mappings:**

| **Framework** | **Control** | **Requirement** |
|---------------|-------------|-----------------|
| ISO 27001 | A.5.17 | Authentication information management |
| NCA ECC | ECC-AC-2 | Password management and complexity |
| NCA CCC | CCC-IAM-3 | Strong authentication |
| PDPL | Article 5 | Technical security measures |
| NIST CSF 2.0 | PR.AC-7 | Credential management |

### العربية
يدعم ISO 27001 (A.5.17)، NCA ECC (AC-2)، NCA CCC (IAM-3)، PDPL (المادة 5)، NIST CSF 2.0 (PR.AC-7).

---

*Related Policies: POL-AC-001 (Access Control), POL-AC-003 (Privileged Access), POL-AC-004 (Remote Access)*
