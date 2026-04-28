#!/usr/bin/env python3
"""
Fill missing Arabic translations in frontend/messages/ar.json.
Uses pattern-based CRUD translation + a comprehensive GRC term dictionary.
Handles the duplicate key in en.json by keeping the last value.
"""
import json
import re
import os

# ── Full-phrase dictionary (lower-case English → Arabic) ──────────────────────
PHRASES = {
    # ── Temporal ──────────────────────────────────────────────────────────────
    "days": "أيام", "weeks": "أسابيع", "months": "أشهر", "years": "سنوات",
    "hours": "ساعات", "minutes": "دقائق",
    "daily": "يومياً", "weekly": "أسبوعياً", "monthly": "شهرياً",
    "yearly": "سنوياً", "annual": "سنوي", "quarterly": "ربع سنوي",
    "step 1": "الخطوة 1", "step 2": "الخطوة 2", "step 3": "الخطوة 3",
    "step 4": "الخطوة 4", "step 5": "الخطوة 5",

    # ── Status / severity ─────────────────────────────────────────────────────
    "inherent": "متأصل", "residual": "متبقي",
    "low": "منخفض", "medium": "متوسط", "high": "مرتفع",
    "critical": "حرج", "very low": "منخفض جداً", "very high": "مرتفع جداً",
    "compliant": "ممتثل", "non compliant": "غير ممتثل",
    "partially compliant": "ممتثل جزئياً",
    "not applicable": "غير قابل للتطبيق", "to do": "للتنفيذ",
    "in progress": "قيد التنفيذ", "done": "منتهٍ", "deprecated": "مهمل",
    "open": "مفتوح", "closed": "مغلق", "mitigated": "تم التخفيف",
    "accepted": "مقبول", "transferred": "محوَّل", "avoided": "تم التجنب",
    "change requested": "تغيير مطلوب", "under review": "قيد المراجعة",
    "under investigation": "قيد التحقيق", "resolved": "تم الحل",
    "verified": "تم التحقق", "approved": "معتمد", "rejected": "مرفوض",
    "pending": "معلق", "overdue": "متأخر", "on track": "في المسار الصحيح",
    "at risk": "في خطر", "blocked": "محظور", "cancelled": "ملغي",
    "expired": "منتهي الصلاحية", "renewed": "تم التجديد",
    "published": "منشور", "archived": "مؤرشف", "active": "نشط",
    "inactive": "غير نشط", "enabled": "مفعّل", "disabled": "معطّل",
    "qualitative": "نوعي", "quantitative": "كمي",
    "not selected": "غير محدد", "selected": "محدد",
    "unassigned": "غير معيَّن",

    # ── Core UI verbs ─────────────────────────────────────────────────────────
    "add": "إضافة", "create": "إنشاء", "edit": "تعديل",
    "update": "تحديث", "delete": "حذف", "remove": "إزالة",
    "view": "عرض", "show": "عرض", "hide": "إخفاء", "toggle": "تبديل",
    "save": "حفظ", "cancel": "إلغاء", "confirm": "تأكيد",
    "close": "إغلاق", "open": "فتح", "submit": "إرسال",
    "continue": "متابعة", "proceed": "المتابعة", "finish": "إنهاء",
    "apply": "تطبيق", "reset": "إعادة تعيين", "clear": "مسح",
    "select": "تحديد", "deselect": "إلغاء التحديد",
    "select all": "تحديد الكل", "deselect all": "إلغاء تحديد الكل",
    "expand": "توسيع", "collapse": "طي", "preview": "معاينة",
    "print": "طباعة", "refresh": "تحديث", "reload": "إعادة تحميل",
    "generate": "إنشاء", "calculate": "حساب", "analyze": "تحليل",
    "visualize": "تصور", "compare": "مقارنة", "sync": "مزامنة",
    "share": "مشاركة", "schedule": "جدولة", "start": "بدء",
    "stop": "إيقاف", "pause": "إيقاف مؤقت", "resume": "استئناف",
    "upload": "رفع", "download": "تنزيل", "import": "استيراد",
    "export": "تصدير", "backup": "نسخ احتياطي", "restore": "استعادة",
    "publish": "نشر", "archive": "أرشفة", "duplicate": "تكرار",
    "copy": "نسخ", "link": "ربط", "unlink": "فك الربط",
    "assign": "تعيين", "unassign": "إلغاء التعيين",
    "approve": "موافقة", "reject": "رفض", "accept": "قبول",
    "enable": "تفعيل", "disable": "تعطيل",
    "manage": "إدارة", "configure": "تهيئة", "deploy": "نشر",
    "build": "بناء", "run": "تشغيل", "test": "اختبار",
    "monitor": "مراقبة", "maintain": "صيانة", "implement": "تنفيذ",
    "plan": "تخطيط", "document": "توثيق", "train": "تدريب",
    "mark as done": "تعيين كمنتهٍ", "mark as reviewed": "تعيين كمراجَع",
    "save and continue": "حفظ ومتابعة",
    "next": "التالي", "previous": "السابق", "back": "رجوع",

    # ── GRC domain entities ───────────────────────────────────────────────────
    "risk": "المخاطر", "risks": "المخاطر",
    "risk assessment": "تقييم المخاطر",
    "risk assessments": "تقييمات المخاطر",
    "risk scenario": "سيناريو المخاطر",
    "risk scenarios": "سيناريوهات المخاطر",
    "risk acceptance": "قبول المخاطر",
    "risk acceptances": "قبول المخاطر",
    "risk matrix": "مصفوفة المخاطر",
    "risk matrices": "مصفوفات المخاطر",
    "risk register": "سجل المخاطر",
    "risk appetite": "شهية المخاطر",
    "risk tolerance": "تحمّل المخاطر",
    "risk owner": "مالك المخاطر",
    "risk treatment": "معالجة المخاطر",
    "residual risk": "المخاطر المتبقية",
    "inherent risk": "المخاطر المتأصلة",
    "risk level": "مستوى المخاطر",
    "risk score": "نتيجة المخاطر",
    "risk rating": "تصنيف المخاطر",
    "risk category": "فئة المخاطر",
    "risk domain": "مجال المخاطر",
    "risk origin": "مصدر المخاطر",
    "risk origins": "مصادر المخاطر",
    "risk origins and target objectives (ebios rm)": "مصادر المخاطر والأهداف المستهدفة (EBIOS RM)",
    "control": "الضابط", "controls": "الضوابط",
    "reference control": "الضابط المرجعي",
    "reference controls": "الضوابط المرجعية",
    "applied control": "الضابط المطبق",
    "applied controls": "الضوابط المطبقة",
    "control effectiveness": "فعالية الضابط",
    "control gap": "فجوة الضابط",
    "control objective": "هدف الضابط",
    "compliance": "الامتثال",
    "compliance assessment": "تقييم الامتثال",
    "compliance assessments": "تقييمات الامتثال",
    "requirement": "المتطلب", "requirements": "المتطلبات",
    "requirement assessment": "تقييم المتطلب",
    "requirement assessments": "تقييمات المتطلبات",
    "requirement node": "عقدة المتطلب",
    "requirement mapping set": "مجموعة تعيين المتطلبات",
    "requirement mapping sets": "مجموعات تعيين المتطلبات",
    "framework": "إطار العمل", "frameworks": "أطر العمل",
    "policy": "السياسة", "policies": "السياسات",
    "threat": "التهديد", "threats": "التهديدات",
    "vulnerability": "الثغرة", "vulnerabilities": "الثغرات",
    "asset": "الأصل", "assets": "الأصول",
    "asset assessment": "تقييم الأصول",
    "asset assessments": "تقييمات الأصول",
    "asset class": "فئة الأصول",
    "asset classes": "فئات الأصول",
    "evidence": "الدليل", "evidences": "الأدلة",
    "evidence revision": "مراجعة الدليل",
    "evidence revisions": "مراجعات الأدلة",
    "folder": "المجلد", "folders": "المجلدات",
    "domain": "النطاق", "domains": "النطاقات",
    "perimeter": "المحيط", "perimeters": "المحيطات",
    "user": "المستخدم", "users": "المستخدمون",
    "user group": "مجموعة المستخدمين",
    "user groups": "مجموعات المستخدمين",
    "role": "الدور", "roles": "الأدوار",
    "role assignment": "تعيين الدور",
    "role assignments": "تعيينات الأدوار",
    "finding": "الاكتشاف", "findings": "الاكتشافات",
    "findings assessment": "تقييم الاكتشافات",
    "task": "المهمة", "tasks": "المهام",
    "task template": "قالب المهمة",
    "task templates": "قوالب المهام",
    "occurrence": "الحدوث", "occurrences": "الحوادث",
    "campaign": "الحملة", "campaigns": "الحملات",
    "entity": "الكيان", "entities": "الكيانات",
    "solution": "الحل", "solutions": "الحلول",
    "contract": "العقد", "contracts": "العقود",
    "supplier": "المورد", "suppliers": "الموردون",
    "library": "المكتبة", "libraries": "المكتبات",
    "loaded library": "المكتبة المحملة",
    "stored library": "المكتبة المخزنة",
    "metric": "المقياس", "metrics": "المقاييس",
    "metric definition": "تعريف المقياس",
    "metric definitions": "تعريفات المقاييس",
    "security objective": "خاصية الأمان",
    "security objectives": "خصائص الأمان",
    "security objective scale": "مقياس خصائص الأمان",
    "observation": "الملاحظة", "observations": "الملاحظات",
    "recommendation": "التوصية", "recommendations": "التوصيات",
    "action plan": "خطة العمل", "action plans": "خطط العمل",
    "corrective action": "الإجراء التصحيحي",
    "corrective actions": "الإجراءات التصحيحية",
    "preventive action": "الإجراء الوقائي",
    "preventive actions": "الإجراءات الوقائية",
    "exception": "الاستثناء", "exceptions": "الاستثناءات",
    "accreditation": "الاعتماد", "accreditations": "الاعتمادات",
    "generic collection": "المجموعة العامة",
    "generic collections": "المجموعات العامة",
    "personal access token": "رمز الوصول الشخصي",
    "personal access tokens": "رموز الوصول الشخصية",
    "sso settings": "إعدادات SSO",
    "global settings": "الإعدادات العامة",
    "filtering label": "علامة التصفية",
    "filtering labels": "علامات التصفية",
    "library filtering labels": "علامات تصفية المكتبة",
    "sso": "SSO", "saml": "SAML",

    # EBIOS RM
    "ebios rm": "EBIOS RM",
    "ebios rm study": "دراسة EBIOS RM",
    "feared event": "الحدث المخيف",
    "feared events": "الأحداث المخيفة",
    "stakeholder": "صاحب المصلحة",
    "stakeholders": "أصحاب المصلحة",
    "attack path": "مسار الهجوم",
    "attack paths": "مسارات الهجوم",
    "strategic scenario": "السيناريو الاستراتيجي",
    "strategic scenarios": "السيناريوهات الاستراتيجية",
    "foundations": "الأسس", "baseline": "الأساس",
    "current trust": "الثقة الحالية",

    # Privacy
    "privacy": "الخصوصية",
    "data transfer": "نقل البيانات",
    "data transfers": "عمليات نقل البيانات",
    "data breach": "خرق البيانات",
    "data breaches": "خروقات البيانات",
    "right request": "طلب الحق",
    "right requests": "طلبات الحقوق",
    "dpia": "تقييم أثر حماية البيانات",
    "service provider": "مزود الخدمة",

    # Quantitative risk / CRQ
    "crq": "CRQ",
    "annual loss expectancy": "التوقع السنوي للخسارة",
    "quantitative risk study": "دراسة المخاطر الكمية",
    "quantitative risk scenario": "سيناريو المخاطر الكمي",
    "quantitative risk hypothesis": "فرضية المخاطر الكمية",
    "crq hypotheses": "فرضيات CRQ",
    "hypothesis": "الفرضية", "hypotheses": "الفرضيات",
    "loss at p/2": "الخسارة عند P/2",
    "probability": "الاحتمالية",
    "likelihood": "الاحتمالية",
    "severity": "الخطورة",
    "frequency": "التكرار",
    "exposure": "التعرض",
    "expected loss": "الخسارة المتوقعة",

    # Resilience / PMBOK / IAM
    "pmbok": "PMBOK",
    "iam": "IAM",
    "business impact analysis": "تحليل الأثر على الأعمال",
    "bcp": "خطة استمرارية الأعمال",
    "rto": "هدف وقت الاسترداد",
    "rpo": "هدف نقطة الاسترداد",
    "resilience": "المرونة",
    "continuity": "الاستمرارية",
    "disaster recovery": "التعافي من الكوارث",
    "business continuity": "استمرارية الأعمال",

    # Additional GRC/UI
    "impact": "التأثير", "effort": "الجهد", "priority": "الأولوية",
    "category": "الفئة", "categories": "الفئات",
    "tag": "العلامة", "tags": "العلامات",
    "label": "التسمية", "labels": "التسميات",
    "filter": "التصفية", "filters": "المرشحات",
    "audit": "التدقيق", "audit log": "سجل التدقيق",
    "log": "السجل", "logs": "السجلات",
    "report": "التقرير", "reports": "التقارير",
    "dashboard": "لوحة التحكم",
    "summary": "الملخص", "overview": "نظرة عامة",
    "detail": "التفاصيل", "details": "التفاصيل",
    "description": "الوصف", "name": "الاسم",
    "title": "العنوان", "date": "التاريخ",
    "deadline": "الموعد النهائي",
    "due date": "تاريخ الاستحقاق",
    "start date": "تاريخ البدء", "end date": "تاريخ الانتهاء",
    "expiry": "انتهاء الصلاحية",
    "created at": "تاريخ الإنشاء", "updated at": "تاريخ التحديث",
    "comment": "تعليق", "comments": "التعليقات",
    "note": "ملاحظة", "notes": "الملاحظات",
    "action": "الإجراء", "actions": "الإجراءات",
    "objective": "الهدف", "objectives": "الأهداف",
    "scope": "النطاق", "treatment": "المعالجة",
    "mitigation": "التخفيف", "remediation": "المعالجة",
    "review": "المراجعة", "reviews": "المراجعات",
    "approval": "الموافقة", "approvals": "الموافقات",
    "approver": "المعتمد", "owner": "المالك",
    "assignee": "المُسنَد إليه", "reviewer": "المراجع",
    "author": "المؤلف", "administrator": "المسؤول", "admin": "المسؤول",
    "permission": "الصلاحية", "permissions": "الصلاحيات",
    "authentication": "المصادقة", "authorization": "التفويض",
    "session": "الجلسة", "token": "الرمز",
    "password": "كلمة المرور", "email": "البريد الإلكتروني",
    "phone": "الهاتف", "organization": "المنظمة",
    "company": "الشركة", "department": "القسم", "team": "الفريق",
    "project": "المشروع", "projects": "المشاريع",
    "setting": "الإعداد", "settings": "الإعدادات",
    "configuration": "الإعداد",
    "notification": "الإشعار", "notifications": "الإشعارات",
    "webhook": "Webhook",
    "integration": "التكامل", "integrations": "التكاملات",
    "file": "الملف", "files": "الملفات",
    "attachment": "المرفق", "attachments": "المرفقات",
    "document": "الوثيقة", "documents": "الوثائق",
    "chart": "الرسم البياني", "matrix": "المصفوفة",
    "table": "الجدول", "list": "القائمة",
    "search": "البحث", "sort": "الفرز",
    "item": "العنصر", "items": "العناصر",
    "result": "النتيجة", "results": "النتائج",
    "message": "الرسالة", "messages": "الرسائل",
    "template": "القالب", "templates": "القوالب",
    "version": "الإصدار", "history": "السجل",
    "activity": "النشاط", "activities": "الأنشطة",
    "workflow": "سير العمل", "process": "العملية",
    "guideline": "الإرشادات", "guidelines": "الإرشادات",
    "reference": "المرجع", "references": "المراجع",
    "source": "المصدر", "target": "الهدف",
    "origin": "المصدر",
    "standard": "المعيار", "standards": "المعايير",
    "regulation": "اللائحة", "regulations": "اللوائح",
    "iso": "ISO", "nist": "NIST", "pci dss": "PCI DSS",
    "gdpr": "GDPR", "sox": "SOX", "hipaa": "HIPAA",
    "nis2": "NIS2", "dora": "DORA",
    "availability": "التوفر", "integrity": "النزاهة",
    "confidentiality": "السرية",
    "information technology": "تقنية المعلومات",
    "information security": "أمن المعلومات",
    "cybersecurity": "الأمن السيبراني",
    "physical security": "الأمن المادي",
    "security assessment": "تقييم الأمن",
    "security review": "مراجعة الأمن",
    "security posture": "الوضع الأمني",
    "penetration test": "اختبار الاختراق",
    "vulnerability assessment": "تقييم الثغرات",
    "gap analysis": "تحليل الفجوات",
    "maturity": "النضج", "maturity level": "مستوى النضج",
    "best practice": "أفضل الممارسات",
    "best practices": "أفضل الممارسات",
    "incident": "الحادث", "incidents": "الحوادث",
    "breach": "الاختراق", "attack": "الهجوم",
    "malware": "البرمجيات الخبيثة",
    "encryption": "التشفير", "certificate": "الشهادة",
    "certificates": "الشهادات",
    "api": "واجهة برمجة التطبيقات",
    "api key": "مفتاح API", "endpoint": "نقطة النهاية",
    "server": "الخادم", "network": "الشبكة",
    "cloud": "السحابة", "infrastructure": "البنية التحتية",
    "software": "البرمجيات", "hardware": "الأجهزة",
    "application": "التطبيق", "applications": "التطبيقات",
    "system": "النظام", "systems": "الأنظمة",
    "database": "قاعدة البيانات", "storage": "التخزين",
    "follow-up": "المتابعة", "follow up": "المتابعة",
    "synced with": "متزامن مع", "synced": "متزامن",
    "unknown or deleted user": "مستخدم غير معروف أو محذوف",
    "assets in scope": "الأصول في النطاق",
    "no": "لا", "yes": "نعم", "none": "لا شيء",
    "all": "الكل", "other": "أخرى", "unknown": "غير معروف",
    "optional": "اختياري", "required": "مطلوب",
    "default": "افتراضي", "custom": "مخصص",
    "general": "عام", "advanced": "متقدم",
    "more": "المزيد", "less": "أقل",
    "count": "العدد", "total": "الإجمالي",
    "average": "المتوسط", "percentage": "النسبة المئوية",
    "score": "النتيجة", "level": "المستوى",
    "step": "الخطوة", "steps": "الخطوات",
    "page": "الصفحة", "section": "القسم",
    "tab": "علامة التبويب",
    "field": "الحقل", "fields": "الحقول",
    "value": "القيمة", "values": "القيم",
    "format": "التنسيق", "type": "النوع",
    "group": "المجموعة", "groups": "المجموعات",
    "loading": "جارٍ التحميل", "error": "خطأ",
    "success": "نجاح", "warning": "تحذير", "info": "معلومات",
    "home": "الرئيسية", "profile": "الملف الشخصي",
    "logout": "تسجيل الخروج", "login": "تسجيل الدخول",
    "register": "تسجيل",
    "forgot password": "نسيت كلمة المرور",
    "file too large": "الملف كبير جداً",
    "invalid file format": "صيغة ملف غير صالحة",
    "invalid compatibility mode": "وضع توافق غير صالح",
    "invalid excel file": "ملف Excel غير صالح",
    "processing timeout": "انتهت مهلة المعالجة",
    "malicious file detected": "تم اكتشاف ملف ضار",
    "server configuration error": "خطأ في تهيئة الخادم",
    "library load failed": "فشل تحميل المكتبة",
    "change history": "سجل التغييرات",
    "maturity assessment": "تقييم النضج",
    "maturity assessments": "تقييمات النضج",
    "score change detected": "تم اكتشاف تغيير في النتيجة",
    "rule of three": "قاعدة الثلاثة",
    "clamp": "تقييد",
    "reset": "إعادة تعيين",
    "mapping": "تعيين الخرائط",
    "mapping suggested": "تم اقتراح رسم الخرائط",
    "associated findings assessments": "التقييمات المرتبطة",
    "matching scenarios": "السيناريوهات المطابقة",
    "save and continue": "حفظ ومتابعة",
    "next occurrence status": "حالة الحدوث التالية",
    "image": "صورة",
    "security objectives": "خصائص الأمان",
    "actor": "فاعل",
    "private key": "المفتاح الخاص",
    "generate": "إنشاء",
    "download certificate": "تنزيل الشهادة",
    "view more": "عرض المزيد",
    "view less": "عرض أقل",
    "score change detected": "تم اكتشاف تغيير في النتيجة",
    "login failed": "فشل تسجيل الدخول",
    "expected evidence": "الأدلة المتوقعة",
    "occurrence due date": "تاريخ استحقاق الحدوث",
    "related to": "مرتبط بـ",
    "legacy evidence field": "حقل الأدلة القديم",
    "change accreditation": "تغيير الاعتماد",
    "delete accreditation": "حذف الاعتماد",
    "view accreditation": "عرض الاعتماد",
    "add folder": "إضافة مجلد",
    "change folder": "تغيير المجلد",
    "delete folder": "حذف المجلد",
    "add personal access token": "إضافة رمز الوصول الشخصي",
    "change personal access token": "تغيير رمز الوصول الشخصي",
    "delete personal access token": "حذف رمز الوصول الشخصي",
    "view personal access token": "عرض رمز الوصول الشخصي",
    "change role": "تغيير الدور",
    "delete role": "حذف الدور",
    "view role": "عرض الدور",
    "add role assignment": "إضافة تعيين الدور",
    "change role assignment": "تغيير تعيين الدور",
    "delete role assignment": "حذف تعيين الدور",
    "view role assignment": "عرض تعيين الدور",
    "add sso settings": "إضافة إعدادات SSO",
    "change sso settings": "تغيير إعدادات SSO",
    "delete sso settings": "حذف إعدادات SSO",
    "view sso settings": "عرض إعدادات SSO",
    "backup user": "نسخ احتياطي للمستخدم",
    "restore user": "استعادة المستخدم",
    "change user": "تغيير المستخدم",
    "delete user": "حذف المستخدم",
    "view user": "عرض المستخدم",
    "add user group": "إضافة مجموعة المستخدمين",
    "change user group": "تغيير مجموعة المستخدمين",
    "delete user group": "حذف مجموعة المستخدمين",
    "view user group": "عرض مجموعة المستخدمين",
    "add generic collection": "إضافة المجموعة العامة",
    "change generic collection": "تغيير المجموعة العامة",
    "delete generic collection": "حذف المجموعة العامة",
    "view generic collection": "عرض المجموعة العامة",
}


