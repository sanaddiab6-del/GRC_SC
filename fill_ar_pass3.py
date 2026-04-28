#!/usr/bin/env python3
"""
Third-pass: translate remaining English-value keys in ar.json.
Covers EBIOS RM, privacy, resilience, BIA, tour, analytics, and misc UI.
"""
import json
import os

DICT3 = {
    # ── Acronyms / pass-through ───────────────────────────────────────────────
    "eta": "ETA", "urn": "URN", "--": "--",
    "sso": "SSO", "pmbok": "PMBOK", "iam": "IAM", "crq": "CRQ",
    "p1": "P1", "p2": "P2", "p3": "P3", "p4": "P4",
    "time": "الوقت", "drop": "إسقاط",
    "custom name": "اسم مخصص",

    # ── Privacy data categories ────────────────────────────────────────────────
    "financial data": "البيانات المالية",
    "bank account information": "معلومات الحساب البنكي",
    "payment card information": "معلومات بطاقة الدفع",
    "transaction history": "سجل المعاملات",
    "salary information": "معلومات الراتب",
    "health data": "البيانات الصحية",
    "genetic data": "البيانات الجينية",
    "biometric data": "البيانات البيومترية",
    "racial or ethnic origin": "الأصل العرقي أو الإثني",
    "political opinions": "الآراء السياسية",
    "religious or philosophical beliefs": "المعتقدات الدينية أو الفلسفية",
    "trade union membership": "العضوية النقابية",
    "sexual orientation": "التوجه الجنسي",
    "sex life data": "بيانات الحياة الجنسية",
    "browsing history": "سجل التصفح",
    "search history": "سجل البحث",
    "cookie data": "بيانات ملفات تعريف الارتباط",
    "device information": "معلومات الجهاز",
    "ip address": "عنوان IP",
    "user behavior": "سلوك المستخدم",
    "employment details": "تفاصيل التوظيف",
    "education history": "السجل التعليمي",
    "professional qualifications": "المؤهلات المهنية",
    "work performance data": "بيانات الأداء الوظيفي",
    "family details": "تفاصيل الأسرة",
    "social network": "الشبكة الاجتماعية",
    "lifestyle information": "معلومات أسلوب الحياة",
    "correspondence content": "محتوى المراسلات",
    "messaging content": "محتوى الرسائل",
    "communication metadata": "بيانات وصفية للاتصالات",
    "government identifiers": "المعرفات الحكومية",
    "tax information": "معلومات الضرائب",
    "social security information": "معلومات الضمان الاجتماعي",
    "driver's license information": "معلومات رخصة القيادة",
    "passport information": "معلومات جواز السفر",
    "legal records": "السجلات القانونية",
    "criminal records": "السجلات الجنائية",
    "judicial data": "البيانات القضائية",
    "preferences": "التفضيلات",
    "opinions": "الآراء",
    "feedback": "التغذية الراجعة",
    "images and photos": "الصور والصور الفوتوغرافية",
    "voice recordings": "التسجيلات الصوتية",
    "video recordings": "التسجيلات المرئية",
    "basic identity information": "معلومات الهوية الأساسية",
    "identification numbers": "أرقام التعريف",
    "online identifiers": "المعرفات الإلكترونية",
    "location data": "بيانات الموقع",
    "contact details": "تفاصيل الاتصال",
    "address": "العنوان",
    "email address": "عنوان البريد الإلكتروني",
    "phone number": "رقم الهاتف",

    # ── Privacy data subjects ─────────────────────────────────────────────────
    "customer": "العميل",
    "prospect": "العميل المحتمل",
    "employee": "الموظف",
    "job applicant": "مقدم طلب توظيف",
    "contractor/supplier": "مقاول/مورد",
    "business partner": "شريك الأعمال",
    "website/application user": "مستخدم الموقع/التطبيق",
    "visitor": "الزائر",
    "child/minor": "طفل/قاصر",
    "vulnerable person": "شخص ضعيف",
    "general public": "عامة الناس",
    "internal team/department": "الفريق الداخلي/القسم",
    "subsidiary": "شركة تابعة",
    "parent company": "الشركة الأم",
    "affiliated entity": "كيان تابع",
    "data processor": "معالج البيانات",
    "cloud service provider": "مزود خدمة سحابية",
    "it service provider": "مزود خدمة تقنية المعلومات",
    "marketing agency": "وكالة التسويق",
    "payment processor": "معالج الدفع",
    "analytics provider": "مزود التحليلات",
    "distributor": "الموزع",
    "reseller": "إعادة البيع",
    "legal advisor": "المستشار القانوني",
    "accountant": "المحاسب",
    "consultant": "المستشار",
    "auditor": "المدقق",
    "regulatory authority": "الهيئة التنظيمية",
    "tax authority": "السلطة الضريبية",
    "law enforcement": "الجهات الأمنية",
    "government entity": "جهة حكومية",
    "court": "المحكمة",
    "joint controller": "متحكم مشترك",
    "individual recipient": "مستلم فردي",
    "sub-processor": "معالج فرعي",
    "independent controller": "متحكم مستقل",

    # ── Privacy processing operations ─────────────────────────────────────────
    "collection": "الجمع",
    "recording": "التسجيل",
    "structuring": "الهيكلة",
    "adaptation or alteration": "التكيف أو التعديل",
    "retrieval": "الاسترجاع",
    "consultation": "الاستشارة",
    "use": "الاستخدام",
    "disclosure by transmission": "الإفصاح بالإرسال",
    "dissemination or otherwise making available": "النشر أو الإتاحة بطريقة أخرى",
    "alignment or combination": "المواءمة أو الدمج",
    "restriction": "التقييد",
    "erasure or destruction": "المحو أو الإتلاف",

    # ── Privacy deletion policies ──────────────────────────────────────────────
    "automatic deletion": "الحذف التلقائي",
    "anonymization": "إخفاء الهوية",
    "deletion after manual review": "الحذف بعد المراجعة اليدوية",
    "user-requested deletion": "الحذف بطلب من المستخدم",
    "legal/regulatory hold": "الإمساك القانوني/التنظيمي",
    "partial deletion": "الحذف الجزئي",

    # ── Privacy status ─────────────────────────────────────────────────────────
    "draft": "مسودة",
    "in review": "قيد المراجعة",

    # ── Privacy other ─────────────────────────────────────────────────────────
    "contract and legitimate interests": "العقد والمصالح المشروعة",
    "other (specify in description)": "أخرى (حدد في الوصف)",
    "add personal data": "إضافة بيانات شخصية",
    "add data subject": "إضافة موضوع بيانات",
    "add data recipient": "إضافة مستلم بيانات",
    "associated data recipient": "مستلم البيانات المرتبط",
    "it can be a reference to a risk assessment, audit or external reference":
        "يمكن أن يكون مرجعاً لتقييم مخاطر أو تدقيق أو مرجع خارجي",

    # ── Data breach ───────────────────────────────────────────────────────────
    "data breaches by type": "خروقات البيانات حسب النوع",
    "requests by type": "الطلبات حسب النوع",
    "discovered on": "تاريخ الاكتشاف",
    "breach type": "نوع الخرق",
    "data breaches open": "خروقات البيانات المفتوحة",
    "no risk: breach tracking required.\nrisk: breach tracking required and authorities must be notified.\nhigh risk: breach tracking required, authorities and data subjects must be notified.":
        "لا مخاطر: يتطلب تتبع الخرق.\nمخاطر: يتطلب تتبع الخرق وإخطار السلطات.\nمخاطر عالية: يتطلب تتبع الخرق وإخطار السلطات وموضوعات البيانات.",
    "affected data subjects count": "عدد موضوعات البيانات المتأثرة",
    "affected processings": "عمليات المعالجة المتأثرة",
    "affected personal data": "البيانات الشخصية المتأثرة",
    "affected personal data count": "عدد البيانات الشخصية المتأثرة",
    "authorities": "السلطات",
    "authority notified on": "تاريخ إخطار السلطة",
    "authority notification reference": "مرجع إخطار السلطة",
    "data subjects notified on": "تاريخ إخطار موضوعات البيانات",
    "potential consequences": "العواقب المحتملة",
    "remediation measures": "تدابير المعالجة",
    "destruction": "الإتلاف",
    "loss": "الفقدان",
    "alteration": "التعديل",
    "unauthorized disclosure": "الإفصاح غير المصرح به",
    "unauthorized access": "الوصول غير المصرح به",
    "no risk": "لا مخاطر",
    "high risk": "مخاطر عالية",
    "discovered": "مكتشف",
    "authority notified": "تم إخطار السلطة",
    "data subjects notified": "تم إخطار موضوعات البيانات",
    "open requests": "الطلبات المفتوحة",
    "associated requests": "الطلبات المرتبطة",
    "request type": "نوع الطلب",
    "requested on": "تاريخ الطلب",
    "deletion": "الحذف",
    "rectification": "التصحيح",
    "access / extract": "الوصول / الاستخراج",
    "portability": "قابلية النقل",
    "objection": "الاعتراض",

    # ── EBIOS RM ──────────────────────────────────────────────────────────────
    "workshop 1: framing and security foundation": "ورشة العمل 1: الإطار والأساس الأمني",
    "workshop 2: risk origins": "ورشة العمل 2: مصادر المخاطر",
    "workshop 3: strategic scenarios": "ورشة العمل 3: السيناريوهات الاستراتيجية",
    "workshop 4: operational scenarios": "ورشة العمل 4: السيناريوهات التشغيلية",
    "workshop 5: risk treatment": "ورشة العمل 5: معالجة المخاطر",
    "define the study framework": "تحديد إطار الدراسة",
    "define business and technical perimeter": "تحديد المحيط التجاري والتقني",
    "identify feared events": "تحديد الأحداث المخيفة",
    "determine the security foundation": "تحديد الأساس الأمني",
    "identify risk origins and targeted objectives": "تحديد مصادر المخاطر والأهداف المستهدفة",
    "evaluate ro/to pairs": "تقييم أزواج مصادر المخاطر/الأهداف",
    "select ro/to pairs": "اختيار أزواج مصادر المخاطر/الأهداف",
    "map the ecosystem": "رسم خريطة النظام البيئي",
    "develop strategic scenarios": "تطوير السيناريوهات الاستراتيجية",
    "define security measures for the ecosystem": "تحديد التدابير الأمنية للنظام البيئي",
    "prepare elementary actions": "تحضير الإجراءات الأولية",
    "develop operational scenarios": "تطوير السيناريوهات التشغيلية",
    "evaluate the likelihood of operational scenarios": "تقييم احتمالية السيناريوهات التشغيلية",
    "decide on risk treatment strategy": "اتخاذ قرار استراتيجية معالجة المخاطر",
    "define security measures": "تحديد التدابير الأمنية",
    "assess and document residual risks": "تقييم المخاطر المتبقية وتوثيقها",
    "establish risk monitoring framework": "وضع إطار رصد المخاطر",
    "visual analysis": "التحليل المرئي",
    "activity level": "مستوى النشاط",
    "risk matrix used as a reference for the study": "مصفوفة المخاطر المستخدمة كمرجع للدراسة",
    "qualifications": "المؤهلات",
    "impacts": "التأثيرات",
    "ebios rm studies": "دراسات EBIOS RM",
    "what do you currently have to manage this risk": "ما الذي لديك حالياً لإدارة هذه المخاطر",
    "what will you do to mitigate this risk": "ما الذي ستفعله للتخفيف من هذه المخاطر",
    "description of the existing mitigations (this field will be deprecated soon)":
        "وصف التخفيفات الموجودة (سيتم إهمال هذا الحقل قريباً)",
    "ebios rm study (arm format)": "دراسة EBIOS RM (تنسيق ARM)",
    "ebios rm study (ciso assistant format)": "دراسة EBIOS RM (تنسيق CISO Assistant)",
    "arm import preview": "معاينة استيراد ARM",
    "the following objects will be created:": "سيتم إنشاء الكائنات التالية:",
    "primary assets": "الأصول الأساسية",
    "supporting assets": "الأصول الداعمة",
    "objects total": "إجمالي الكائنات",
    "in domain": "في النطاق",
    "study description": "وصف الدراسة",
    "confirm import": "تأكيد الاستيراد",
    "target objective": "الهدف المستهدف",
    "target objectives": "الأهداف المستهدفة",
    "motivation": "الدافع",
    "resources": "الموارد",
    "pertinence": "الصلة",
    "limited": "محدود",
    "significant": "ذو أهمية",
    "important": "مهم",
    "unlimited": "غير محدود",
    "strong": "قوي",
    "irrelevant": "غير ذي صلة",
    "partially relevant": "ذو صلة جزئياً",
    "fairly relevant": "ذو صلة إلى حد ما",
    "highly relevant": "ذو صلة عالية",
    "ro/to couple": "زوج مصدر المخاطر/الهدف",
    "ro/to couples": "أزواج مصادر المخاطر/الأهداف",
    "selected ro/to couples": "أزواج مصادر المخاطر/الأهداف المختارة",
    "focused feared event": "الحدث المخيف المحوري",
    "focused on": "محوره",
    "organized crime": "الجريمة المنظمة",
    "terrorist": "إرهابي",
    "activist": "ناشط",
    "competitor": "منافس",
    "amateur": "هاوٍ",
    "avenger": "منتقم",
    "pathological": "مرضي",
    "current dependency": "التبعية الحالية",
    "current penetration": "الاختراق الحالي",
    "current maturity": "النضج الحالي",
    "residual dependency": "التبعية المتبقية",
    "residual penetration": "الاختراق المتبقي",
    "residual maturity": "النضج المتبقي",
    "residual trust": "الثقة المتبقية",
    "selected attack paths": "مسارات الهجوم المختارة",
    "no attack paths defined": "لم يتم تحديد مسارات هجوم",
    "current criticality": "الأهمية الحرجة الحالية",
    "residual criticality": "الأهمية الحرجة المتبقية",
    "you can reset your password here.": "يمكنك إعادة تعيين كلمة المرور هنا.",
    "reset password": "إعادة تعيين كلمة المرور",
    "workshop 1": "ورشة العمل 1",
    "workshop 2": "ورشة العمل 2",
    "workshop 3": "ورشة العمل 3",
    "workshop 4": "ورشة العمل 4",
    "workshop 5": "ورشة العمل 5",
    "workshop": "ورشة العمل",
    "workshops": "ورش العمل",
    "frame the study": "وضع إطار الدراسة",
    "ecosystem": "النظام البيئي",
    "identify risk origins": "تحديد مصادر المخاطر",
    "operational scenarios assessment": "تقييم السيناريوهات التشغيلية",
    "risks summary and treatment": "ملخص المخاطر والمعالجة",
    "define your security baseline through compliance": "حدد أساسك الأمني من خلال الامتثال",
    "identify feared events and their gravity": "تحديد الأحداث المخيفة وخطورتها",
    "map risk origins to target objectives and study their relevance":
        "ربط مصادر المخاطر بالأهداف المستهدفة ودراسة صلتها",
    "identify stakeholders and their associated controls": "تحديد أصحاب المصلحة وضوابطهم المرتبطة",
    "define strategic scenarios": "تحديد السيناريوهات الاستراتيجية",
    "define elementary actions and techniques": "تحديد الإجراءات الأولية والتقنيات",
    "build operational scenarios": "بناء السيناريوهات التشغيلية",
    "summarize risk and prepare the treatment plan": "تلخيص المخاطر وإعداد خطة المعالجة",
    "refence id:": "معرف المرجع:",
    "no author assigned": "لم يتم تعيين مؤلف",
    "no reviewer assigned": "لم يتم تعيين مراجع",
    "select audit": "اختر التدقيق",
    "the asset graph must not contain cycles.": "يجب ألا يحتوي مخطط الأصول على دوائر.",
    "the domain graph must not contain cycles.": "يجب ألا يحتوي مخطط النطاق على دوائر.",
    "the risk scenario graph must not contain cycles.": "يجب ألا يحتوي مخطط سيناريو المخاطر على دوائر.",
    "operational scenario": "السيناريو التشغيلي",
    "operational scenario {refid}": "السيناريو التشغيلي {refId}",
    "operational scenarios": "السيناريوهات التشغيلية",
    "add operational scenario": "إضافة سيناريو تشغيلي",
    "no threat": "لا تهديد",
    "likely": "محتمل",
    "unlikely": "غير محتمل",
    "very likely": "محتمل جداً",
    "certain": "مؤكد",
    "minor": "طفيف",
    "operating modes description": "ملخص أوضاع التشغيل",
    "no stakeholders": "لا يوجد أصحاب مصلحة",
    "unitary actions / techniques": "الإجراءات الأحادية / التقنيات",
    "go back to ebios rm study": "العودة إلى دراسة EBIOS RM",
    "mark as in progress": "تعيين كقيد التنفيذ",
    "risk analyses": "تحليلات المخاطر",
    "client": "العميل",
    "clients": "العملاء",
    "partner": "الشريك",
    "partners": "الشركاء",
    "reference entity": "الكيان المرجعي",
    "reference entity:": "الكيان المرجعي:",
    "moderate": "معتدل",
    "associated attack paths": "مسارات الهجوم المرتبطة",
    "power-ups": "التحسينات",
    "nothing to show yet. charts will be updated once you've started your audits.":
        "لا يوجد شيء لعرضه بعد. سيتم تحديث المخططات بعد بدء عمليات التدقيق.",
    "govern": "الحوكمة",
    "identify": "التعرف",
    "protect": "الحماية",
    "detect": "الكشف",
    "respond": "الاستجابة",
    "recover": "التعافي",
    "estimating the level and intensity of the effects of a risk":
        "تقدير مستوى وشدة تأثيرات المخاطر",
    "estimate of the feasibility or probability of a risk occurring":
        "تقدير إمكانية أو احتمالية وقوع المخاطر",
    "primary (business asset) and supporting assets relating to the object under study":
        "الأصول الأساسية (أصول الأعمال) والأصول الداعمة المتعلقة بالموضوع قيد الدراسة",
    "the feared events must express/translate the fears of the business":
        "يجب أن تعبر الأحداث المخيفة عن مخاوف الأعمال",
    "possible impact categories": "فئات التأثير المحتملة",
    "selection of the feared event for the study": "اختيار الحدث المخيف للدراسة",
    "element, person, group of persons or organisation likely to generate a risk.\nyou can expand this list through the terminologies menu.":
        "عنصر أو شخص أو مجموعة أشخاص أو منظمة يُرجَّح أن تُولِّد مخاطر.\nيمكنك توسيع هذه القائمة من خلال قائمة المصطلحات.",
    "purpose of a risk origin, depending on its motivations":
        "غرض مصدر المخاطر وفقاً لدوافعه",
    "including financial resources, level of cyber skills, tools, time available to the attacker to carry out the attack, etc.":
        "بما في ذلك الموارد المالية ومستوى المهارات الإلكترونية والأدوات والوقت المتاح للمهاجم لتنفيذ الهجوم، إلخ.",
    "interests, factors that drive the risk origin to achieve its objective":
        "المصالح والعوامل التي تدفع مصدر المخاطر لتحقيق هدفه",
    "what is the level of activity of the risk origin within the scope of the study? ":
        "ما مستوى نشاط مصدر المخاطر ضمن نطاق الدراسة؟",
    "the relevance of the risk origin to the target objective":
        "صلة مصدر المخاطر بالهدف المستهدف",
    "selection of the ro/to couple for the study": "اختيار زوج مصدر المخاطر/الهدف للدراسة",
    "confronting the most serious feared events": "مواجهة الأحداث المخيفة الأشد خطورة",
    "stakeholder in the ecosystem": "صاحب مصلحة في النظام البيئي",
    "considered relationship with the stakeholder": "العلاقة المعتبرة مع صاحب المصلحة",
    "is the relationship with this stakeholder vital to my business?":
        "هل العلاقة مع صاحب المصلحة هذا حيوية لأعمالي؟",
    "to what extent does the stakeholder have access to my internal resources?":
        "إلى أي مدى يمكن لصاحب المصلحة الوصول إلى مواردي الداخلية؟",
    "what are the stakeholder's safety capabilities?":
        "ما قدرات صاحب المصلحة الأمنية؟",
    "could the stakeholder's intentions or interests be contrary to my own?":
        "هل يمكن أن تكون نوايا أو مصالح صاحب المصلحة معارضة لمصالحي؟",
    "selection of the stakeholder for the study": "اختيار صاحب المصلحة للدراسة",
    "sets of attack paths from a risk origin to an intended target":
        "مجموعات مسارات هجوم من مصدر مخاطر إلى هدف مقصود",
    "description of a series of elementary actions. you can now provide the details of the kill chain in the next step.\nif this field is empty, it will be inferred":
        "وصف سلسلة من الإجراءات الأولية. يمكنك تقديم تفاصيل سلسلة الهجوم في الخطوة التالية.\nإذا كان هذا الحقل فارغاً، سيتم استنتاجه",
    "unitary actions carried out by a risk origin on a critical supporting asset as part of an operational scenario":
        "إجراءات أحادية تنفذها مصادر المخاطر على أصل داعم حيوي كجزء من سيناريو تشغيلي",
    "selection of the operational scenario for the study": "اختيار السيناريو التشغيلي للدراسة",
    "stakeholders involved in the attack path": "أصحاب المصلحة المشاركون في مسار الهجوم",
    "selection of the attack path for the study": "اختيار مسار الهجوم للدراسة",
    "applied controls (compliance)": "الضوابط المطبقة (الامتثال)",
    "applied controls (risk assessment)": "الضوابط المطبقة (تقييم المخاطر)",
    "{number}%": "{number}%",
    "progress": "التقدم",
    "ecosystem radar": "رادار النظام البيئي",
    "criticality:": "الأهمية الحرجة:",
    "cyber reliability": "الموثوقية الإلكترونية",
    "insights": "الرؤى",
    "impact analysis": "تحليل التأثير",
    "priority review": "مراجعة الأولويات",
    "timeline view": "عرض الجدول الزمني",
    "missions and organizational services": "المهام والخدمات التنظيمية",
    "human": "بشري",
    "material": "مادي",
    "environmental": "بيئي",

    # ── Guided tour ───────────────────────────────────────────────────────────
    "guided tour": "الجولة الإرشادية",
    "welcome!": "مرحباً!",
    "let's take a tour of the main features to get you started.":
        "لنقم بجولة في الميزات الرئيسية لمساعدتك على البدء.",
    "you can always restart this tour by clicking this button.":
        "يمكنك دائماً إعادة تشغيل هذه الجولة بالنقر على هذا الزر.",
    "this is where you will define the hierarchy and perimeters of your organization. <br/><b>click on it.</b>":
        "هنا ستحدد التسلسل الهرمي ومحيطات مؤسستك. <br/><b>انقر عليه.</b>",
    "domains allow you to isolate your objects using the associated roles. you will need at least one. <br/><b>click on it.</b>":
        "تتيح لك النطاقات عزل كائناتك باستخدام الأدوار المرتبطة. ستحتاج إلى واحد على الأقل. <br/><b>انقر عليه.</b>",
    "this where you will be able to create a new domain.": "هنا يمكنك إنشاء نطاق جديد.",
    "perimeters are functional sets within a domain. you will need at least one. <br/><b>click on it.</b>":
        "المحيطات مجموعات وظيفية داخل النطاق. ستحتاج إلى واحد على الأقل. <br/><b>انقر عليه.</b>",
    "this is where you will be able to create a perimeter.": "هنا يمكنك إنشاء محيط.",
    "catalog overview": "نظرة عامة على الكتالوج",
    "the catalog is where you will be able to import frameworks, threats, matrices and other predifined objects":
        "الكتالوج حيث يمكنك استيراد أطر العمل والتهديدات والمصفوفات وكائنات أخرى محددة مسبقاً",
    "you will be able to browse the loaded objects per category and import new ones. <br/><b>click on it.</b>":
        "ستتمكن من تصفح الكائنات المحملة حسب الفئة واستيراد كائنات جديدة. <br/><b>انقر عليه.</b>",
    "this where you will be able to import new frameworks.": "هنا يمكنك استيراد أطر عمل جديدة.",
    "this is where you will be able to import new matrices.": "هنا يمكنك استيراد مصفوفات جديدة.",
    "this where will be able to manage your compliance activities. <br/><b>click on it.</b>":
        "هنا ستتمكن من إدارة أنشطة الامتثال الخاصة بك. <br/><b>انقر عليه.</b>",
    "audits": "عمليات التدقيق",
    "this is where you will be able to drive and track your audits and baselines":
        "هنا يمكنك قيادة وتتبع عمليات التدقيق والخطوط الأساسية",
    "this is where you will be able to manage your risk analysis and registry. <br/><b>click on it.</b>":
        "هنا يمكنك إدارة تحليل المخاطر والسجل. <br/><b>انقر عليه.</b>",
    "group and manage your analysis through risk assessments.":
        "تجميع وإدارة تحليلاتك من خلال تقييمات المخاطر.",
    "analytics": "التحليلات",
    "the overview section cover your main dashboards and analytics. <br/><b>click on it.</b>":
        "يغطي قسم النظرة العامة لوحات التحكم والتحليلات الرئيسية. <br/><b>انقر عليه.</b>",
    "or track your indivdual assignements and tasks here.":
        "أو تتبع تعيينات ومهام فردية هنا.",
    "remember, you can always restart the tour from here!": "تذكر، يمكنك دائماً إعادة تشغيل الجولة من هنا!",
    "help & tour": "المساعدة والجولة",
    "assessments breakdown": "تفصيل التقييمات",

    # ── Audit / extended result ───────────────────────────────────────────────
    "implementation score": "نتيجة التنفيذ",
    "allows adding extended audit results (nonconformities, observations, opportunities for improvement, good practices) to requirement assessments.":
        "يتيح إضافة نتائج تدقيق موسعة (عدم المطابقات والملاحظات وفرص التحسين والممارسات الجيدة) لتقييمات المتطلبات.",
    "extended result": "النتيجة الموسعة",
    "major nonconformity": "عدم مطابقة رئيسية",
    "minor nonconformity": "عدم مطابقة ثانوية",
    "observation / sensitive point": "ملاحظة / نقطة حساسة",
    "opportunity for improvement": "فرصة للتحسين",
    "good practice": "ممارسة جيدة",
    "auditor progress on requirement review": "تقدم المدقق في مراجعة المتطلبات",
    "the compliance result for this requirement": "نتيجة الامتثال لهذا المتطلب",
    "additional audit finding information": "معلومات إضافية عن نتائج التدقيق",
    "enable progress status": "تفعيل حالة التقدم",
    "shows progress status (to do, in progress, in review, done) on requirement assessments.":
        "يعرض حالة التقدم (للتنفيذ، قيد التنفيذ، قيد المراجعة، منتهٍ) في تقييمات المتطلبات.",
    "score calculation method": "طريقة حساب النتيجة",
    "defines how the global score is calculated. average computes the weighted mean of scores. sum computes the weighted total of scores.":
        "يحدد كيفية حساب النتيجة الإجمالية. المتوسط يحسب الوسط الموزون للنتائج. المجموع يحسب الإجمالي الموزون للنتائج.",
    "sum": "مجموع",
    "the import version is not compatible with the current version of the application":
        "إصدار الاستيراد غير متوافق مع الإصدار الحالي من التطبيق",
    "an error occurred during the import": "حدث خطأ أثناء الاستيراد",
    "folder successfully imported": "تم استيراد المجلد بنجاح",

    # ── Settings / MFA ────────────────────────────────────────────────────────
    "only users with approver roles appear here": "تظهر هنا فقط المستخدمون ذوو أدوار الاعتماد",
    "when enabled, users will see a warning before opening external links":
        "عند التفعيل، سيرى المستخدمون تحذيراً قبل فتح الروابط الخارجية",
    "when enabled, all local users (except superusers) must set up mfa before accessing the application. sso users are exempt.":
        "عند التفعيل، يجب على جميع المستخدمين المحليين (باستثناء المستخدمين المتميزين) إعداد المصادقة متعددة العوامل قبل الوصول. مستخدمو SSO مستثنون.",
    "your administrator requires all users to enable multi-factor authentication. please set up an authenticator app to continue.":
        "يطلب المسؤول من جميع المستخدمين تفعيل المصادقة متعددة العوامل. يرجى إعداد تطبيق مصادقة للمتابعة.",
    "score a risk scenario using a risk matrix based on threat agent and vulnerability factors":
        "تسجيل سيناريو مخاطر باستخدام مصفوفة مخاطر بناءً على عوامل عميل التهديد والثغرات",
    "reference scale": "المقياس المرجعي",
    "this serves as a template and would override some fields values (name, ref_id, category, csf function, etc.)":
        "يعمل كقالب ويتجاوز قيم بعض الحقول (الاسم، ref_id، الفئة، وظيفة CSF، إلخ)",
    "you can review your levels definition by clicking on the matrix above (opens in a new tab)":
        "يمكنك مراجعة تعريفات مستوياتك بالنقر على المصفوفة أعلاه (يفتح في علامة تبويب جديدة)",
    "depends on ↓": "يعتمد على ↓",
    "visualize the dependency graph for this asset and its related assets":
        "عرض مخطط التبعيات لهذا الأصل وأصوله المرتبطة",
    "extra assets that could affect this asset resiliency.\nthe data from the primary/supporting relationship are automatically captured. no need to mention them.":
        "أصول إضافية قد تؤثر على مرونة هذا الأصل.\nيتم التقاط بيانات العلاقة الأساسية/الداعمة تلقائياً. لا حاجة لذكرها.",
    "controls specifically designed to improve this asset resiliency":
        "ضوابط مصممة خصيصاً لتحسين مرونة هذا الأصل",
    "evidences specific to resiliency implementation or testing":
        "أدلة خاصة بتنفيذ المرونة أو اختبارها",
    "usually a primary asset / business process to focus on for this entry":
        "عادةً أصل أساسي / عملية أعمال للتركيز عليها في هذا الإدخال",
    "future updates will include detailed requirement-by-requirement comparisons and more.":
        "ستتضمن التحديثات المستقبلية مقارنات تفصيلية متطلباً بمتطلب والمزيد.",
    "associated exceptions": "الاستثناءات المرتبطة",
    "a user is already linked to this representative.":
        "مستخدم مرتبط بالفعل بهذا الممثل.",
    "if mentioned on this list, these capabilites from this asset will override those of its supporting assets":
        "إذا ذُكرت في هذه القائمة، ستتجاوز هذه القدرات من هذا الأصل تلك الخاصة بأصوله الداعمة",
    "pending p1": "P1 معلق",
    "missed eta": "ETA فائت",
    "expired evidences": "أدلة منتهية الصلاحية",
    "average progress": "متوسط التقدم",
    "advanced analytics is disabled. enable it in settings > feature flags.":
        "التحليلات المتقدمة معطلة. فعِّلها في الإعدادات > علامات الميزات.",
    "this framework does not define implementation groups":
        "لا يحدد هذا الإطار مجموعات تنفيذ",
    "no mapping targets available for this framework":
        "لا توجد أهداف تعيين متاحة لهذا الإطار",
    "are you sure you want to delete this assignment? the associated requirements will become unassigned.":
        "هل أنت متأكد من حذف هذا التعيين؟ ستصبح المتطلبات المرتبطة غير معيَّنة.",
    "failed to create assignment": "فشل إنشاء التعيين",
    "failed to update assignment": "فشل تحديث التعيين",
    "failed to delete assignment": "فشل حذف التعيين",
    "risk scenarios that precede this scenario. cannot form cycles or include itself.":
        "سيناريوهات المخاطر التي تسبق هذا السيناريو. لا يمكن أن تشكّل دوائر أو تتضمن نفسها.",
}


def load_json_no_dup(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f, object_pairs_hook=lambda pairs: dict(pairs))


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
        if ar_val == en_val:
            lower = en_val.lower().strip()
            if lower in DICT3:
                ar_data[key] = DICT3[lower]
                fixed += 1
            elif key.lower() in DICT3:
                ar_data[key] = DICT3[key.lower()]
                fixed += 1

    print(f"Third-pass: fixed {fixed} keys")

    schema = ar_data.pop("$schema", None)
    ordered = {}
    if schema:
        ordered["$schema"] = schema
    ordered.update(ar_data)

    with open(ar_path, "w", encoding="utf-8") as f:
        json.dump(ordered, f, ensure_ascii=False, indent="\t")
        f.write("\n")

    en_data2 = load_json_no_dup(en_path)
    ar_data2 = load_json_no_dup(ar_path)
    still_en = [k for k in ar_data2
                if k in en_data2
                and isinstance(en_data2[k], str)
                and ar_data2[k] == en_data2[k]
                and not k.startswith("$")]
    print(f"Still in English: {len(still_en)}")
    print(f"Written to {ar_path}")


if __name__ == "__main__":
    main()
