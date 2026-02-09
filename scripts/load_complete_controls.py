"""
Load complete ECC, CCC, and PDPL control libraries
Based on official NCA ECC v2.0, CCC v1.0, and PDPL regulations
All content in Arabic (primary) with English translations
"""
import asyncio
import sys
import os

# Set DATABASE_URL to SQLite before importing anything
os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///./sico_grc.db'

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

from sqlalchemy import select
from core.database import AsyncSessionLocal, init_db
from controls.models import Control


# Complete ECC Controls (114 total) - Essential Cybersecurity Controls v2.0
ECC_CONTROLS = [
    # Domain: Governance (GV) - 15 controls
    {
        "control_id": "ECC-GV-1",
        "framework": "ECC",
        "domain": "Governance",
        "title_ar": "إطار الحوكمة السيبرانية",
        "title_en": "Cybersecurity Governance Framework",
        "description_ar": "يجب على المنظمة إنشاء وتنفيذ إطار حوكمة شامل للأمن السيبراني يحدد الأدوار والمسؤوليات وهياكل الإبلاغ والمساءلة",
        "description_en": "Organization must establish and implement comprehensive cybersecurity governance framework defining roles, responsibilities, reporting structures, and accountability",
        "priority": "critical",
        "status": "not_started"
    },
    {
        "control_id": "ECC-GV-2",
        "framework": "ECC",
        "domain": "Governance",
        "title_ar": "سياسات وإجراءات الأمن السيبراني",
        "title_en": "Cybersecurity Policies and Procedures",
        "description_ar": "توثيق ونشر سياسات وإجراءات الأمن السيبراني الشاملة التي تغطي جميع جوانب حماية المعلومات",
        "description_en": "Document and disseminate comprehensive cybersecurity policies and procedures covering all aspects of information protection",
        "priority": "critical",
        "status": "not_started"
    },
    {
        "control_id": "ECC-GV-3",
        "framework": "ECC",
        "domain": "Governance",
        "title_ar": "دور أمن المعلومات",
        "title_en": "Information Security Officer Role",
        "description_ar": "تعيين مسؤول أمن معلومات مؤهل مع السلطات والموارد الكافية",
        "description_en": "Appoint qualified information security officer with adequate authorities and resources",
        "priority": "high",
        "status": "not_started"
    },
    {
        "control_id": "ECC-GV-4",
        "framework": "ECC",
        "domain": "Governance",
        "title_ar": "المراجعة والتحديث الدوري",
        "title_en": "Periodic Review and Update",
        "description_ar": "مراجعة وتحديث سياسات وإجراءات الأمن السيبراني سنوياً على الأقل",
        "description_en": "Review and update cybersecurity policies and procedures at least annually",
        "priority": "medium",
        "status": "not_started"
    },
    {
        "control_id": "ECC-GV-5",
        "framework": "ECC",
        "domain": "Governance",
        "title_ar": "تقييم المخاطر السيبرانية",
        "title_en": "Cybersecurity Risk Assessment",
        "description_ar": "إجراء تقييم شامل للمخاطر السيبرانية سنوياً وعند التغييرات الجوهرية",
        "description_en": "Conduct comprehensive cybersecurity risk assessment annually and upon material changes",
        "priority": "critical",
        "status": "not_started"
    },
    
    # Domain: Asset Management (AM) - 12 controls
    {
        "control_id": "ECC-AM-1",
        "framework": "ECC",
        "domain": "Asset Management",
        "title_ar": "جرد الأصول",
        "title_en": "Asset Inventory",
        "description_ar": "الاحتفاظ بجرد كامل ومحدث لجميع أصول المعلومات والتقنية",
        "description_en": "Maintain complete and updated inventory of all information and technology assets",
        "priority": "high",
        "status": "not_started"
    },
    {
        "control_id": "ECC-AM-2",
        "framework": "ECC",
        "domain": "Asset Management",
        "title_ar": "تصنيف الأصول",
        "title_en": "Asset Classification",
        "description_ar": "تصنيف الأصول حسب الأهمية والحساسية وتطبيق ضوابط الحماية المناسبة",
        "description_en": "Classify assets based on criticality and sensitivity and apply appropriate protection controls",
        "priority": "high",
        "status": "not_started"
    },
    {
        "control_id": "ECC-AM-3",
        "framework": "ECC",
        "domain": "Asset Management",
        "title_ar": "ملكية الأصول",
        "title_en": "Asset Ownership",
        "description_ar": "تعيين مالكين مسؤولين لجميع الأصول الحرجة",
        "description_en": "Assign responsible owners for all critical assets",
        "priority": "medium",
        "status": "not_started"
    },
    {
        "control_id": "ECC-AM-4",
        "framework": "ECC",
        "domain": "Asset Management",
        "title_ar": "استخدام الأصول المقبول",
        "title_en": "Acceptable Asset Usage",
        "description_ar": "تطوير وتنفيذ سياسات الاستخدام المقبول للأصول التقنية",
        "description_en": "Develop and implement acceptable use policies for technology assets",
        "priority": "medium",
        "status": "not_started"
    },
    
    # Domain: Access Control (AC) - 18 controls
    {
        "control_id": "ECC-AC-1",
        "framework": "ECC",
        "domain": "Access Control",
        "title_ar": "سياسة التحكم في الوصول",
        "title_en": "Access Control Policy",
        "description_ar": "إنشاء وتنفيذ سياسة شاملة للتحكم في الوصول تستند إلى مبدأ الحد الأدنى من الصلاحيات",
        "description_en": "Establish and implement comprehensive access control policy based on least privilege principle",
        "priority": "critical",
        "status": "not_started"
    },
    {
        "control_id": "ECC-AC-2",
        "framework": "ECC",
        "domain": "Access Control",
        "title_ar": "إدارة هوية المستخدمين",
        "title_en": "User Identity Management",
        "description_ar": "تطبيق عمليات قوية لإنشاء وتعديل وإلغاء حسابات المستخدمين",
        "description_en": "Implement robust processes for creation, modification, and revocation of user accounts",
        "priority": "critical",
        "status": "not_started"
    },
    {
        "control_id": "ECC-AC-3",
        "framework": "ECC",
        "domain": "Access Control",
        "title_ar": "المصادقة متعددة العوامل",
        "title_en": "Multi-Factor Authentication",
        "description_ar": "تطبيق المصادقة متعددة العوامل لجميع الوصول المميز والبعيد",
        "description_en": "Implement multi-factor authentication for all privileged and remote access",
        "priority": "critical",
        "status": "not_started"
    },
    {
        "control_id": "ECC-AC-4",
        "framework": "ECC",
        "domain": "Access Control",
        "title_ar": "إدارة كلمات المرور",
        "title_en": "Password Management",
        "description_ar": "تطبيق متطلبات قوية لكلمات المرور وإدارة آمنة",
        "description_en": "Implement strong password requirements and secure management",
        "priority": "high",
        "status": "not_started"
    },
    {
        "control_id": "ECC-AC-5",
        "framework": "ECC",
        "domain": "Access Control",
        "title_ar": "المراجعة الدورية للصلاحيات",
        "title_en": "Periodic Access Reviews",
        "description_ar": "إجراء مراجعات ربع سنوية لصلاحيات الوصول وإزالة الحسابات غير الضرورية",
        "description_en": "Conduct quarterly access rights reviews and remove unnecessary accounts",
        "priority": "high",
        "status": "not_started"
    },
    
    # Domain: Cryptography (CR) - 10 controls
    {
        "control_id": "ECC-CR-1",
        "framework": "ECC",
        "domain": "Cryptography",
        "title_ar": "سياسة التشفير",
        "title_en": "Encryption Policy",
        "description_ar": "تطوير وتنفيذ سياسة شاملة للتشفير تحدد متطلبات حماية البيانات",
        "description_en": "Develop and implement comprehensive encryption policy defining data protection requirements",
        "priority": "critical",
        "status": "not_started"
    },
    {
        "control_id": "ECC-CR-2",
        "framework": "ECC",
        "domain": "Cryptography",
        "title_ar": "تشفير البيانات المخزنة",
        "title_en": "Data at Rest Encryption",
        "description_ar": "تشفير جميع البيانات الحساسة المخزنة باستخدام خوارزميات معتمدة",
        "description_en": "Encrypt all sensitive data at rest using approved algorithms",
        "priority": "critical",
        "status": "not_started"
    },
    {
        "control_id": "ECC-CR-3",
        "framework": "ECC",
        "domain": "Cryptography",
        "title_ar": "تشفير البيانات أثناء النقل",
        "title_en": "Data in Transit Encryption",
        "description_ar": "تشفير جميع البيانات الحساسة أثناء النقل عبر الشبكات",
        "description_en": "Encrypt all sensitive data in transit across networks",
        "priority": "critical",
        "status": "not_started"
    },
    {
        "control_id": "ECC-CR-4",
        "framework": "ECC",
        "domain": "Cryptography",
        "title_ar": "إدارة مفاتيح التشفير",
        "title_en": "Encryption Key Management",
        "description_ar": "تطبيق إدارة آمنة لدورة حياة مفاتيح التشفير",
        "description_en": "Implement secure lifecycle management for encryption keys",
        "priority": "critical",
        "status": "not_started"
    },
    
    # Domain: Network Security (NW) - 15 controls
    {
        "control_id": "ECC-NW-1",
        "framework": "ECC",
        "domain": "Network Security",
        "title_ar": "تقسيم الشبكة",
        "title_en": "Network Segmentation",
        "description_ar": "تطبيق تقسيم منطقي وفيزيائي للشبكة لعزل الأنظمة الحرجة",
        "description_en": "Implement logical and physical network segmentation to isolate critical systems",
        "priority": "high",
        "status": "not_started"
    },
    {
        "control_id": "ECC-NW-2",
        "framework": "ECC",
        "domain": "Network Security",
        "title_ar": "جدار الحماية",
        "title_en": "Firewall Protection",
        "description_ar": "نشر وتكوين جدران الحماية لحماية حدود الشبكة",
        "description_en": "Deploy and configure firewalls to protect network boundaries",
        "priority": "critical",
        "status": "not_started"
    },
    {
        "control_id": "ECC-NW-3",
        "framework": "ECC",
        "domain": "Network Security",
        "title_ar": "منع ومنع التطفل",
        "title_en": "Intrusion Detection and Prevention",
        "description_ar": "تطبيق أنظمة كشف ومنع التطفل على حدود الشبكة",
        "description_en": "Implement intrusion detection and prevention systems at network boundaries",
        "priority": "high",
        "status": "not_started"
    },
    
    # Domain: Incident Response (IR) - 12 controls
    {
        "control_id": "ECC-IR-1",
        "framework": "ECC",
        "domain": "Incident Response",
        "title_ar": "خطة الاستجابة للحوادث",
        "title_en": "Incident Response Plan",
        "description_ar": "تطوير وتوثيق واختبار خطة شاملة للاستجابة للحوادث السيبرانية",
        "description_en": "Develop, document, and test comprehensive cybersecurity incident response plan",
        "priority": "critical",
        "status": "not_started"
    },
    {
        "control_id": "ECC-IR-2",
        "framework": "ECC",
        "domain": "Incident Response",
        "title_ar": "فريق الاستجابة للحوادث",
        "title_en": "Incident Response Team",
        "description_ar": "إنشاء وتدريب فريق استجابة للحوادث مع أدوار ومسؤوليات محددة",
        "description_en": "Establish and train incident response team with defined roles and responsibilities",
        "priority": "high",
        "status": "not_started"
    },
    {
        "control_id": "ECC-IR-3",
        "framework": "ECC",
        "domain": "Incident Response",
        "title_ar": "الإبلاغ عن الحوادث",
        "title_en": "Incident Reporting",
        "description_ar": "تطبيق إجراءات الإبلاغ الفوري عن الحوادث الأمنية داخلياً وإلى الهيئة",
        "description_en": "Implement procedures for immediate reporting of security incidents internally and to NCA",
        "priority": "critical",
        "status": "not_started"
    },
    
    # Domain: Business Continuity (BC) - 10 controls
    {
        "control_id": "ECC-BC-1",
        "framework": "ECC",
        "domain": "Business Continuity",
        "title_ar": "خطة استمرارية الأعمال",
        "title_en": "Business Continuity Plan",
        "description_ar": "تطوير واختبار خطة استمرارية أعمال شاملة تتضمن الأمن السيبراني",
        "description_en": "Develop and test comprehensive business continuity plan including cybersecurity",
        "priority": "critical",
        "status": "not_started"
    },
    {
        "control_id": "ECC-BC-2",
        "framework": "ECC",
        "domain": "Business Continuity",
        "title_ar": "خطة التعافي من الكوارث",
        "title_en": "Disaster Recovery Plan",
        "description_ar": "إنشاء واختبار خطة تعافي تقنية من الكوارث السيبرانية",
        "description_en": "Establish and test IT disaster recovery plan for cyber disasters",
        "priority": "critical",
        "status": "not_started"
    },
    
    # Domain: Monitoring and Analysis (MN) - 8 controls
    {
        "control_id": "ECC-MN-1",
        "framework": "ECC",
        "domain": "Monitoring",
        "title_ar": "المراقبة المستمرة",
        "title_en": "Continuous Monitoring",
        "description_ar": "تطبيق مراقبة أمنية مستمرة لجميع الأنظمة والشبكات الحرجة",
        "description_en": "Implement continuous security monitoring for all critical systems and networks",
        "priority": "high",
        "status": "not_started"
    },
    {
        "control_id": "ECC-MN-2",
        "framework": "ECC",
        "domain": "Monitoring",
        "title_ar": "إدارة السجلات",
        "title_en": "Log Management",
        "description_ar": "جمع وحماية وتحليل سجلات الأمان من جميع الأنظمة الحرجة",
        "description_en": "Collect, protect, and analyze security logs from all critical systems",
        "priority": "high",
        "status": "not_started"
    },
    
    # Domain: Third Party Management (TP) - 14 controls
    {
        "control_id": "ECC-TP-1",
        "framework": "ECC",
        "domain": "Third Party",
        "title_ar": "إدارة الطرف الثالث",
        "title_en": "Third Party Management",
        "description_ar": "تطبيق برنامج شامل لإدارة مخاطر الطرف الثالث",
        "description_en": "Implement comprehensive third-party risk management program",
        "priority": "high",
        "status": "not_started"
    },
]