# ── CRUD-prefix map ───────────────────────────────────────────────────────────
AR_VERBS = {
    "add": "إضافة", "create": "إنشاء",
    "change": "تغيير", "edit": "تعديل", "update": "تحديث",
    "delete": "حذف", "remove": "حذف",
    "view": "عرض", "show": "عرض",
    "manage": "إدارة",
    "import": "استيراد", "export": "تصدير",
    "upload": "رفع", "download": "تنزيل",
    "backup": "نسخ احتياطي", "restore": "استعادة",
    "generate": "إنشاء", "publish": "نشر",
    "archive": "أرشفة", "duplicate": "تكرار",
    "assign": "تعيين", "enable": "تفعيل", "disable": "تعطيل",
    "approve": "اعتماد", "reject": "رفض",
    "sync": "مزامنة", "configure": "تهيئة", "copy": "نسخ",
    "link": "ربط",
}

# ── model-name → Arabic ──────────────────────────────────────────────────────
AR_MODELS = {
    "risk": "المخاطر",
    "riskassessment": "تقييم المخاطر",
    "riskscenario": "سيناريو المخاطر",
    "riskacceptance": "قبول المخاطر",
    "riskmatrix": "مصفوفة المخاطر",
    "control": "الضابط",
    "referencecontrol": "الضابط المرجعي",
    "appliedcontrol": "الضابط المطبق",
    "complianceassessment": "تقييم الامتثال",
    "requirement": "المتطلب",
    "requirementassessment": "تقييم المتطلب",
    "requirementnode": "عقدة المتطلب",
    "requirementmappingset": "مجموعة تعيين المتطلبات",
    "requirementmapping": "تعيين المتطلبات",
    "framework": "إطار العمل",
    "policy": "السياسة",
    "threat": "التهديد",
    "vulnerability": "الثغرة",
    "asset": "الأصل",
    "assetassessment": "تقييم الأصول",
    "assetclass": "فئة الأصول",
    "evidence": "الدليل",
    "evidencerevision": "مراجعة الدليل",
    "folder": "المجلد",
    "user": "المستخدم",
    "usergroup": "مجموعة المستخدمين",
    "role": "الدور",
    "roleassignment": "تعيين الدور",
    "personalaccesstoken": "رمز الوصول الشخصي",
    "ssosettings": "إعدادات SSO",
    "entity": "الكيان",
    "contract": "العقد",
    "supplier": "المورد",
    "library": "المكتبة",
    "loadedlibrary": "المكتبة المحملة",
    "storedlibrary": "المكتبة المخزنة",
    "filteringlabel": "علامة التصفية",
    "metricdefinition": "تعريف المقياس",
    "tasktemplate": "قالب المهمة",
    "task": "المهمة",
    "occurrence": "الحدوث",
    "campaign": "الحملة",
    "finding": "الاكتشاف",
    "observation": "الملاحظة",
    "accreditation": "الاعتماد",
    "genericcollection": "المجموعة العامة",
    "fearedevent": "الحدث المخيف",
    "roto": "مصادر المخاطر والأهداف",
    "attackpath": "مسار الهجوم",
    "strategicscenario": "السيناريو الاستراتيجي",
    "ebiosrmstudy": "دراسة EBIOS RM",
    "databreach": "خرق البيانات",
    "datatransfer": "نقل البيانات",
    "rightrequest": "طلب الحق",
    "quantitativeriskstudy": "دراسة المخاطر الكمية",
    "quantitativeriskscenario": "سيناريو المخاطر الكمي",
    "quantitativeriskhypothesis": "فرضية المخاطر الكمية",
    "businessimpactanalysis": "تحليل الأثر على الأعمال",
}


