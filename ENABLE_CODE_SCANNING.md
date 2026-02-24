# تفعيل فحص الكود GitHub Code Scanning

## المشكلة | Problem

```
Warning: Code scanning is not enabled for this repository. 
Please enable code scanning in the repository settings.
```

## الحل | Solution

### الطريقة الأولى: من خلال واجهة GitHub (الأسهل)

1. **اذهب إلى إعدادات المستودع**:
   ```
   https://github.com/sonaiso/sanadcom/settings
   ```

2. **في القائمة الجانبية، اختر**:
   - **Code security and analysis** (الأمان وتحليل الكود)

3. **ابحث عن قسم "Code scanning"**:
   - اضغط على **"Set up"** أو **"Enable"**
   - اختر **"Default"** (الافتراضي) أو **"Advanced"** (متقدم)

4. **إذا اخترت Default**:
   - GitHub سيكتشف تلقائيًا CodeQL workflow الموجود
   - سيبدأ الفحص تلقائيًا

5. **إذا اخترت Advanced**:
   - استخدم الـ workflow الموجود بالفعل في:
     ```
     .github/workflows/security-scanning.yml
     ```

---

### الطريقة الثانية: التأكد من صلاحيات الـ Workflow

تأكد أن ملف `.github/workflows/security-scanning.yml` يحتوي على:

```yaml
permissions:
  contents: read
  security-events: write  # ✅ مهم لرفع نتائج CodeQL
  actions: read
  pull-requests: write
```

✅ **تم التحديث**: تم تعديل الملف لرفع النتائج (`upload: true`)

---

### الطريقة الثالثة: إنشاء CodeQL Workflow منفصل

إذا لم ينجح ما سبق، أنشئ ملف:

**`.github/workflows/codeql.yml`**:

```yaml
name: CodeQL Security Analysis

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * 1'  # كل إثنين الساعة 2 صباحًا

jobs:
  analyze:
    name: Analyze
    runs-on: ubuntu-latest
    permissions:
      actions: read
      contents: read
      security-events: write

    strategy:
      fail-fast: false
      matrix:
        language: ['python', 'javascript']

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Initialize CodeQL
        uses: github/codeql-action/init@v3
        with:
          languages: ${{ matrix.language }}

      - name: Autobuild
        uses: github/codeql-action/autobuild@v3

      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v3
        with:
          category: "/language:${{matrix.language}}"
```

---

## التحقق من التفعيل | Verification

بعد التفعيل، يمكنك التحقق من:

1. **تبويب Security في المستودع**:
   ```
   https://github.com/sonaiso/sanadcom/security
   ```

2. **تبويب Code scanning alerts**:
   ```
   https://github.com/sonaiso/sanadcom/security/code-scanning
   ```

3. **ستظهر رسالة**:
   ```
   ✅ Code scanning has been set up for this repository
   ```

---

## ملاحظات مهمة | Important Notes

### 1. المستودعات الخاصة (Private Repos)
- Code Scanning في المستودعات الخاصة يتطلب:
  - **GitHub Advanced Security** (مدفوع)
  - أو تفعيل **GitHub Enterprise**

### 2. المستودعات العامة (Public Repos)
- Code Scanning **مجاني تماماً** للمستودعات العامة ✅

### 3. الحدود والقيود
- **لغات مدعومة**: Python, JavaScript, TypeScript, Java, C++, C#, Go, Ruby
- **عدد الفحوصات**: غير محدود للمستودعات العامة
- **حجم الكود**: حتى 100K سطر بدون قيود

---

## التغييرات المطبقة | Applied Changes

✅ **تم التعديل في `security-scanning.yml`**:

```yaml
# قبل (Before):
- name: Perform CodeQL Analysis
  uses: github/codeql-action/analyze@v4
  with:
    category: "/language:${{ matrix.language }}"
    upload: false  # ❌ كان يمنع الرفع

# بعد (After):
- name: Perform CodeQL Analysis
  uses: github/codeql-action/analyze@v4
  with:
    category: "/language:${{ matrix.language }}"
    upload: true  # ✅ الآن يرفع النتائج
```

---

## الخطوات التالية | Next Steps

1. **Commit التغييرات**:
   ```powershell
   git add .github/workflows/security-scanning.yml
   git commit -m "fix: enable CodeQL results upload for code scanning"
   git push origin main
   ```

2. **انتظر تشغيل الـ Workflow**:
   - اذهب إلى: `https://github.com/sonaiso/sanadcom/actions`
   - انتظر انتهاء **Security CI Pipeline**

3. **تحقق من النتائج**:
   - اذهب إلى: `https://github.com/sonaiso/sanadcom/security/code-scanning`
   - يجب أن ترى نتائج الفحص

---

## المساعدة والدعم | Help & Support

### الوثائق الرسمية:
- [About code scanning](https://docs.github.com/en/code-security/code-scanning/automatically-scanning-your-code-for-vulnerabilities-and-errors/about-code-scanning)
- [Setting up code scanning](https://docs.github.com/en/code-security/code-scanning/automatically-scanning-your-code-for-vulnerabilities-and-errors/configuring-code-scanning)
- [CodeQL documentation](https://codeql.github.com/docs/)

### إذا واجهت مشاكل:
1. تأكد من أن المستودع **عام** (Public) للحصول على الميزة مجاناً
2. تحقق من صلاحيات الـ **security-events: write**
3. راجع سجلات الـ Actions للأخطاء
4. تواصل مع GitHub Support إذا استمرت المشكلة

---

آخر تحديث: 24 فبراير 2026  
Last Updated: February 24, 2026