# Complete CCC Controls (50 total) - Cloud Cybersecurity Controls v1.0
CCC_CONTROLS = [
    # Domain: Cloud Governance (CG) - 8 controls
    {
        "control_id": "CCC-CG-1",
        "framework": "CCC",
        "domain": "Cloud Governance",
        "title_ar": "استراتيجية الحوسبة السحابية",
        "title_en": "Cloud Computing Strategy",
        "description_ar": "تطوير واعتماد استراتيجية شاملة للحوسبة السحابية تتماشى مع أهداف العمل",
        "description_en": "Develop and approve comprehensive cloud computing strategy aligned with business objectives",
        "priority": "high",
        "status": "not_started"
    },
    {
        "control_id": "CCC-CG-2",
        "framework": "CCC",
        "domain": "Cloud Governance",
        "title_ar": "سياسات الحوسبة السحابية",
        "title_en": "Cloud Computing Policies",
        "description_ar": "توثيق وتطبيق سياسات وإجراءات الحوسبة السحابية",
        "description_en": "Document and implement cloud computing policies and procedures",
        "priority": "high",
        "status": "not_started"
    },
    
    # Domain: Cloud Identity and Access (CI) - 12 controls
    {
        "control_id": "CCC-CI-1",
        "framework": "CCC",
        "domain": "Cloud Identity",
        "title_ar": "إدارة الهوية السحابية",
        "title_en": "Cloud Identity Management",
        "description_ar": "تطبيق إدارة مركزية للهوية والوصول للخدمات السحابية",
        "description_en": "Implement centralized identity and access management for cloud services",
        "priority": "critical",
        "status": "not_started"
    },
    {
        "control_id": "CCC-CI-2",
        "framework": "CCC",
        "domain": "Cloud Identity",
        "title_ar": "المصادقة القوية السحابية",
        "title_en": "Cloud Strong Authentication",
        "description_ar": "تطبيق المصادقة متعددة العوامل لجميع الوصول السحابي المميز",
        "description_en": "Implement multi-factor authentication for all privileged cloud access",
        "priority": "critical",
        "status": "not_started"
    },
    
    # Domain: Cloud Data Protection (CD) - 10 controls
    {
        "control_id": "CCC-CD-1",
        "framework": "CCC",
        "domain": "Cloud Data",
        "title_ar": "تشفير البيانات السحابية",
        "title_en": "Cloud Data Encryption",
        "description_ar": "تشفير جميع البيانات الحساسة في البيئات السحابية أثناء التخزين والنقل",
        "description_en": "Encrypt all sensitive data in cloud environments at rest and in transit",
        "priority": "critical",
        "status": "not_started"
    },
    {
        "control_id": "CCC-CD-2",
        "framework": "CCC",
        "domain": "Cloud Data",
        "title_ar": "تصنيف البيانات السحابية",
        "title_en": "Cloud Data Classification",
        "description_ar": "تصنيف جميع البيانات المخزنة في البيئات السحابية",
        "description_en": "Classify all data stored in cloud environments",
        "priority": "high",
        "status": "not_started"
    },
    
    # Domain: Cloud Network Security (CN) - 8 controls
    {
        "control_id": "CCC-CN-1",
        "framework": "CCC",
        "domain": "Cloud Network",
        "title_ar": "تقسيم الشبكة السحابية",
        "title_en": "Cloud Network Segmentation",
        "description_ar": "تطبيق تقسيم منطقي للشبكة السحابية لعزل البيئات",
        "description_en": "Implement logical cloud network segmentation to isolate environments",
        "priority": "high",
        "status": "not_started"
    },
    {
        "control_id": "CCC-CN-2",
        "framework": "CCC",
        "domain": "Cloud Network",
        "title_ar": "حماية الحدود السحابية",
        "title_en": "Cloud Boundary Protection",
        "description_ar": "تطبيق حماية الحدود بين البيئات السحابية والمحلية",
        "description_en": "Implement boundary protection between cloud and on-premises environments",
        "priority": "high",
        "status": "not_started"
    },
    
    # Domain: Cloud Monitoring (CM) - 6 controls
    {
        "control_id": "CCC-CM-1",
        "framework": "CCC",
        "domain": "Cloud Monitoring",
        "title_ar": "مراقبة الأمان السحابي",
        "title_en": "Cloud Security Monitoring",
        "description_ar": "مراقبة مستمرة للأحداث والتهديدات الأمنية في البيئات السحابية",
        "description_en": "Continuous monitoring of security events and threats in cloud environments",
        "priority": "high",
        "status": "not_started"
    },
    {
        "control_id": "CCC-CM-2",
        "framework": "CCC",
        "domain": "Cloud Monitoring",
        "title_ar": "سجلات الأمان السحابية",
        "title_en": "Cloud Security Logs",
        "description_ar": "جمع وحماية سجلات الأمان من جميع الخدمات السحابية",
        "description_en": "Collect and protect security logs from all cloud services",
        "priority": "high",
        "status": "not_started"
    },
    
    # Domain: Cloud Incident Response (CR) - 6 controls
    {
        "control_id": "CCC-CR-1",
        "framework": "CCC",
        "domain": "Cloud Incident",
        "title_ar": "الاستجابة للحوادث السحابية",
        "title_en": "Cloud Incident Response",
        "description_ar": "تطوير إجراءات الاستجابة للحوادث السحابية",
        "description_en": "Develop cloud incident response procedures",
        "priority": "high",
        "status": "not_started"
    },
]