def camel_to_words(key: str) -> str:
    """Convert camelCase key to space-separated lowercase words."""
    s = re.sub(r'([A-Z])', r' \1', key).strip().lower()
    # also split on _ and -
    s = re.sub(r'[_\-]', ' ', s)
    return s


def translate(en_value: str) -> str:
    """Best-effort translation of an English UI string to Arabic."""
    if not en_value or not isinstance(en_value, str):
        return en_value

    lower = en_value.lower().strip()

    # 1. Full-phrase exact match
    if lower in PHRASES:
        return PHRASES[lower]

    # 2. Try CRUD-prefix + model pattern on the English VALUE
    for verb_en, verb_ar in AR_VERBS.items():
        if lower.startswith(verb_en + " "):
            rest = lower[len(verb_en):].strip()
            rest_nospace = rest.replace(" ", "")
            if rest in PHRASES:
                return f"{verb_ar} {PHRASES[rest]}"
            if rest_nospace in AR_MODELS:
                return f"{verb_ar} {AR_MODELS[rest_nospace]}"
            # word-by-word substitution of the rest
            translated = rest
            for phrase, ar in sorted(PHRASES.items(), key=lambda x: -len(x[0])):
                if phrase in translated:
                    translated = translated.replace(phrase, ar)
                    break
            if translated != rest:
                return f"{verb_ar} {translated}"

    # 3. Try CRUD-prefix + model on the KEY itself (camelCase → Arabic)
    return en_value  # fallback: keep English


