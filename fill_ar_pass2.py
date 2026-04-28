#!/usr/bin/env python3
"""
Second-pass: translate keys that were left in English after the first pass.
Adds a richer dictionary covering privacy, BIA, analytics, validation flows, etc.
"""
import json
import re
import os

EXTRA_PHRASES = {
    # ── Language names ────────────────────────────────────────────────────────
    "hungarian": "الهنغارية", "ukrainian": "الأوكرانية",
    "greek": "اليونانية", "turkish": "التركية",
    "chinese (simplified)": "الصينية المبسطة",
    "lithuanian": "الليتوانية", "czech": "التشيكية",
    "slovak": "السلوفاكية", "croatian": "الكرواتية",
    "romanian": "الرومانية", "bulgarian": "البلغارية",
    "slovenian": "السلوفينية", "estonian": "الإستونية",
    "latvian": "اللاتفية", "serbian": "الصربية",
    "catalan": "الكاتالانية", "danish": "الدنماركية",
    "swedish": "السويدية", "norwegian": "النرويجية",
    "finnish": "الفنلندية", "dutch": "الهولندية",
    "portuguese": "البرتغالية", "italian": "الإيطالية",
    "spanish": "الإسبانية", "french": "الفرنسية",
    "german": "الألمانية", "english": "الإنجليزية",
    "arabic": "العربية", "chinese": "الصينية",
    "japanese": "اليابانية", "korean": "الكورية",
    "russian": "الروسية", "polish": "البولندية",

    # ── Month abbreviations ───────────────────────────────────────────────────
    "jan": "يناير", "feb": "فبراير", "mar": "مارس",
    "apr": "أبريل", "may": "مايو", "jun": "يونيو",
    "jul": "يوليو", "aug": "أغسطس", "sep": "سبتمبر",
    "oct": "أكتوبر", "nov": "نوفمبر", "dec": "ديسمبر",

    # ── Validation flow ───────────────────────────────────────────────────────
    "validation": "التحقق", "validations": "التحققات",
    "validations management": "إدارة التحققات",
    "request a validation": "طلب تحقق",
    "validation approved successfully": "تمت الموافقة على التحقق بنجاح",
    "validation rejected successfully": "تم رفض التحقق بنجاح",
    "validation revoked successfully": "تم سحب التحقق بنجاح",
    "validation dropped successfully": "تم إسقاط التحقق بنجاح",
    "validation resubmitted successfully": "تمت إعادة إرسال التحقق بنجاح",
    "changes requested successfully": "تم طلب التغييرات بنجاح",
    "accept notes": "ملاحظات القبول",
    "rejection notes": "ملاحظات الرفض",
    "revocation notes": "ملاحظات السحب",
    "changes request notes": "ملاحظات طلب التغييرات",
    "drop notes": "ملاحظات الإسقاط",
    "resubmission notes": "ملاحظات إعادة الإرسال",
    "request changes": "طلب تغييرات",
    "resubmit": "إعادة الإرسال",
    "requester": "مقدم الطلب",
    "only the requester can perform actions on this validation":
        "يمكن لمقدم الطلب فقط تنفيذ إجراءات على هذا التحقق",
    "only the assigned approver can modify this validation":
        "يمكن للمعتمد المعيَّن فقط تعديل هذا التحقق",
    "validation deadline": "الموعد النهائي للتحقق",
    "request validation": "طلب تحقق",
    "request notes": "ملاحظات الطلب",
    "approver observation": "ملاحظة المعتمد",
    "allow self-validation": "السماح بالتحقق الذاتي",
    "when enabled, users can approve their own validation requests":
        "عند التفعيل، يمكن للمستخدمين اعتماد طلبات التحقق الخاصة بهم",

    # ── BIA / Resilience ──────────────────────────────────────────────────────
    "bia": "تحليل الأثر على الأعمال",
    "bia assessments": "تقييمات تحليل الأثر على الأعمال",
    "bia thresholds": "عتبات تحليل الأثر على الأعمال",
    "escalation threshold": "عتبة التصعيد",
    "escalation thresholds": "عتبات التصعيد",
    "asset domain": "نطاق الأصول",
    "impact on": "التأثير على",
    "point in time": "نقطة زمنية",
    "quantified impact": "التأثير المحدد كمياً",
    "qualitative impact": "التأثير النوعي",
    "unit": "الوحدة",
    "rationale": "المبرر",
    "recovery documented": "الاسترداد موثق",
    "recovery tested": "الاسترداد مختبر",
    "recovery targets met": "أهداف الاسترداد محققة",
    "recovery insights": "رؤى الاسترداد",
    "recovery indicators": "مؤشرات الاسترداد",
    "recovery capabilities": "قدرات الاسترداد",
    "impact over time": "التأثير عبر الزمن",
    "assets management": "إدارة الأصول",
    "asset dependencies": "تبعيات الأصول",
    "dependencies chain": "سلسلة التبعيات",
    "no dependencies found for this asset": "لم يتم العثور على تبعيات لهذا الأصل",
    "extra dependencies": "تبعيات إضافية",
    "rto": "هدف وقت الاسترداد (RTO)",
    "rpo": "هدف نقطة الاسترداد (RPO)",
    "mtd": "الحد الأقصى للتوقف المسموح به (MTD)",
    "recovery time objective": "هدف وقت الاسترداد",
    "recovery point objective": "هدف نقطة الاسترداد",
    "maximum tolerable downtime": "الحد الأقصى للتوقف المسموح به",
    "disaster recovery objectives": "أهداف التعافي من الكوارث",
    "is critical": "حرج",
    "is business function": "وظيفة أعمال",
    "support assets": "يعتمد على ↓",
    "underlying dependencies": "التبعيات الأساسية",
    "overridden capabilities": "قدرات مُتجاوَزة",
    "scoped asset": "أصل في النطاق",

    # ── DORA ──────────────────────────────────────────────────────────────────
    "licensed activity": "النشاط المرخص",
    "criticality assessment": "تقييم الأهمية الحرجة",
    "criticality justification": "مبرر الأهمية الحرجة",
    "discontinuing impact": "أثر التوقف",
    "dora": "DORA",

    # ── Privacy / GDPR ────────────────────────────────────────────────────────
    "metrology": "قياسية",
    "track metrics, kpis, and visualize them on customizable dashboards":
        "تتبع المقاييس ومؤشرات الأداء وعرضها على لوحات تحكم قابلة للتخصيص",
    "data processing activities (gdpr) and data breach incidents and notifications":
        "أنشطة معالجة البيانات (GDPR) وحوادث خرق البيانات وإشعاراتها",
    "processings": "عمليات المعالجة",
    "processings register": "سجل عمليات المعالجة",
    "purpose": "الغرض", "purposes": "الأغراض",
    "personal data": "البيانات الشخصية",
    "data subject": "موضوع البيانات",
    "data subjects": "موضوعات البيانات",
    "data recipient": "مستلم البيانات",
    "data recipients": "مستلمو البيانات",
    "data contractor": "مقاول البيانات",
    "data contractors": "مقاولو البيانات",
    "deletion policy": "سياسة الحذف",
    "retention policy": "سياسة الاحتفاظ",
    "retention": "الاحتفاظ",
    "is sensitive": "حساس",
    "legal basis": "الأساس القانوني",
    "article 9 condition": "شرط المادة 9",
    "transfer mechanism": "آلية النقل",
    "adequacy decision (art. 45)": "قرار الكفاية (المادة 45)",
    "appropriate safeguards (art. 46)": "الضمانات المناسبة (المادة 46)",
    "binding corporate rules (art. 47)": "قواعد الشركات الملزمة (المادة 47)",
    "derogation for specific situations (art. 49)": "الاستثناء للحالات الخاصة (المادة 49)",
    "documentation link": "رابط التوثيق",
    "dpia required": "تقييم أثر حماية البيانات مطلوب",
    "relationship type": "نوع العلاقة",
    "country": "الدولة",
    "guarantees": "الضمانات",
    "information channel": "قناة المعلومات",
    "usage channel": "قناة الاستخدام",
    "reference to dpia": "مرجع تقييم أثر حماية البيانات",
    "has sensitive personal data": "يحتوي على بيانات شخصية حساسة",
    "processing nature": "طبيعة المعالجة",
    "nature": "الطبيعة",
    "personal data categories identified": "فئات البيانات الشخصية المحددة",
    "documented processings": "عمليات المعالجة الموثقة",
    "consent": "الموافقة",
    "contract performance": "تنفيذ العقد",
    "legal obligation": "الالتزام القانوني",
    "vital interests": "المصالح الحيوية",
    "public interest": "المصلحة العامة",
    "legitimate interests": "المصالح المشروعة",
    "explicit consent for special categories": "موافقة صريحة للفئات الخاصة",
    "employment and social security law": "قانون العمل والضمان الاجتماعي",
    "vital interests (subject physically/legally incapable)":
        "المصالح الحيوية (الموضوع غير قادر جسدياً/قانونياً)",
    "processing by non-profit organization": "المعالجة بواسطة منظمة غير ربحية",
    "data made publicly available by the data subject":
        "بيانات متاحة للعموم من قِبل موضوع البيانات",
    "establishment, exercise or defense of legal claims":
        "إثبات أو ممارسة أو الدفاع عن المطالبات القانونية",
    "substantial public interest": "مصلحة عامة جوهرية",
    "preventive or occupational medicine": "الطب الوقائي أو مهني",
    "public health": "الصحة العامة",
    "archiving, research or statistical purposes": "أغراض الأرشفة أو البحث أو الإحصاء",
    "child consent with parental authorization": "موافقة الطفل بإذن الوالدين",
    "transfer based on adequacy decision": "النقل بناءً على قرار الكفاية",
    "transfer subject to appropriate safeguards": "النقل وفق ضمانات مناسبة",
    "transfer subject to binding corporate rules": "النقل وفق قواعد الشركات الملزمة",
    "transfer based on derogation for specific situations": "النقل بناءً على استثناء للحالات الخاصة",
    "consent and contract": "الموافقة والعقد",

    # ── Analytics / Dashboard ─────────────────────────────────────────────────
    "metrology description": "تتبع المقاييس ومؤشرات الأداء وعرضها على لوحات تحكم قابلة للتخصيص",
    "scores & metrics": "النتائج والمقاييس",
    "radar comparison": "مقارنة راداري",
    "compliance by section": "الامتثال حسب القسم",
    "controls coverage": "تغطية الضوابط",
    "with controls": "مع ضوابط",
    "without controls": "بدون ضوابط",
    "coverage": "التغطية",
    "control status distribution": "توزيع حالة الضوابط",
    "evidence coverage": "تغطية الأدلة",
    "with evidence": "مع أدلة",
    "without evidence": "بدون أدلة",
    "direct only": "مباشر فقط",
    "indirect only": "غير مباشر فقط",
    "direct & indirect": "مباشر وغير مباشر",
    "evidence status": "حالة الدليل",
    "threats overview": "نظرة عامة على التهديدات",
    "unique threats": "تهديدات فريدة",
    "affected requirements": "المتطلبات المتأثرة",
    "exceptions overview": "نظرة عامة على الاستثناءات",
    "total exceptions": "إجمالي الاستثناءات",
    "compliance over time": "الامتثال عبر الزمن",
    "implementation groups breakdown": "تحليل مجموعات التنفيذ",
    "mapping projection": "توقعات رسم الخرائط",
    "no implementation groups": "لا تحدد هذه الإطار مجموعات تنفيذ",
    "no mapping targets": "لا توجد أهداف تعيين متاحة لهذا الإطار",
    "comparable audits": "عمليات التدقيق القابلة للمقارنة",
    "avg. score": "متوسط النتيجة",
    "avg. doc. score": "متوسط نتيجة التوثيق",
    "advanced analytics": "التحليلات المتقدمة",
    "coverage percent": "نسبة التغطية",
    "implementation groups": "مجموعات التنفيذ",
    "kanban mode": "وضع كانبان",
    "modes": "الأوضاع",
    "scoring assistant description":
        "تسجيل سيناريو مخاطر باستخدام مصفوفة مخاطر بناءً على عوامل التهديد والثغرات",
    "reference scale": "المقياس المرجعي",

    # ── Assignment ────────────────────────────────────────────────────────────
    "assignments": "التعيينات",
    "respondent view": "عرض المستجيب",
    "respondent": "المستجيب",
    "assignment/respondent mode": "وضع التعيين/المستجيب",
    "select requirements to assign": "اختر المتطلبات للتعيين",
    "select requirements to include in a new assignment":
        "اختر المتطلبات لتضمينها في تعيين جديد",
    "make sure that the assigned users have access to the domain of this audit":
        "تأكد من أن المستخدمين المعيَّنين لديهم وصول إلى نطاق هذا التدقيق",
    "select all available": "تحديد كل المتاح",
    "expand all": "توسيع الكل",
    "collapse all": "طي الكل",
    "click to select": "انقر للتحديد",
    "already assigned": "معيَّن بالفعل",
    "new assignment": "تعيين جديد",
    "assign to": "عيِّن إلى",
    "search for an actor...": "ابحث عن فاعل...",
    "selected requirements": "المتطلبات المحددة",
    "updating...": "جارٍ التحديث...",
    "creating...": "جارٍ الإنشاء...",
    "select an actor and at least one requirement":
        "اختر فاعلاً ومتطلباً واحداً على الأقل",
    "existing assignments": "التعيينات الموجودة",
    "no assignments created yet": "لم يتم إنشاء تعيينات بعد",
    "assignment created successfully": "تم إنشاء التعيين بنجاح",
    "assignment updated successfully": "تم تحديث التعيين بنجاح",
    "assignment deleted successfully": "تم حذف التعيين بنجاح",
    "assignment creation failed": "فشل إنشاء التعيين",
    "assignment update failed": "فشل تحديث التعيين",
    "assignment deletion failed": "فشل حذف التعيين",
    "click to view requirements": "انقر لعرض المتطلبات",
    "available": "متاح",
    "current user": "المستخدم الحالي",
    "filter by actor": "التصفية حسب الفاعل",
    "no audit assignments": "لا توجد عمليات تدقيق معيَّنة لك بعد",
    "no audits assigned to you yet, or a permission is missing":
        "لم يتم تعيين عمليات تدقيق لك بعد، أو صلاحية مفقودة",
    "start assessment": "بدء التقييم",
    "continue assessment": "متابعة التقييم",
    "about assignments": "حول التعيينات",
    "requirement assignment": "تعيين المتطلب",
    "requirement assignments": "تعيينات المتطلبات",

    # ── Audit / Comparison ────────────────────────────────────────────────────
    "clone audit": "استنساخ التدقيق",
    "compare to": "مقارنة مع",
    "select audit to compare with": "اختر التدقيق للمقارنة",
    "audits with the same framework and perimeter are prioritized at the top.":
        "تُعطى الأولوية لعمليات التدقيق ذات نفس الإطار والمحيط في القمة.",
    "audits comparison": "مقارنة عمليات التدقيق",
    "back to base audit": "العودة إلى التدقيق الأساسي",
    "base audit": "التدقيق الأساسي",
    "comparison audit": "تدقيق المقارنة",
    "more comparison features coming soon": "المزيد من ميزات المقارنة قريباً",
    "back to table": "العودة إلى الجدول",
    "compliance assessment comparison": "مقارنة تقييمات الامتثال",
    "requirement differences": "اختلافات المتطلبات",
    "with differences": "مع اختلافات",
    "audits with same framework prioritized":
        "تُعطى الأولوية لعمليات التدقيق ذات نفس الإطار",

    # ── Financial ─────────────────────────────────────────────────────────────
    "financial settings": "الإعدادات المالية",
    "currency": "العملة",
    "select the default currency for financial units": "اختر العملة الافتراضية للوحدات المالية",
    "daily rate": "المعدل اليومي",
    "people-days conversion rate for cost calculation":
        "معدل تحويل الأيام البشرية لحساب التكلفة",

    # ── Mapping ───────────────────────────────────────────────────────────────
    "mapping max depth": "الحد الأقصى لعمق رسم الخرائط",
    "maximum depth for exploring framework mapping relationships (2-5). higher values find more indirect mappings but take longer to compute.":
        "الحد الأقصى للعمق لاستكشاف علاقات تعيين الإطار (2-5). القيم الأعلى تجد تعيينات غير مباشرة أكثر لكن تستغرق وقتاً أطول.",

    # ── Select/Filter options ─────────────────────────────────────────────────
    "select audits": "اختر عمليات التدقيق",
    "select ebios rm studies": "اختر دراسات EBIOS RM",
    "select entity assessments": "اختر تقييمات الكيانات",
    "select documents": "اختر الوثائق",
    "select crq studies": "اختر دراسات CRQ",
    "select risk assessments": "اختر تقييمات المخاطر",
    "select findings follow-ups": "اختر متابعات الاكتشافات",
    "associated ebios rm studies": "دراسات EBIOS RM المرتبطة",
    "associated crq studies": "دراسات CRQ المرتبطة",
    "associated policies": "السياسات المرتبطة",
    "associated security exceptions": "الاستثناءات الأمنية المرتبطة",
    "checklist": "قائمة التحقق",
    "associated objects": "الكائنات المرتبطة",
    "accreditation status": "حالة الاعتماد",
    "accreditation category": "فئة الاعتماد",
    "entities ecosystem": "بيئة الكيانات",
    "management of third-party entities and their representatives, contracts, solutions and assessments.":
        "إدارة الكيانات الخارجية وممثليها والعقود والحلول والتقييمات.",
    "default criticality": "الأهمية الحرجة الافتراضية",
    "third-party solutions": "حلول الطرف الثالث",
    "beneficiary": "المستفيد",
    "parent entity": "الكيان الأصل",
    "parent entity for branch or subsidiary relationships":
        "الكيان الأصل لعلاقات الفروع أو الشركات التابعة",
    "legal identifiers": "المعرفات القانونية",
    "add identifier": "إضافة معرّف",
    "no legal identifiers added yet": "لم تتم إضافة معرّفات قانونية بعد",
    "identifier type": "نوع المعرّف",
    "identifier value": "قيمة المعرّف",
    "invalid identifier": "معرّف غير صالح",
    "lei must be exactly 20 characters long": "يجب أن يكون LEI 20 حرفاً بالضبط",
    "enter identifier value...": "أدخل قيمة المعرّف...",
    "remove identifier": "إزالة المعرّف",
    "assigned to": "معيَّن إلى",
    "disk space": "مساحة القرص",
    "disk used": "المساحة المستخدمة",

    # ── Workflow / General UI ──────────────────────────────────────────────────
    "workflows": "سير العمل",
    "linked models": "الكائنات المرتبطة",
    "associated contracts": "العقود المرتبطة",
    "associated tasks": "المهام المرتبطة",
    "associated objects": "الكائنات المرتبطة",
    " ": " ",
    "associated controls": "الضوابط المرتبطة",
    "associated purposes": "الأغراض المرتبطة",
    "associated personal data": "البيانات الشخصية المرتبطة",
    "associated data subjects": "موضوعات البيانات المرتبطة",
    "associated data transfers": "عمليات نقل البيانات المرتبطة",
    "associated data recipients": "مستلمو البيانات المرتبطون",
    "associated data contractors": "مقاولو البيانات المرتبطون",
    "associated purposes": "الأغراض المرتبطة",

    # ── Settings ─────────────────────────────────────────────────────────────
    "interface": "الواجهة",
    "aggregate scenarios on risk matrices": "تجميع السيناريوهات في مصفوفات المخاطر",
    "notifications settings": "إعدادات الإشعارات",
    "you do not have the permission to import a domain. please contact your administrator.":
        "ليس لديك صلاحية استيراد نطاق. يرجى التواصل مع المسؤول.",
    "general settings updated": "تم تحديث الإعدادات العامة",
    "experimental features": "الميزات التجريبية",
    "additional and experimental features.": "ميزات إضافية وتجريبية.",
    "enforce multi-factor authentication": "فرض المصادقة متعددة العوامل",
    "set up multi-factor authentication": "إعداد المصادقة متعددة العوامل",
    "show warning external links help text": "عرض تحذير الروابط الخارجية",
    "external link warning": "تحذير الرابط الخارجي",
    "you are about to leave the app and access an external website:":
        "أنت على وشك مغادرة التطبيق والوصول إلى موقع خارجي:",
    "please verify this is the correct destination before continuing.":
        "يرجى التحقق من صحة الوجهة قبل المتابعة.",
    "data wizard": "معالج البيانات",
    "x-rays": "الأشعة السينية (X-Rays)",
    "x-rays is a very useful tool to detect inconsistencies across your assessments for each perimeter.":
        "X-Rays أداة مفيدة جداً لاكتشاف التناقضات في تقييماتك لكل محيط.",
    "analyzing data...": "جارٍ تحليل البيانات...",
    "issue type": "نوع المشكلة",
    "issue types": "أنواع المشكلات",
    "could not find attachment file. please contact your administrator.":
        "تعذر العثور على ملف المرفق. يرجى التواصل مع المسؤول.",
    "can't load the backup, the version of the backup is invalid":
        "تعذر تحميل النسخ الاحتياطي، إصدار النسخة الاحتياطية غير صالح",
    "confirm by typing 'yes' below:": "أكِّد بكتابة 'yes' أدناه:",
    "type 'yes' to confirm": "اكتب 'yes' للتأكيد",
    "a user with this email already exists as an internal user and cannot be converted to a third-party representative.":
        "مستخدم بهذا البريد الإلكتروني موجود بالفعل كمستخدم داخلي ولا يمكن تحويله إلى ممثل طرف ثالث.",
    "covers daily and periodic grc activities: task management, findings follow-up, security incidents, and inconsistency checks via x-rays.":
        "يغطي أنشطة GRC اليومية والدورية: إدارة المهام ومتابعة الاكتشافات وحوادث الأمن وفحوصات التناسق عبر X-Rays.",
    "you have only {days_left} days before the end of your license.":
        "لديك {days_left} أيام فقط قبل انتهاء ترخيصك.",

    # ── Various GRC UI ────────────────────────────────────────────────────────
    "compliance includes compliant and partially compliant requirements":
        "يشمل الامتثال المتطلبات الممتثلة والممتثلة جزئياً",
    "no controls in this category": "لا توجد ضوابط في هذه الفئة",
    "drop here to change status": "أفلت هنا لتغيير الحالة",
    "is marked as an existing control but its status is not active":
        "محدد كضابط موجود لكن حالته غير نشطة",
    "appears in both existing and additional controls":
        "يظهر في كلٍّ من الضوابط الموجودة والإضافية",
    "requirement is marked compliant but has no evidence attached (direct or indirect)":
        "المتطلب محدد كممتثل لكن ليس له دليل مرفق (مباشر أو غير مباشر)",
    "treatment progress": "تقدم المعالجة",
    "closing date": "تاريخ الإغلاق",
    "actual date the objective was closed or completed":
        "التاريخ الفعلي لإغلاق الهدف أو اكتماله",
    "additional notes and comments in markdown format":
        "ملاحظات وتعليقات إضافية بتنسيق Markdown",
    "tasks status": "حالة المهام",
    "as excel": "كـ Excel",
    "as word": "كـ Word",
    "export pdf": "تصدير PDF",
    "excel (beta)": "Excel (تجريبي)",
    "generating": "جارٍ الإنشاء",
    "as markdown": "كـ Markdown",
    "no actions available for this status": "لا إجراءات متاحة لهذه الحالة",
    "reference control help text":
        "يعمل كقالب ويتجاوز قيم بعض الحقول (الاسم، ref_id، الفئة، وظيفة CSF، إلخ)",
    "enclave": "جيب معزول",
    "include enclaves": "تضمين الجيوب المعزولة",
    "type to search...": "اكتب للبحث...",
    "searching...": "جارٍ البحث...",
    "is a third party": "طرف ثالث",
    "revision number of the audit": "رقم مراجعة التدقيق",
    "planning tip": "تلميح: حدِّث تاريخ البدء والتقدم لضوابطك المطبقة لرؤيتها هنا.",
    "security controls implemented for this asset":
        "ضوابط الأمن المطبقة على هذا الأصل",
    "applied controls distribution": "توزيع الضوابط المطبقة",
    "affected scenarios": "السيناريوهات المتأثرة",
    "antecedent scenarios": "السيناريوهات السابقة",
    "no antecedent scenarios": "لا توجد سيناريوهات سابقة",
    "no assignment created yet": "لم يُنشأ أي تعيين بعد",
    "custom/external library": "مكتبة مخصصة/خارجية",
    "you can import your library defined in ciso assistant format or external ones like cis or ccm. libraries can be directly imported as excel file or converted using the external toolbox.":
        "يمكنك استيراد مكتبتك المحددة بتنسيق CISO Assistant أو الخارجية مثل CIS أو CCM. يمكن استيراد المكتبات مباشرة كملف Excel أو تحويلها باستخدام صندوق الأدوات الخارجي.",
    "extra-small": "صغير جداً",
    "compliance & risk management": "الامتثال وإدارة المخاطر",
    "enter your observation": "أدخل ملاحظتك",
    "this will be sent to the approver for validation.":
        "سيُرسل هذا إلى المعتمد للتحقق.",
    "this risk acceptance has not yet been submitted.":
        "لم يتم إرسال قبول المخاطر هذا بعد.",
    "approver required before submitting.": "المعتمد مطلوب قبل الإرسال.",
    ". this user has no default permissions. remember to edit their user groups":
        ". هذا المستخدم ليس له صلاحيات افتراضية. تذكر تعديل مجموعات المستخدمين.",
    "users have no default permission; remember to edit their user groups":
        "المستخدمون ليس لديهم صلاحيات افتراضية؛ تذكر تعديل مجموعات المستخدمين.",
    "failed to submit": "فشل الإرسال",
    "a new version of the library has been stored. please trigger the update to apply it.":
        "تم تخزين إصدار جديد من المكتبة. يرجى تشغيل التحديث لتطبيقه.",
    "not set": "--",
    "third-party respondent": "مستجيب الطرف الثالث",
    "information": "معلومات",
    "unaffected": "غير متأثر",
    "not exploitable": "غير قابل للاستغلال",
    "existing measures": "التدابير الموجودة",
    "score:": "النتيجة:",
    "processing": "المعالجة",
    "select controls": "اختر الضوابط",
    "hour": "ساعة", "minute": "دقيقة",
    "seconds": "ثواني", "milliseconds": "ميلي ثانية",
    "events history": "سجل الأحداث",
    "risk option helper": "يمكنك مراجعة تعريفات مستوياتك بالنقر على المصفوفة أعلاه (يفتح في علامة تبويب جديدة)",
    "support assets": "يعتمد على ↓",
    "other assets supported by this one (upstream)": "الأصول الأخرى التي يدعمها هذا الأصل (مصدر علوي)",
    "specifiy the assets supporting this one (downstream)": "حدد الأصول الداعمة لهذا الأصل (مصدر سفلي)",
    "tip: update the start date and progress of your applied controls to see them here.":
        "تلميح: حدّث تاريخ البدء والتقدم لضوابطك المطبقة لرؤيتها هنا.",
    "library add help text":
        "يمكنك استيراد مكتبتك بتنسيق CISO Assistant أو الخارجية مثل CIS أو CCM.",
    "solutions associated with this asset": "الحلول المرتبطة بهذا الأصل",
    "third party description": "إدارة الكيانات الخارجية وممثليها والعقود والحلول والتقييمات.",
    "p1": "P1", "p2": "P2", "p3": "P3", "p4": "P4",
    "select compliance assessments": "اختر تقييمات الامتثال",
    "scoring assistant": "مساعد التسجيل",
    "what would you like to do?": "ماذا تريد أن تفعل؟",
    "how would you like to proceed?": "كيف تريد المتابعة؟",
    "are you sure?": "هل أنت متأكد؟",
    "confirm action": "تأكيد الإجراء",
    "this action cannot be undone": "لا يمكن التراجع عن هذا الإجراء",
    "changes saved": "تم حفظ التغييرات",
    "no changes detected": "لم يتم اكتشاف أي تغييرات",
    "field required": "الحقل مطلوب",
    "invalid value": "قيمة غير صالحة",
    "value too long": "القيمة طويلة جداً",
    "value too short": "القيمة قصيرة جداً",
    "out of range": "خارج النطاق",
    "association": "الارتباط", "associations": "الارتباطات",
    "no data available": "لا توجد بيانات متاحة",
    "click to copy": "انقر للنسخ",
    "copied to clipboard": "تم النسخ إلى الحافظة",
    "read only": "للقراءة فقط",
    "write": "كتابة", "read": "قراءة",
    "access rights": "حقوق الوصول",
    "not yet implemented": "لم يتم التنفيذ بعد",
    "coming soon": "قريباً",
    "beta": "تجريبي",
    "new": "جديد",
    "updated": "محدَّث",
    "deprecated": "مهمل",
    "experimental": "تجريبي",
    "feature flags": "علامات الميزات",
    "enable feature": "تفعيل الميزة",
    "disable feature": "تعطيل الميزة",
    "context": "السياق",
    "scope": "النطاق",
    "in scope": "في النطاق",
    "out of scope": "خارج النطاق",
    "associated metric instances": " ",
    "assetsindependencies": "تبعيات الأصول",
    "solutionslinkedtoassethelptext": "الحلول المرتبطة بهذا الأصل",
    "supportedassetshelptext": "الأصول الأخرى المدعومة من هذا الأصل",
    "supportingassetshelptext": "الأصول الداعمة لهذا الأصل",
    "overriddenchilrencapabilitieshelptext":
        "إذا ذُكرت في هذه القائمة، ستتجاوز القدرات من هذا الأصل تلك الخاصة بأصوله الداعمة",
    "operationsdescription":
        "يغطي أنشطة GRC اليومية والدورية: إدارة المهام ومتابعة الاكتشافات وحوادث الأمن وفحوصات التناسق",
}