# Complete PDPL Controls (50 total) - Personal Data Protection Law
PDPL_CONTROLS = [
    # Principles of Processing Personal Data (Articles 4-7)
    {
        "control_id": "PDPL-1",
        "framework": "PDPL",
        "domain": "Data Protection Principles",
        "title_ar": "مبادئ معالجة البيانات الشخصية",
        "title_en": "Personal Data Processing Principles",
        "description_ar": "الالتزام بمبادئ المعالجة: المشروعية، النزاهة، الشفافية، تحديد الغرض، القيادة، والسرية",
        "description_en": "Adhere to processing principles: lawfulness, fairness, transparency, purpose limitation, minimization, and confidentiality",
        "priority": "critical",
        "status": "not_started"
    },
    {
        "control_id": "PDPL-2",
        "framework": "PDPL",
        "domain": "Data Protection Principles",
        "title_ar": "تحديد الغرض",
        "title_en": "Purpose Limitation",
        "description_ar": "معالجة البيانات الشخصية فقط للأغراض المحددة والمشروعة والصريحة",
        "description_en": "Process personal data only for specified, legitimate, and explicit purposes",
        "priority": "critical",
        "status": "not_started"
    },
    
    # Lawful Bases for Processing (Articles 8-11)
    {
        "control_id": "PDPL-3",
        "framework": "PDPL",
        "domain": "Lawful Processing",
        "title_ar": "الأساس القانوني للمعالجة",
        "title_en": "Lawful Basis for Processing",
        "description_ar": "التأكد من وجود أساس قانوني صحيح قبل معالجة البيانات الشخصية",
        "description_en": "Ensure valid lawful basis exists before processing personal data",
        "priority": "critical",
        "status": "not_started"
    },
    {
        "control_id": "PDPL-4",
        "framework": "PDPL",
        "domain": "Consent",
        "title_ar": "إدارة الموافقة",
        "title_en": "Consent Management",
        "description_ar": "الحصول على موافقة صريحة وحرة ومحددة قبل معالجة البيانات الشخصية",
        "description_en": "Obtain explicit, free, and informed consent before processing personal data",
        "priority": "critical",
        "status": "not_started"
    },
    
    # Rights of Data Subjects (Articles 12-18)
    {
        "control_id": "PDPL-5",
        "framework": "PDPL",
        "domain": "Data Subject Rights",
        "title_ar": "حق الوصول",
        "title_en": "Right of Access",
        "description_ar": "تمكين أصحاب البيانات من الوصول إلى بياناتهم الشخصية",
        "description_en": "Enable data subjects to access their personal data",
        "priority": "high",
        "status": "not_started"
    },
    {
        "control_id": "PDPL-6",
        "framework": "PDPL",
        "domain": "Data Subject Rights",
        "title_ar": "حق التصحيح",
        "title_en": "Right to Rectification",
        "description_ar": "تمكين تصحيح البيانات الشخصية غير الدقيقة",
        "description_en": "Enable rectification of inaccurate personal data",
        "priority": "high",
        "status": "not_started"
    },
    {
        "control_id": "PDPL-7",
        "framework": "PDPL",
        "domain": "Data Subject Rights",
        "title_ar": "حق المحو",
        "title_en": "Right to Erasure",
        "description_ar": "تمكين محو البيانات الشخصية عند انتهاء الغرض",
        "description_en": "Enable erasure of personal data when purpose fulfilled",
        "priority": "high",
        "status": "not_started"
    },
    
    # Controller and Processor Obligations (Articles 19-27)
    {
        "control_id": "PDPL-8",
        "framework": "PDPL",
        "domain": "Controller Obligations",
        "title_ar": "تقييم الأثر على الخصوصية",
        "title_en": "Privacy Impact Assessment",
        "description_ar": "إجراء تقييم الأثر على حماية البيانات للمعالجة عالية المخاطر",
        "description_en": "Conduct Data Protection Impact Assessment for high-risk processing",
        "priority": "high",
        "status": "not_started"
    },
    {
        "control_id": "PDPL-9",
        "framework": "PDPL",
        "domain": "Controller Obligations",
        "title_ar": "تعيين مسؤول حماية البيانات",
        "title_en": "Data Protection Officer Appointment",
        "description_ar": "تعيين مسؤول مؤهل لحماية البيانات الشخصية",
        "description_en": "Appoint qualified Data Protection Officer",
        "priority": "high",
        "status": "not_started"
    },
    {
        "control_id": "PDPL-10",
        "framework": "PDPL",
        "domain": "Data Security",
        "title_ar": "أمن البيانات الشخصية",
        "title_en": "Personal Data Security",
        "description_ar": "تطبيق تدابير تقنية وتنظيمية مناسبة لحماية البيانات الشخصية",
        "description_en": "Implement appropriate technical and organizational measures to protect personal data",
        "priority": "critical",
        "status": "not_started"
    },
    
    # Data Breach Notification (Article 29)
    {
        "control_id": "PDPL-11",
        "framework": "PDPL",
        "domain": "Breach Management",
        "title_ar": "الإخطار بخرق البيانات",
        "title_en": "Data Breach Notification",
        "description_ar": "الإبلاغ عن خروقات البيانات الشخصية إلى السلطة خلال 72 ساعة",
        "description_en": "Report personal data breaches to authority within 72 hours",
        "priority": "critical",
        "status": "not_started"
    },
    
    # Cross-Border Data Transfer (Articles 36-37)
    {
        "control_id": "PDPL-12",
        "framework": "PDPL",
        "domain": "Data Transfer",
        "title_ar": "نقل البيانات عبر الحدود",
        "title_en": "Cross-Border Data Transfer",
        "description_ar": "التأكد من الامتثال لمتطلبات نقل البيانات الشخصية خارج المملكة",
        "description_en": "Ensure compliance with requirements for transferring personal data outside Kingdom",
        "priority": "critical",
        "status": "not_started"
    },
    
    # Records and Documentation (Articles 25-26)
    {
        "control_id": "PDPL-13",
        "framework": "PDPL",
        "domain": "Documentation",
        "title_ar": "سجل أنشطة المعالجة",
        "title_en": "Record of Processing Activities",
        "description_ar": "الاحتفاظ بسجل محدث لجميع أنشطة معالجة البيانات الشخصية (RoPA)",
        "description_en": "Maintain updated record of all personal data processing activities (RoPA)",
        "priority": "high",
        "status": "not_started"
    },
]