def translate_by_key(key: str, en_value: str) -> str:
    """Translate using the key pattern (CRUD + model) then the value."""
    # First try by English value
    result = translate(en_value)
    if result != en_value:
        return result

    lower_key = key.lower()
    lower_key_nospace = re.sub(r'[_\-]', '', lower_key)

    # Try CRUD prefix on camelCase key
    for verb_en, verb_ar in AR_VERBS.items():
        if lower_key_nospace.startswith(verb_en):
            model_part = lower_key_nospace[len(verb_en):]
            if model_part in AR_MODELS:
                return f"{verb_ar} {AR_MODELS[model_part]}"
            # direct phrase lookup on model_part
            if model_part in PHRASES:
                return f"{verb_ar} {PHRASES[model_part]}"

    # Last resort: look up key directly in models dict
    if lower_key_nospace in AR_MODELS:
        return AR_MODELS[lower_key_nospace]

    # Return English value unchanged
    return en_value


def load_json_no_dup(path: str) -> dict:
    """Load JSON allowing duplicate keys (last value wins)."""
    with open(path, encoding="utf-8") as f:
        return json.load(f, object_pairs_hook=lambda pairs: dict(pairs))


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    en_path = os.path.join(base, "frontend", "messages", "en.json")
    ar_path = os.path.join(base, "frontend", "messages", "ar.json")

    en_data = load_json_no_dup(en_path)
    ar_data = load_json_no_dup(ar_path)

    missing_keys = [k for k in en_data if k not in ar_data]
    print(f"Missing keys: {len(missing_keys)}")

    translated = 0
    kept_english = 0
    skipped_complex = 0

    for key in missing_keys:
        en_val = en_data[key]
        if isinstance(en_val, list):
            # Complex plural form – keep the EN plural structure unchanged;
            # Arabic plurals need manual crafting so we copy the EN version.
            ar_data[key] = en_val
            skipped_complex += 1
        elif isinstance(en_val, str):
            ar_val = translate_by_key(key, en_val)
            ar_data[key] = ar_val
            if ar_val != en_val:
                translated += 1
            else:
                kept_english += 1
        else:
            ar_data[key] = en_val

    # Also fix the 8 known English stubs already in ar.json
    stubs = {
        "fileTooLarge": "الملف كبير جداً",
        "invalidFileFormat": "صيغة ملف غير صالحة",
        "invalidCompatMode": "وضع توافق غير صالح",
        "invalidExcelFile": "ملف Excel غير صالح",
        "processingTimeout": "انتهت مهلة المعالجة",
        "maliciousFileDetected": "تم اكتشاف ملف ضار",
        "serverConfigurationError": "خطأ في تهيئة الخادم",
        "libraryLoadFailed": "فشل تحميل المكتبة",
    }
    for k, v in stubs.items():
        if k in ar_data:
            ar_data[k] = v

    print(f"  Translated to Arabic  : {translated}")
    print(f"  Kept in English       : {kept_english}")
    print(f"  Complex plurals copied: {skipped_complex}")
    print(f"  English stubs fixed   : {len(stubs)}")

    # Preserve $schema key at the top
    schema = ar_data.pop("$schema", None)
    ordered = {}
    if schema:
        ordered["$schema"] = schema
    ordered.update(ar_data)

    with open(ar_path, "w", encoding="utf-8") as f:
        json.dump(ordered, f, ensure_ascii=False, indent="\t")
        f.write("\n")

    print(f"\nWritten to {ar_path}")
    total_ar = len(ordered)
    print(f"Total keys in ar.json now: {total_ar}")


if __name__ == "__main__":
    main()
