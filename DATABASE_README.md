# قاعدة البيانات - SICO GRC Platform Database

## نظرة عامة | Overview

قاعدة البيانات المستخدمة في المشروع هي **SQLite 3** مع محرك اتصال غير متزامن (asyncio).

The database used in this project is **SQLite 3** with asynchronous connection driver (asyncio).

---

## المواصفات التقنية | Technical Specifications

### نوع قاعدة البيانات | Database Type

- **النوع**: SQLite 3
- **المحرك**: `aiosqlite` (Async SQLite driver)
- **ORM**: SQLAlchemy 2.0 (Async)
- **أداة الهجرة**: Alembic

### الموقع | Location

```
src/backend/sico_grc.db
```

### سلسلة الاتصال | Connection String

```
DATABASE_URL=sqlite+aiosqlite:///./sico_grc.db
```

### معلومات الملف | File Information

- **الحجم**: 1,060,864 بايت (~1.01 ميجابايت)
- **آخر تعديل**: 23/02/2026 23:43:40
- **عدد الجداول**: 66 جدول
- **إجمالي السجلات**: ~620 سجل نشط

---

## البنية | Structure

### الجداول الرئيسية | Main Tables

#### 1. وحدة الضوابط | Controls Module

- **controls**: 495 سجل (أكبر جدول في النظام)
  - الضوابط الأمنية من مختلف الأطر (NCA ECC, SAMA CSF, إلخ)
  - يحتوي على معلومات ثنائية اللغة (عربي/إنجليزي)

#### 2. وحدة الأدلة | Evidence Module

- **evidences**: 13 سجل
  - الأدلة المرفوعة
  - تواريخ الانتهاء والموافقات

#### 3. إدارة المستخدمين | User Management

- **users**: 8 مستخدمين
- **organizations**: 5 منظمات
- **roles**: 5 أدوار
- **permissions**: 17 صلاحية
- **role_permissions**: 37 ربط بين الأدوار والصلاحيات

#### 4. إدارة الأصول | Assets Management

- **assets**: 5 أصول
- **asset_owners**: تعيين مالكي الأصول
- **asset_data_classifications**: تصنيفات البيانات

#### 5. إدارة المخاطر | Risk Management

- **risks**: 3 مخاطر
- **risk_assessments**: تقييمات المخاطر
- **risk_registers**: سجلات المخاطر

#### 6. المراجعات | Auditing

- **audit_findings**: 2 نتيجة مراجعة
- **audit_trails**: سجلات المراجعة
- **compliance_audits**: مراجعات الامتثال

#### 7. الخصوصية (PDPL) | Privacy Module

- **dsar_requests**: 2 طلب حقوق الوصول للبيانات
- **ropa_records**: 2 سجل معالجة البيانات
- **data_breaches**: 1 خرق بيانات

#### 8. الموردين | Vendors

- **vendors**: 2 مورد
- **vendor_assessments**: تقييمات الموردين
- **vendor_contracts**: عقود الموردين

#### 9. سير العمل | Workflows

- **workflow_cases**: 2 حالة سير عمل
- **workflow_approvals**: موافقات سير العمل
- **workflow_comments**: تعليقات سير العمل

#### 10. ISMS (إدارة أمن المعلومات)

- **isms_policies**: سياسات أمن المعلومات
- **isms_procedures**: إجراءات أمن المعلومات
- **information_assets**: أصول المعلومات

#### 11. الذكاء الاصطناعي AI Governance

- **ai_systems**: أنظمة الذكاء الاصطناعي
- **ai_model_assessments**: تقييمات نماذج AI
- **ai_risk_assessments**: تقييمات مخاطر AI

#### 12. SIEM (إدارة الأحداث الأمنية)

- **siem_events**: الأحداث الأمنية
- **siem_alerts**: التنبيهات الأمنية
- **incidents**: الحوادث الأمنية

#### 13. التدريب | Training

- **training_courses**: دورات التدريب
- **training_enrollments**: تسجيلات التدريب
- **training_completions**: إنجازات التدريب

#### 14. النسخ الاحتياطي | Backup & DR

- **backup_schedules**: جداول النسخ الاحتياطي
- **backup_logs**: سجلات النسخ الاحتياطي
- **disaster_recovery_plans**: خطط استمرارية الأعمال

---

## الإعداد | Setup

### المتطلبات | Requirements