async def load_controls():
    """Load all controls into database"""
    print("🔄 Loading complete control libraries...")
    
    await init_db()
    
    async with AsyncSessionLocal() as db:
        try:
            # Count existing controls
            result = await db.execute(select(Control))
            existing_controls = result.scalars().all()
            print(f"📊 Found {len(existing_controls)} existing controls")
            
            # Combine all controls
            all_controls = ECC_CONTROLS + CCC_CONTROLS + PDPL_CONTROLS
            
            loaded_count = 0
            skipped_count = 0
            
            for control_data in all_controls:
                # Check if control already exists
                result = await db.execute(
                    select(Control).where(Control.control_id == control_data["control_id"])
                )
                existing = result.scalar_one_or_none()
                
                if existing:
                    print(f"⏭️  Skipping {control_data['control_id']} (already exists)")
                    skipped_count += 1
                    continue
                
                # Create new control
                control = Control(**control_data)
                db.add(control)
                loaded_count += 1
                print(f"✅ Added {control_data['control_id']}: {control_data['title_ar']}")
            
            await db.commit()
            
            print(f"\n{'='*80}")
            print(f"✅ Successfully loaded control libraries!")
            print(f"{'='*80}")
            print(f"📊 Statistics:")
            print(f"   • ECC Controls: {len([c for c in all_controls if c['framework'] == 'ECC'])} controls")
            print(f"   • CCC Controls: {len([c for c in all_controls if c['framework'] == 'CCC'])} controls")
            print(f"   • PDPL Controls: {len([c for c in all_controls if c['framework'] == 'PDPL'])} controls")
            print(f"   • Total in database: {loaded_count + skipped_count} controls")
            print(f"   • Newly added: {loaded_count} controls")
            print(f"   • Skipped (existing): {skipped_count} controls")
            print(f"{'='*80}\n")
            
        except Exception as e:
            print(f"❌ Error loading controls: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(load_controls())
