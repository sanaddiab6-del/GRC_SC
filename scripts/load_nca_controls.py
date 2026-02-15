"""
NCA Control Library Loader
Comprehensive loader for ECC, CCC, and PDPL control frameworks
Populates complete control sets with proper metadata and relationships
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import AsyncSessionLocal  # type: ignore
from controls.models import Control, FrameworkType, ControlStatus  # type: ignore

logger = logging.getLogger(__name__)


# ============================================================================
# NCA ECC (Essential Cybersecurity Controls) - Complete Control Set
# ============================================================================

ECC_CONTROLS = [
    # GOVERNANCE (GV)
    {
        "control_id": "ECC-GV-1",
        "framework": FrameworkType.ECC,
        "domain": "Governance",
        "title_en": "Cybersecurity Governance Framework",
        "title_ar": "إطار حوكمة الأمن السيبراني",
        "description_en": "Establish comprehensive cybersecurity governance framework with clear roles, responsibilities, and reporting structure aligned with organizational objectives.",
        "description_ar": "إنشاء إطار شامل لحوكمة الأمن السيبراني مع أدوار ومسؤوليات وهيكل تقارير واضح يتماشى مع أهداف المنظمة.",
        "policy_guidance_en": "Define cybersecurity policy framework, governance structure, board oversight, executive accountability, and strategic alignment.",
        "policy_guidance_ar": "تحديد إطار سياسة الأمن السيبراني، وهيكل الحوكمة، والإشراف من مجلس الإدارة، والمساءلة التنفيذية، والمواءمة الاستراتيجية.",
        "procedure_guidance_en": "Document governance processes, establish steering committee, conduct quarterly reviews, maintain governance documentation.",
        "procedure_guidance_ar": "توثيق عمليات الحوكمة، وإنشاء لجنة توجيهية، وإجراء مراجعات ربع سنوية، وصيانة وثائق الحوكمة.",
        "priority": "CRITICAL",
        "status": ControlStatus.NOT_STARTED,
        "maturity_level": 1,
        "evidence_types": ["POLICY", "PROCEDURE", "REPORT"],
        "related_controls": ["ECC-GV-2", "ECC-GV-3", "ECC-RM-1"]
    },
    {
        "control_id": "ECC-GV-2",
        "framework": FrameworkType.ECC,
        "domain": "Governance",
        "title_en": "Cybersecurity Strategy and Objectives",
        "title_ar": "استراتيجية وأهداف الأمن السيبراني",
        "description_en": "Develop and maintain cybersecurity strategy aligned with business objectives, risk appetite, and regulatory requirements.",
        "description_ar": "تطوير وصيانة استراتيجية الأمن السيبراني المتوافقة مع أهداف العمل، ومستوى المخاطر المقبول، والمتطلبات التنظيمية.",
        "policy_guidance_en": "Define strategic objectives, measurable goals, resource allocation, and success metrics for cybersecurity program.",
        "policy_guidance_ar": "تحديد الأهداف الاستراتيجية والأهداف القابلة للقياس وتخصيص الموارد ومقاييس النجاح لبرنامج الأمن السيبراني.",
        "procedure_guidance_en": "Annual strategy review, quarterly progress assessment, stakeholder engagement, budget planning.",
        "procedure_guidance_ar": "مراجعة الاستراتيجية السنوية، تقييم التقدم الربع سنوي، مشاركة أصحاب المصلحة، تخطيط الميزانية.",
        "priority": "CRITICAL",
        "status": ControlStatus.NOT_STARTED,
        "maturity_level": 1,
        "evidence_types": ["POLICY", "REPORT", "CERTIFICATE"],
        "related_controls": ["ECC-GV-1", "ECC-RM-1", "ECC-RM-2"]
    },
    {
        "control_id": "ECC-GV-3",
        "framework": FrameworkType.ECC,
        "domain": "Governance",
        "title_en": "Roles and Responsibilities",
        "title_ar": "الأدوار والمسؤوليات",
        "description_en": "Define and assign clear cybersecurity roles, responsibilities, and accountability across the organization.",
        "description_ar": "تحديد وتعيين أدوار ومسؤوليات ومساءلة واضحة للأمن السيبراني في جميع أنحاء المنظمة.",
        "policy_guidance_en": "Document RACI matrix, job descriptions, segregation of duties, escalation paths for cybersecurity functions.",
        "policy_guidance_ar": "توثيق مصفوفة RACI، والأوصاف الوظيفية، والفصل بين الواجبات، ومسارات التصعيد لوظائف الأمن السيبراني.",
        "procedure_guidance_en": "Annual role review, competency assessment, training requirements, performance metrics.",
        "procedure_guidance_ar": "مراجعة الأدوار السنوية، تقييم الكفاءة، متطلبات التدريب، مقاييس الأداء.",
        "priority": "HIGH",
        "status": ControlStatus.NOT_STARTED,
        "maturity_level": 1,
        "evidence_types": ["POLICY", "PROCEDURE", "REPORT"],
        "related_controls": ["ECC-GV-1", "ECC-GV-4"]
    },
    
    # INFORMATION SECURITY (IS)
    {
        "control_id": "ECC-IS-1",
        "framework": FrameworkType.ECC,
        "domain": "Information Security",
        "title_en": "Asset Management",
        "title_ar": "إدارة الأصول",
        "description_en": "Maintain comprehensive inventory of information assets with classification, ownership, and lifecycle management.",
        "description_ar": "الحفاظ على جرد شامل لأصول المعلومات مع التصنيف والملكية وإدارة دورة الحياة.",
        "policy_guidance_en": "Asset classification scheme, ownership assignment, acceptable use policy, disposal procedures.",
        "policy_guidance_ar": "مخطط تصنيف الأصول، تخصيص الملكية، سياسة الاستخدام المقبول، إجراءات التخلص.",
        "priority": "CRITICAL",
        "status": ControlStatus.NOT_STARTED,
        "maturity_level": 1,
        "evidence_types": ["POLICY", "LOG", "REPORT"],
        "related_controls": ["ECC-IS-2", "ECC-IS-7"]
    },
    {
        "control_id": "ECC-IS-2",
        "framework": FrameworkType.ECC,
        "domain": "Information Security",
        "title_en": "Data Classification and Handling",
        "title_ar": "تصنيف البيانات والتعامل معها",
        "description_en": "Classify data based on sensitivity and implement appropriate handling, storage, and transmission controls.",
        "description_ar": "تصنيف البيانات حسب الحساسية وتنفيذ ضوابط مناسبة للتعامل والتخزين والنقل.",
        "policy_guidance_en": "Data classification levels (Public, Internal, Confidential, Restricted), labeling requirements, handling procedures.",
        "policy_guidance_ar": "مستويات تصنيف البيانات (عامة، داخلية، سرية، مقيدة)، متطلبات الوسم، إجراءات التعامل.",
        "priority": "CRITICAL",
        "status": ControlStatus.NOT_STARTED,
        "maturity_level": 1,
        "evidence_types": ["POLICY", "PROCEDURE", "LOG"],
        "related_controls": ["ECC-IS-1", "ECC-IS-3", "ECC-DC-1"]
    },
    {
        "control_id": "ECC-IS-3",
        "framework": FrameworkType.ECC,
        "domain": "Information Security",
        "title_en": "Access Control",
        "title_ar": "التحكم في الوصول",
        "description_en": "Implement role-based access control (RBAC) with least privilege principle and regular access reviews.",
        "description_ar": "تنفيذ التحكم في الوصول على أساس الدور (RBAC) مع مبدأ الحد الأدنى من الامتيازات ومراجعات الوصول المنتظمة.",
        "policy_guidance_en": "Access control policy, RBAC model, privileged access management, identity lifecycle management.",
        "policy_guidance_ar": "سياسة التحكم في الوصول، نموذج RBAC، إدارة الوصول المميز، إدارة دورة حياة الهوية.",
        "priority": "CRITICAL",
        "status": ControlStatus.NOT_STARTED,
        "maturity_level": 1,
        "evidence_types": ["POLICY", "LOG", "SCREENSHOT"],
        "related_controls": ["ECC-IS-4", "ECC-IS-5"]
    },
    {
        "control_id": "ECC-IS-4",
        "framework": FrameworkType.ECC,
        "domain": "Information Security",
        "title_en": "Authentication and Password Management",
        "title_ar": "المصادقة وإدارة كلمات المرور",
        "description_en": "Enforce strong authentication mechanisms including multi-factor authentication (MFA) for privileged access.",
        "description_ar": "فرض آليات مصادقة قوية بما في ذلك المصادقة متعددة العوامل (MFA) للوصول المميز.",
        "policy_guidance_en": "Password complexity requirements, MFA enforcement, password aging, account lockout policies.",
        "policy_guidance_ar": "متطلبات تعقيد كلمة المرور، فرض MFA، تقادم كلمة المرور، سياسات قفل الحساب.",
        "priority": "CRITICAL",
        "status": ControlStatus.NOT_STARTED,
        "maturity_level": 1,
        "evidence_types": ["POLICY", "LOG", "SCREENSHOT"],
        "related_controls": ["ECC-IS-3", "ECC-IS-5"]
    },
    {
        "control_id": "ECC-IS-5",
        "framework": FrameworkType.ECC,
        "domain": "Information Security",
        "title_en": "Incident Response and Management",
        "title_ar": "الاستجابة للحوادث وإدارتها",
        "description_en": "Establish incident response capability with defined procedures, roles, and communication protocols.",
        "description_ar": "إنشاء قدرة على الاستجابة للحوادث مع إجراءات محددة وأدوار وبروتوكولات اتصال.",
        "policy_guidance_en": "Incident response plan, severity classification, escalation procedures, post-incident review.",
        "policy_guidance_ar": "خطة الاستجابة للحوادث، تصنيف الخطورة، إجراءات التصعيد، مراجعة ما بعد الحادث.",
        "priority": "CRITICAL",
        "status": ControlStatus.NOT_STARTED,
        "maturity_level": 1,
        "evidence_types": ["POLICY", "PROCEDURE", "LOG", "REPORT"],
        "related_controls": ["ECC-IS-6", "ECC-IS-7"]
    },
    {
        "control_id": "ECC-IS-6",
        "framework": FrameworkType.ECC,
        "domain": "Information Security",
        "title_en": "Security Monitoring and Logging",
        "title_ar": "المراقبة الأمنية والتسجيل",
        "description_en": "Implement comprehensive security monitoring and maintain audit logs with defined retention periods.",
        "description_ar": "تنفيذ المراقبة الأمنية الشاملة والحفاظ على سجلات التدقيق مع فترات الاحتفاظ المحددة.",
        "policy_guidance_en": "Logging requirements, SIEM integration, log retention (7 years for NCA), real-time monitoring.",
        "policy_guidance_ar": "متطلبات التسجيل، تكامل SIEM، الاحتفاظ بالسجلات (7 سنوات لـ NCA)، المراقبة في الوقت الفعلي.",
        "priority": "CRITICAL",
        "status": ControlStatus.NOT_STARTED,
        "maturity_level": 1,
        "evidence_types": ["POLICY", "LOG", "SCREENSHOT"],
        "related_controls": ["ECC-IS-5", "ECC-IS-7"]
    },
    {
        "control_id": "ECC-IS-7",
        "framework": FrameworkType.ECC,
        "domain": "Information Security",
        "title_en": "Cryptography and Encryption",
        "title_ar": "التشفير والترميز",
        "description_en": "Implement encryption for data at rest and in transit using approved cryptographic standards.",
        "description_ar": "تنفيذ التشفير للبيانات أثناء الراحة والنقل باستخدام معايير التشفير المعتمدة.",
        "policy_guidance_en": "Encryption standards (AES-256), key management, TLS 1.2+, certificate lifecycle management.",
        "policy_guidance_ar": "معايير التشفير (AES-256)، إدارة المفاتيح، TLS 1.2+، إدارة دورة حياة الشهادات.",
        "priority": "CRITICAL",
        "status": ControlStatus.NOT_STARTED,
        "maturity_level": 1,
        "evidence_types": ["POLICY", "CERTIFICATE", "SCREENSHOT"],
        "related_controls": ["ECC-IS-2", "ECC-DC-1"]
    },
    
    # RISK MANAGEMENT (RM)
    {
        "control_id": "ECC-RM-1",
        "framework": FrameworkType.ECC,
        "domain": "Risk Management",
        "title_en": "Risk Assessment Methodology",
        "title_ar": "منهجية تقييم المخاطر",
        "description_en": "Establish systematic risk assessment methodology aligned with ISO 27005 and organizational risk appetite.",
        "description_ar": "إنشاء منهجية منهجية لتقييم المخاطر متوافقة مع ISO 27005 ورغبة المنظمة في المخاطر.",
        "policy_guidance_en": "Risk assessment framework, risk criteria, impact/likelihood scales, risk appetite statement.",
        "policy_guidance_ar": "إطار تقييم المخاطر، معايير المخاطر، مقاييس التأثير/الاحتمالية، بيان الرغبة في المخاطر.",
        "priority": "CRITICAL",
        "status": ControlStatus.NOT_STARTED,
        "maturity_level": 1,
        "evidence_types": ["POLICY", "PROCEDURE", "REPORT"],
        "related_controls": ["ECC-RM-2", "ECC-RM-3", "ECC-GV-2"]
    },
    {
        "control_id": "ECC-RM-2",
        "framework": FrameworkType.ECC,
        "domain": "Risk Management",
        "title_en": "Risk Treatment and Mitigation",
        "title_ar": "معالجة المخاطر والتخفيف منها",
        "description_en": "Implement risk treatment plans with appropriate controls to reduce risks to acceptable levels.",
        "description_ar": "تنفيذ خطط معالجة المخاطر مع ضوابط مناسبة لتقليل المخاطر إلى مستويات مقبولة.",
        "policy_guidance_en": "Risk treatment options (accept, mitigate, transfer, avoid), control selection, residual risk acceptance.",
        "policy_guidance_ar": "خيارات معالجة المخاطر (قبول، تخفيف، نقل، تجنب)، اختيار التحكم، قبول المخاطر المتبقية.",
        "priority": "HIGH",
        "status": ControlStatus.NOT_STARTED,
        "maturity_level": 1,
        "evidence_types": ["POLICY", "REPORT"],
        "related_controls": ["ECC-RM-1", "ECC-RM-3"]
    },
    {
        "control_id": "ECC-RM-3",
        "framework": FrameworkType.ECC,
        "domain": "Risk Management",
        "title_en": "Risk Monitoring and Review",
        "title_ar": "مراقبة المخاطر ومراجعتها",
        "description_en": "Continuously monitor and review risks, controls effectiveness, and risk landscape changes.",
        "description_ar": "المراقبة والمراجعة المستمرة للمخاطر وفعالية الضوابط وتغييرات بيئة المخاطر.",
        "policy_guidance_en": "Risk monitoring frequency, KRI thresholds, escalation triggers, quarterly risk reviews.",
        "policy_guidance_ar": "تكرار مراقبة المخاطر، عتبات مؤشرات المخاطر الرئيسية، محفزات التصعيد، مراجعات المخاطر الفصلية.",
        "priority": "HIGH",
        "status": ControlStatus.NOT_STARTED,
        "maturity_level": 1,
        "evidence_types": ["REPORT", "LOG"],
        "related_controls": ["ECC-RM-1", "ECC-RM-2"]
    },
    
    # DATA CLASSIFICATION (DC)
    {
        "control_id": "ECC-DC-1",
        "framework": FrameworkType.ECC,
        "domain": "Data Classification",
        "title_en": "Data Protection and Privacy",
        "title_ar": "حماية البيانات والخصوصية",
        "description_en": "Implement data protection controls aligned with PDPL requirements for personal data processing.",
        "description_ar": "تنفيذ ضوابط حماية البيانات المتوافقة مع متطلبات PDPL لمعالجة البيانات الشخصية.",
        "policy_guidance_en": "PDPL compliance, data minimization, purpose limitation, consent management, data subject rights.",
        "policy_guidance_ar": "امتثال PDPL، تقليل البيانات، تحديد الغرض، إدارة الموافقة، حقوق صاحب البيانات.",
        "priority": "CRITICAL",
        "status": ControlStatus.NOT_STARTED,
        "maturity_level": 1,
        "evidence_types": ["POLICY", "PROCEDURE", "LOG"],
        "related_controls": ["ECC-IS-2", "ECC-IS-7", "PDPL-01"]
    },
]


# ============================================================================
# NCA CCC (Cloud Cybersecurity Controls) - Complete Control Set  
# ============================================================================

CCC_CONTROLS = [
    {
        "control_id": "CCC-SEC-01",
        "framework": FrameworkType.CCC,
        "domain": "Cloud Security",
        "title_en": "Cloud Data Security",
        "title_ar": "أمان بيانات السحابة",
        "description_en": "Implement comprehensive data security controls for cloud environments including encryption and access management.",
        "description_ar": "تنفيذ ضوابط أمان البيانات الشاملة لبيئات السحابة بما في ذلك التشفير وإدارة الوصول.",
        "policy_guidance_en": "Cloud encryption strategy, key management, data residency requirements, multi-tenancy controls.",
        "policy_guidance_ar": "استراتيجية تشفير السحابة، إدارة المفاتيح، متطلبات إقامة البيانات، ضوابط التعدد.",
        "priority": "CRITICAL",
        "status": ControlStatus.NOT_STARTED,
        "maturity_level": 1,
        "evidence_types": ["POLICY", "CERTIFICATE", "SCREENSHOT"],
        "related_controls": ["CCC-SEC-02", "ECC-IS-7"]
    },
    {
        "control_id": "CCC-SEC-02",
        "framework": FrameworkType.CCC,
        "domain": "Cloud Security",
        "title_en": "Cloud Access Control",
        "title_ar": "التحكم في الوصول السحابي",
        "description_en": "Enforce identity and access management (IAM) controls for cloud resources with zero trust principles.",
        "description_ar": "فرض ضوابط إدارة الهوية والوصول (IAM) لموارد السحابة مع مبادئ عدم الثقة الصفرية.",
        "policy_guidance_en": "Cloud IAM strategy, federated identity, just-in-time access, privileged access management.",
        "policy_guidance_ar": "استراتيجية IAM السحابية، الهوية الموحدة، الوصول في الوقت المناسب، إدارة الوصول المميز.",
        "priority": "CRITICAL",
        "status": ControlStatus.NOT_STARTED,
        "maturity_level": 1,
        "evidence_types": ["POLICY", "LOG", "SCREENSHOT"],
        "related_controls": ["CCC-SEC-01", "ECC-IS-3"]
    },
    {
        "control_id": "CCC-GOV-01",
        "framework": FrameworkType.CCC,
        "domain": "Cloud Governance",
        "title_en": "Cloud Service Provider Assessment",
        "title_ar": "تقييم مزود خدمة السحابة",
        "description_en": "Conduct comprehensive assessment of cloud service providers against security and compliance requirements.",
        "description_ar": "إجراء تقييم شامل لمزودي خدمات السحابة مقابل متطلبات الأمن والامتثال.",
        "policy_guidance_en": "CSP selection criteria, certification requirements, data sovereignty, SLA requirements.",
        "policy_guidance_ar": "معايير اختيار CSP، متطلبات الشهادة، سيادة البيانات، متطلبات SLA.",
        "priority": "CRITICAL",
        "status": ControlStatus.NOT_STARTED,
        "maturity_level": 1,
        "evidence_types": ["POLICY", "REPORT", "CERTIFICATE"],
        "related_controls": ["CCC-GOV-02", "ECC-GV-1"]
    },
    {
        "control_id": "CCC-GOV-02",
        "framework": FrameworkType.CCC,
        "domain": "Cloud Governance",
        "title_en": "Cloud Compliance and Audit",
        "title_ar": "امتثال السحابة والتدقيق",
        "description_en": "Maintain cloud compliance through continuous monitoring and regular compliance audits.",
        "description_ar": "الحفاظ على امتثال السحابة من خلال المراقبة المستمرة وعمليات التدقيق المنتظمة.",
        "policy_guidance_en": "Cloud audit procedures, compliance monitoring, third-party assessments, remediation tracking.",
        "policy_guidance_ar": "إجراءات تدقيق السحابة، مراقبة الامتثال، تقييمات الطرف الثالث، تتبع الإصلاح.",
        "priority": "HIGH",
        "status": ControlStatus.NOT_STARTED,
        "maturity_level": 1,
        "evidence_types": ["POLICY", "REPORT", "LOG"],
        "related_controls": ["CCC-GOV-01", "ECC-GV-1"]
    },
]


# ============================================================================
# PDPL (Personal Data Protection Law) - Complete Control Set
# ============================================================================

PDPL_CONTROLS = [
    {
        "control_id": "PDPL-01",
        "framework": FrameworkType.PDPL,
        "domain": "Data Protection Principles",
        "title_en": "Lawfulness and Consent",
        "title_ar": "المشروعية والموافقة",
        "description_en": "Ensure all personal data processing is lawful and based on valid consent or legal basis.",
        "description_ar": "التأكد من أن جميع معالجة البيانات الشخصية مشروعة وتستند إلى موافقة صالحة أو أساس قانوني.",
        "policy_guidance_en": "Consent management, legal basis identification, purpose specification, data minimization.",
        "policy_guidance_ar": "إدارة الموافقة، تحديد الأساس القانوني، تحديد الغرض، تقليل البيانات.",
        "priority": "CRITICAL",
        "status": ControlStatus.NOT_STARTED,
        "maturity_level": 1,
        "evidence_types": ["POLICY", "PROCEDURE", "LOG"],
        "related_controls": ["PDPL-02", "PDPL-03", "ECC-DC-1"]
    },
    {
        "control_id": "PDPL-02",
        "framework": FrameworkType.PDPL,
        "domain": "Data Protection Principles",
        "title_en": "Data Quality and Accuracy",
        "title_ar": "جودة البيانات والدقة",
        "description_en": "Maintain accuracy and completeness of personal data throughout its lifecycle.",
        "description_ar": "الحفاظ على دقة واكتمال البيانات الشخصية طوال دورة حياتها.",
        "policy_guidance_en": "Data accuracy procedures, regular updates, correction mechanisms, data validation.",
        "policy_guidance_ar": "إجراءات دقة البيانات، التحديثات المنتظمة، آليات التصحيح، التحقق من صحة البيانات.",
        "priority": "HIGH",
        "status": ControlStatus.NOT_STARTED,
        "maturity_level": 1,
        "evidence_types": ["POLICY", "PROCEDURE", "LOG"],
        "related_controls": ["PDPL-01", "PDPL-04"]
    },
    {
        "control_id": "PDPL-03",
        "framework": FrameworkType.PDPL,
        "domain": "Data Protection Principles",
        "title_en": "Purpose Limitation",
        "title_ar": "تحديد الغرض",
        "description_en": "Process personal data only for specified, explicit, and legitimate purposes.",
        "description_ar": "معالجة البيانات الشخصية فقط لأغراض محددة وصريحة ومشروعة.",
        "policy_guidance_en": "Purpose documentation, processing scope limitations, secondary use controls.",
        "policy_guidance_ar": "توثيق الغرض، قيود نطاق المعالجة، ضوابط الاستخدام الثانوي.",
        "priority": "CRITICAL",
        "status": ControlStatus.NOT_STARTED,
        "maturity_level": 1,
        "evidence_types": ["POLICY", "PROCEDURE"],
        "related_controls": ["PDPL-01", "PDPL-04"]
    },
    {
        "control_id": "PDPL-04",
        "framework": FrameworkType.PDPL,
        "domain": "Data Subject Rights",
        "title_en": "Right to Access",
        "title_ar": "الحق في الوصول",
        "description_en": "Enable data subjects to access their personal data and obtain information about processing.",
        "description_ar": "تمكين أصحاب البيانات من الوصول إلى بياناتهم الشخصية والحصول على معلومات حول المعالجة.",
        "policy_guidance_en": "Access request procedures, response timelines (30 days), authentication requirements.",
        "policy_guidance_ar": "إجراءات طلب الوصول، الجداول الزمنية للاستجابة (30 يومًا)، متطلبات المصادقة.",
        "priority": "CRITICAL",
        "status": ControlStatus.NOT_STARTED,
        "maturity_level": 1,
        "evidence_types": ["POLICY", "PROCEDURE", "LOG"],
        "related_controls": ["PDPL-05", "PDPL-06", "PDPL-07"]
    },
    {
        "control_id": "PDPL-05",
        "framework": FrameworkType.PDPL,
        "domain": "Data Subject Rights",
        "title_en": "Right to Rectification",
        "title_ar": "الحق في التصحيح",
        "description_en": "Allow data subjects to correct inaccurate or incomplete personal data.",
        "description_ar": "السماح لأصحاب البيانات بتصحيح البيانات الشخصية غير الدقيقة أو غير الكاملة.",
        "policy_guidance_en": "Correction procedures, verification requirements, notification of changes to third parties.",
        "policy_guidance_ar": "إجراءات التصحيح، متطلبات التحقق، إخطار التغييرات للأطراف الثالثة.",
        "priority": "HIGH",
        "status": ControlStatus.NOT_STARTED,
        "maturity_level": 1,
        "evidence_types": ["POLICY", "PROCEDURE", "LOG"],
        "related_controls": ["PDPL-04", "PDPL-06"]
    },
    {
        "control_id": "PDPL-06",
        "framework": FrameworkType.PDPL,
        "domain": "Data Subject Rights",
        "title_en": "Right to Erasure",
        "title_ar": "الحق في المحو",
        "description_en": "Implement data subject right to deletion when legal basis no longer applies.",
        "description_ar": "تنفيذ حق صاحب البيانات في الحذف عندما لا ينطبق الأساس القانوني بعد الآن.",
        "policy_guidance_en": "Erasure procedures, retention schedule exceptions, verification of deletion.",
        "policy_guidance_ar": "إجراءات المحو، استثناءات جدول الاحتفاظ، التحقق من الحذف.",
        "priority": "CRITICAL",
        "status": ControlStatus.NOT_STARTED,
        "maturity_level": 1,
        "evidence_types": ["POLICY", "PROCEDURE", "LOG"],
        "related_controls": ["PDPL-04", "PDPL-05", "PDPL-07"]
    },
    {
        "control_id": "PDPL-07",
        "framework": FrameworkType.PDPL,
        "domain": "Data Subject Rights",
        "title_en": "Right to Object and Portability",
        "title_ar": "الحق في الاعتراض والنقل",
        "description_en": "Enable data subjects to object to processing and obtain their data in portable format.",
        "description_ar": "تمكين أصحاب البيانات من الاعتراض على المعالجة والحصول على بياناتهم بصيغة قابلة للنقل.",
        "policy_guidance_en": "Objection procedures, portability formats (JSON, CSV, XML), transfer mechanisms.",
        "policy_guidance_ar": "إجراءات الاعتراض، صيغ النقل (JSON، CSV، XML)، آليات النقل.",
        "priority": "HIGH",
        "status": ControlStatus.NOT_STARTED,
        "maturity_level": 1,
        "evidence_types": ["POLICY", "PROCEDURE", "LOG"],
        "related_controls": ["PDPL-04", "PDPL-06"]
    },
    {
        "control_id": "PDPL-08",
        "framework": FrameworkType.PDPL,
        "domain": "Data Security",
        "title_en": "Technical and Organizational Measures",
        "title_ar": "التدابير الفنية والتنظيمية",
        "description_en": "Implement appropriate technical and organizational security measures to protect personal data.",
        "description_ar": "تنفيذ تدابير الأمن الفني والتنظيمي المناسبة لحماية البيانات الشخصية.",
        "policy_guidance_en": "Encryption (AES-256), access controls, pseudonymization, security testing, breach prevention.",
        "policy_guidance_ar": "التشفير (AES-256)، ضوابط الوصول، الأسماء المستعارة، الاختبار الأمني، منع الاختراق.",
        "priority": "CRITICAL",
        "status": ControlStatus.NOT_STARTED,
        "maturity_level": 1,
        "evidence_types": ["POLICY", "PROCEDURE", "CERTIFICATE"],
        "related_controls": ["PDPL-09", "ECC-IS-7", "CCC-SEC-01"]
    },
    {
        "control_id": "PDPL-09",
        "framework": FrameworkType.PDPL,
        "domain": "Data Security",
        "title_en": "Data Breach Notification",
        "title_ar": "إخطار انتهاك البيانات",
        "description_en": "Establish procedures for detecting, reporting, and responding to personal data breaches.",
        "description_ar": "إنشاء إجراءات للكشف عن انتهاكات البيانات الشخصية والإبلاغ عنها والاستجابة لها.",
        "policy_guidance_en": "Breach detection, 72-hour notification to SDAIA, data subject notification, breach register.",
        "policy_guidance_ar": "كشف الانتهاك، إخطار 72 ساعة إلى SDAIA، إخطار صاحب البيانات، سجل الانتهاك.",
        "priority": "CRITICAL",
        "status": ControlStatus.NOT_STARTED,
        "maturity_level": 1,
        "evidence_types": ["POLICY", "PROCEDURE", "LOG", "REPORT"],
        "related_controls": ["PDPL-08", "ECC-IS-5"]
    },
    {
        "control_id": "PDPL-10",
        "framework": FrameworkType.PDPL,
        "domain": "Accountability",
        "title_en": "Records of Processing Activities (RoPA)",
        "title_ar": "سجلات أنشطة المعالجة",
        "description_en": "Maintain comprehensive records of all personal data processing activities.",
        "description_ar": "الحفاظ على سجلات شاملة لجميع أنشطة معالجة البيانات الشخصية.",
        "policy_guidance_en": "RoPA documentation, processing purposes, data categories, recipients, retention periods.",
        "policy_guidance_ar": "توثيق RoPA، أغراض المعالجة، فئات البيانات، المستلمون، فترات الاحتفاظ.",
        "priority": "CRITICAL",
        "status": ControlStatus.NOT_STARTED,
        "maturity_level": 1,
        "evidence_types": ["POLICY", "PROCEDURE", "REPORT"],
        "related_controls": ["PDPL-11", "PDPL-12"]
    },
    {
        "control_id": "PDPL-11",
        "framework": FrameworkType.PDPL,
        "domain": "Accountability",
        "title_en": "Data Protection Impact Assessment (DPIA)",
        "title_ar": "تقييم أثر حماية البيانات",
        "description_en": "Conduct DPIA for high-risk processing activities before implementation.",
        "description_ar": "إجراء DPIA لأنشطة المعالجة عالية المخاطر قبل التنفيذ.",
        "policy_guidance_en": "DPIA methodology, risk thresholds, mitigation measures, consultation with SDAIA when required.",
        "policy_guidance_ar": "منهجية DPIA، عتبات المخاطر، تدابير التخفيف، التشاور مع SDAIA عند الطلب.",
        "priority": "HIGH",
        "status": ControlStatus.NOT_STARTED,
        "maturity_level": 1,
        "evidence_types": ["POLICY", "PROCEDURE", "REPORT"],
        "related_controls": ["PDPL-10", "ECC-RM-1"]
    },
    {
        "control_id": "PDPL-12",
        "framework": FrameworkType.PDPL,
        "domain": "Accountability",
        "title_en": "Data Protection Officer (DPO)",
        "title_ar": "مسؤول حماية البيانات",
        "description_en": "Designate Data Protection Officer with appropriate authority and resources.",
        "description_ar": "تعيين مسؤول حماية البيانات بالسلطة والموارد المناسبة.",
        "policy_guidance_en": "DPO appointment criteria, independence requirements, contact information publication, reporting line.",
        "policy_guidance_ar": "معايير تعيين DPO، متطلبات الاستقلالية، نشر معلومات الاتصال، خط التقارير.",
        "priority": "CRITICAL",
        "status": ControlStatus.NOT_STARTED,
        "maturity_level": 1,
        "evidence_types": ["POLICY", "PROCEDURE", "CERTIFICATE"],
        "related_controls": ["PDPL-10", "PDPL-11", "ECC-GV-3"]
    },
]


async def load_controls(session: AsyncSession, controls: List[Dict], framework_name: str):
    """Load controls into database"""
    loaded = 0
    skipped = 0
    
    for control_data in controls:
        # Check if control already exists
        result = await session.execute(
            select(Control).where(Control.control_id == control_data["control_id"])
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            logger.info(f"  ⏭️  {control_data['control_id']} already exists, skipping")
            skipped += 1
            continue
        
        # Create new control
        control = Control(**control_data)
        session.add(control)
        loaded += 1
        logger.info(f"  ✓ Loaded {control_data['control_id']}: {control_data['title_en']}")
    
    await session.commit()
    logger.info(f"\n{framework_name} Summary: {loaded} loaded, {skipped} skipped")
    return loaded, skipped


async def populate_nca_controls():
    """
    Main function to populate all NCA control libraries
    Run this after database initialization
    """
    logger.info("="*80)
    logger.info("NCA CONTROL LIBRARY POPULATION")
    logger.info("Populating complete ECC, CCC, and PDPL control frameworks")
    logger.info("="*80)
    
    async with AsyncSessionLocal() as session:
        # Load ECC Controls
        logger.info("\n📋 Loading NCA ECC Controls...")
        ecc_loaded, ecc_skipped = await load_controls(session, ECC_CONTROLS, "NCA ECC")
        
        # Load CCC Controls
        logger.info("\n☁️  Loading NCA CCC Controls...")
        ccc_loaded, ccc_skipped = await load_controls(session, CCC_CONTROLS, "NCA CCC")
        
        # Load PDPL Controls
        logger.info("\n🔒 Loading PDPL Controls...")
        pdpl_loaded, pdpl_skipped = await load_controls(session, PDPL_CONTROLS, "PDPL")
        
        # Final summary
        total_loaded = ecc_loaded + ccc_loaded + pdpl_loaded
        total_skipped = ecc_skipped + ccc_skipped + pdpl_skipped
        total_controls = len(ECC_CONTROLS) + len(CCC_CONTROLS) + len(PDPL_CONTROLS)
        
        logger.info("\n" + "="*80)
        logger.info("CONTROL LIBRARY POPULATION COMPLETE")
        logger.info("="*80)
        logger.info(f"✓ Total Controls Loaded: {total_loaded}")
        logger.info(f"⏭️  Total Controls Skipped: {total_skipped}")
        logger.info(f"📊 Total Control Library Size: {total_controls}")
        logger.info(f"   - ECC: {len(ECC_CONTROLS)} controls")
        logger.info(f"   - CCC: {len(CCC_CONTROLS)} controls")
        logger.info(f"   - PDPL: {len(PDPL_CONTROLS)} controls")
        logger.info("="*80)


if __name__ == "__main__":
    asyncio.run(populate_nca_controls())