```bash
pip install sqlalchemy[asyncio] aiosqlite alembic
```

### إنشاء قاعدة البيانات | Database Creation

```bash
# تشغيل الهجرات
alembic upgrade head

# تحميل البيانات التجريبية
python scripts/load_sample_data.py
```

### الاتصال | Connection

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(
    "sqlite+aiosqlite:///./sico_grc.db",
    echo=False,
    future=True
)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
```

---

## فحص قاعدة البيانات | Database Inspection

### عرض جميع الجداول | List All Tables

```python
import sqlite3
conn = sqlite3.connect('sico_grc.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    print(table[0])
```

### عد السجلات | Count Records

```python
cursor.execute("SELECT COUNT(*) FROM controls")
print(f"Controls: {cursor.fetchone()[0]}")
```

### استخدام السكريبت الجاهز | Use Ready Script

```bash
cd src/backend
python check_db.py
```

---

## الهجرات | Migrations

### سجل الهجرات المطبقة | Applied Migrations

- 8 هجرات مطبقة
- من 001 إلى 007
- تشمل: إنشاء الجداول الأساسية، الضوابط، الأدلة، المستخدمين، الأدوار، الصلاحيات

### إنشاء هجرة جديدة | Create New Migration

```bash
alembic revision --autogenerate -m "وصف الهجرة"
```

### تطبيق الهجرات | Apply Migrations

```bash
alembic upgrade head
```

### التراجع عن هجرة | Rollback Migration

```bash
alembic downgrade -1
```

---

## النسخ الاحتياطي | Backup

### نسخ احتياطي يدوي | Manual Backup

```bash
# Windows PowerShell
Copy-Item src\backend\sico_grc.db src\backend\sico_grc_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').db

# Linux/Mac
cp src/backend/sico_grc.db src/backend/sico_grc_backup_$(date +%Y%m%d_%H%M%S).db
```

### نسخ احتياطي تلقائي | Automated Backup

راجع سكريبتات النسخ الاحتياطي في `scripts/backup/`

---

## الانتقال إلى PostgreSQL | Migration to PostgreSQL

عند الانتقال للإنتاج، يمكن التحول إلى PostgreSQL بتحديث `DATABASE_URL`:

```bash
# PostgreSQL
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/sico_grc
```

الكود يدعم PostgreSQL بدون تعديلات إضافية بفضل SQLAlchemy.

---

## إحصائيات البيانات | Data Statistics

### توزيع السجلات | Record Distribution

| الجدول             | Table           | عدد السجلات | Count     |
| ------------------ | --------------- | ----------- | --------- |
| controls           | الضوابط         | 495         | ⭐ الأكبر |
| evidences          | الأدلة          | 13          |           |
| users              | المستخدمين      | 8           |           |
| organizations      | المنظمات        | 5           |           |
| assets             | الأصول          | 5           |           |
| roles              | الأدوار         | 5           |           |
| role_permissions   | صلاحيات الأدوار | 37          |           |
| permissions        | الصلاحيات       | 17          |           |
| risks              | المخاطر         | 3           |           |
| compliance_metrics | مقاييس الامتثال | 3           |           |
| audit_findings     | نتائج المراجعات | 2           |           |
| dsar_requests      | طلبات DSAR      | 2           |           |
| ropa_records       | سجلات ROPA      | 2           |           |
| vendors            | الموردين        | 2           |           |
| workflow_cases     | حالات سير العمل | 2           |           |
| data_breaches      | خروقات البيانات | 1           |           |

**إجمالي**: ~620 سجل نشط عبر 66 جدول

---

## الموارد | Resources

- [SQLAlchemy Async Documentation](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Aiosqlite Documentation](https://aiosqlite.omnilib.dev/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)

---

## الملاحظات | Notes

1. **الأداء**: SQLite مناسب للتطوير والنماذج الأولية، لكن يُنصح بـ PostgreSQL للإنتاج
2. **التزامن**: استخدام `aiosqlite` يتيح عمليات async/await مع SQLite
3. **الأمان**: كلمات المرور مشفرة باستخدام bcrypt
4. **ثنائية اللغة**: جميع الجداول الرئيسية تدعم العربية والإنجليزية
5. **التدقيق**: جدول `audit_trails` يسجل جميع العمليات الحرجة

---

آخر تحديث: 24 فبراير 2026
Last Updated: February 24, 2026