def load_json_no_dup(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f, object_pairs_hook=lambda pairs: dict(pairs))


def best_translate(key: str, en_val: str) -> str:
    lower = en_val.lower().strip()
    if lower in EXTRA_PHRASES:
        return EXTRA_PHRASES[lower]
    # camelCase → lower phrase
    lower_key = key.lower()
    if lower_key in EXTRA_PHRASES:
        return EXTRA_PHRASES[lower_key]
    return en_val


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    en_path = os.path.join(base, "frontend", "messages", "en.json")
    ar_path = os.path.join(base, "frontend", "messages", "ar.json")

    en_data = load_json_no_dup(en_path)
    ar_data = load_json_no_dup(ar_path)

    fixed = 0
    for key, ar_val in list(ar_data.items()):
        if key not in en_data:
            continue
        en_val = en_data[key]
        if not isinstance(en_val, str) or not isinstance(ar_val, str):
            continue
        # Still in English?
        if ar_val == en_val:
            new_val = best_translate(key, en_val)
            if new_val != en_val:
                ar_data[key] = new_val
                fixed += 1

    print(f"Second-pass: fixed {fixed} additional keys")

    # Preserve $schema at top
    schema = ar_data.pop("$schema", None)
    ordered = {}
    if schema:
        ordered["$schema"] = schema
    ordered.update(ar_data)

    with open(ar_path, "w", encoding="utf-8") as f:
        json.dump(ordered, f, ensure_ascii=False, indent="\t")
        f.write("\n")

    # Report remaining English
    en_data2 = load_json_no_dup(en_path)
    ar_data2 = load_json_no_dup(ar_path)
    still_en = [k for k in ar_data2 if k in en_data2
                and isinstance(en_data2[k], str)
                and ar_data2[k] == en_data2[k]
                and not k.startswith("$")]
    print(f"Still in English: {len(still_en)}")
    print(f"Written to {ar_path}")


if __name__ == "__main__":
    main()
