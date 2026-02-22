"""
SICO GRC Platform - Saudi Framework Data Loader
Loads comprehensive Saudi regulatory framework controls (ECC, CCC, PDPL)
"""

import sqlite3
import json
from datetime import datetime, timedelta, date
from pathlib import Path

DB_PATH = Path(__file__).parent / "sico_grc.db"

def load_saudi_frameworks():
    """Load Saudi regulatory framework controls with bilingual support"""
    
    print("🇸🇦 Loading Saudi Framework Controls...")
    print("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # ============================================================================
    # 1. NCA ECC (Essential Cybersecurity Controls) - Comprehensive
    # ============================================================================
    print("🛡️ Loading NCA ECC Framework...")
    
    ecc_controls = [
        # Governance Domain (ECC-1)
        {
            "control_id": "ECC-1-1",
            "framework": "ECC",
            "domain": "Governance",
            "title_en": "Cybersecurity Governance Framework",
            "title_ar": "إطار حوكمة الأمن السيبراني",
            "description_en": "Establish and maintain a comprehensive cybersecurity governance framework with defined roles, responsibilities, and accountability structures.",
            "description_ar": "إنشاء والحفاظ على إطار شامل لحوكمة الأمن السيبراني مع أدوار ومسؤوليات وهياكل مساءلة محددة.",
            "control_type": "governance",
            "status": "active",
            "priority": "critical",
            "category": "governance",
            "nca_classification": "essential"
        },
        {
            "control_id": "ECC-1-2",
            "framework": "ECC",
            "domain": "Governance",
            "title_en": "Cybersecurity Strategy",
            "title_ar": "استراتيجية الأمن السيبراني",
            "description_en": "Develop and implement a comprehensive cybersecurity strategy aligned with business objectives and risk appetite.",
            "description_ar": "تطوير وتنفيذ استراتيجية شاملة للأمن السيبراني متوافقة مع أهداف الأعمال ورغبة المخاطرة.",
            "control_type": "governance",
            "status": "active",
            "priority": "critical",
            "category": "governance",
            "nca_classification": "essential"
        },
        {
            "control_id": "ECC-1-3",
            "framework": "ECC",
            "domain": "Governance",
            "title_en": "Cybersecurity Policies and Procedures",
            "title_ar": "سياسات وإجراءات الأمن السيبراني",
            "description_en": "Establish comprehensive cybersecurity policies and procedures covering all aspects of information security.",
            "description_ar": "إنشاء سياسات وإجراءات شاملة للأمن السيبراني تغطي جميع جوانب أمن المعلومات.",
            "control_type": "governance",
            "status": "active",
            "priority": "high",
            "category": "governance",
            "nca_classification": "essential"
        },
        # Cybersecurity Risk Management (ECC-2)
        {
            "control_id": "ECC-2-1",
            "framework": "ECC",
            "domain": "Risk Management",
            "title_en": "Cybersecurity Risk Assessment",
            "title_ar": "تقييم مخاطر الأمن السيبراني",
            "description_en": "Conduct regular cybersecurity risk assessments to identify, analyze, and evaluate risks.",
            "description_ar": "إجراء تقييمات منتظمة لمخاطر الأمن السيبراني لتحديد وتحليل وتقييم المخاطر.",
            "control_type": "assessment",
            "status": "active",
            "priority": "critical",
            "category": "risk_management",
            "nca_classification": "essential"
        },
        {
            "control_id": "ECC-2-2",
            "framework": "ECC",
            "domain": "Risk Management",
            "title_en": "Risk Treatment Plans",
            "title_ar": "خطط معالجة المخاطر",
            "description_en": "Develop and implement risk treatment plans for identified cybersecurity risks.",
            "description_ar": "تطوير وتنفيذ خطط معالجة المخاطر للمخاطر السيبرانية المحددة.",
            "control_type": "procedural",
            "status": "active",
            "priority": "high",
            "category": "risk_management",
            "nca_classification": "essential"
        },
        # Access Control (ECC-3)
        {
            "control_id": "ECC-3-1",
            "framework": "ECC",
            "domain": "Access Control",
            "title_en": "User Access Management",
            "title_ar": "إدارة وصول المستخدمين",
            "description_en": "Implement user access management processes including provisioning, review, and deprovisioning.",
            "description_ar": "تنفيذ عمليات إدارة وصول المستخدمين بما في ذلك التزويد والمراجعة وإلغاء التزويد.",
            "control_type": "technical",
            "status": "active",
            "priority": "critical",
            "category": "access_control",
            "nca_classification": "essential"
        },
        {
            "control_id": "ECC-3-2",
            "framework": "ECC",
            "domain": "Access Control",
            "title_en": "Multi-Factor Authentication",
            "title_ar": "المصادقة متعددة العوامل",
            "description_en": "Implement multi-factor authentication for all remote access and privileged accounts.",
            "description_ar": "تنفيذ المصادقة متعددة العوامل لجميع الوصول عن بعد والحسابات المميزة.",
            "control_type": "technical",
            "status": "active",
            "priority": "critical",
            "category": "access_control",
            "nca_classification": "essential"
        },
        {
            "control_id": "ECC-3-3",
            "framework": "ECC",
            "domain": "Access Control",
            "title_en": "Privileged Access Management",
            "title_ar": "إدارة الوصول المميز",
            "description_en": "Implement privileged access management controls with monitoring and logging.",
            "description_ar": "تنفيذ ضوابط إدارة الوصول المميز مع المراقبة والتسجيل.",
            "control_type": "technical",
            "status": "active",
            "priority": "critical",
            "category": "access_control",
            "nca_classification": "essential"
        },
        # Cybersecurity Operations (ECC-4)
        {
            "control_id": "ECC-4-1",
            "framework": "ECC",
            "domain": "Cybersecurity Operations",
            "title_en": "Security Monitoring",
            "title_ar": "المراقبة الأمنية",
            "description_en": "Implement 24/7 security monitoring and logging of critical systems.",
            "description_ar": "تنفيذ المراقبة الأمنية وتسجيل الأنظمة الحرجة على مدار الساعة.",
            "control_type": "technical",
            "status": "active",
            "priority": "critical",
            "category": "operations",
            "nca_classification": "essential"
        },
        {
            "control_id": "ECC-4-2",
            "framework": "ECC",
            "domain": "Cybersecurity Operations",
            "title_en": "Incident Response",
            "title_ar": "الاستجابة للحوادث",
            "description_en": "Establish and maintain incident response capability with defined procedures and team.",
            "description_ar": "إنشاء والحفاظ على قدرة الاستجابة للحوادث مع إجراءات وفريق محدد.",
            "control_type": "procedural",
            "status": "active",
            "priority": "critical",
            "category": "operations",
            "nca_classification": "essential"
        },
        {
            "control_id": "ECC-4-3",
            "framework": "ECC",
            "domain": "Cybersecurity Operations",
            "title_en": "Vulnerability Management",
            "title_ar": "إدارة الثغرات",
            "description_en": "Implement vulnerability management program including scanning and patching.",
            "description_ar": "تنفيذ برنامج إدارة الثغرات بما في ذلك الفحص والتصحيح.",
            "control_type": "technical",
            "status": "active",
            "priority": "critical",
            "category": "operations",
            "nca_classification": "essential"
        },
        # Resilience (ECC-5)
        {
            "control_id": "ECC-5-1",
            "framework": "ECC",
            "domain": "Resilience",
            "title_en": "Business Continuity Planning",
            "title_ar": "تخطيط استمرارية الأعمال",
            "description_en": "Develop and maintain business continuity and disaster recovery plans.",
            "description_ar": "تطوير والحفاظ على خطط استمرارية الأعمال والتعافي من الكوارث.",
            "control_type": "procedural",
            "status": "active",
            "priority": "critical",
            "category": "resilience",
            "nca_classification": "essential"
        },
        {
            "control_id": "ECC-5-2",
            "framework": "ECC",
            "domain": "Resilience",
            "title_en": "Backup and Recovery",
            "title_ar": "النسخ الاحتياطي والاستعادة",
            "description_en": "Implement regular backup procedures with tested recovery mechanisms.",
            "description_ar": "تنفيذ إجراءات نسخ احتياطي منتظمة مع آليات استعادة مختبرة.",
            "control_type": "technical",
            "status": "active",
            "priority": "critical",
            "category": "resilience",
            "nca_classification": "essential"
        },
        # Third-Party Cybersecurity (ECC-6)
        {
            "control_id": "ECC-6-1",
            "framework": "ECC",
            "domain": "Third-Party Security",
            "title_en": "Vendor Risk Management",
            "title_ar": "إدارة مخاطر الموردين",
            "description_en": "Implement third-party risk management program with security assessments.",
            "description_ar": "تنفيذ برنامج إدارة مخاطر الأطراف الثالثة مع تقييمات أمنية.",
            "control_type": "assessment",
            "status": "active",
            "priority": "high",
            "category": "third_party",
            "nca_classification": "essential"
        },
        {
            "control_id": "ECC-6-2",
            "framework": "ECC",
            "domain": "Third-Party Security",
            "title_en": "Vendor Security Contracts",
            "title_ar": "عقود أمن الموردين",
            "description_en": "Include cybersecurity requirements in vendor contracts and agreements.",
            "description_ar": "تضمين متطلبات الأمن السيبراني في عقود واتفاقيات الموردين.",
            "control_type": "governance",
            "status": "active",
            "priority": "high",
            "category": "third_party",
            "nca_classification": "essential"
        },
        # Cybersecurity Awareness (ECC-7)
        {
            "control_id": "ECC-7-1",
            "framework": "ECC",
            "domain": "Awareness",
            "title_en": "Security Awareness Training",
            "title_ar": "التدريب على التوعية الأمنية",
            "description_en": "Provide regular cybersecurity awareness training to all employees.",
            "description_ar": "توفير تدريب منتظم على التوعية بالأمن السيبراني لجميع الموظفين.",
            "control_type": "procedural",
            "status": "active",
            "priority": "high",
            "category": "awareness",
            "nca_classification": "essential"
        },
    ]
    
    # Insert ECC controls
    for control in ecc_controls:
        cursor.execute("""
            INSERT INTO controls (control_id, framework, domain, title_en, title_ar, 
                                description_en, description_ar, priority, status, 
                                maturity_level, evidence_types, related_controls)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 3, '[]', '{}')
        """, (
            control["control_id"],
            control["framework"],
            control["domain"],
            control["title_en"],
            control["title_ar"],
            control["description_en"],
            control["description_ar"],
            control["priority"],
            control["status"]
        ))
    
    print(f"   ✓ Loaded {len(ecc_controls)} ECC controls")
    
    # ============================================================================
    # 2. NCA CCC (Cloud Cybersecurity Controls)
    # ============================================================================
    print("☁️ Loading NCA CCC Framework...")
    
    ccc_controls = [
        {
            "control_id": "CCC-1-1",
            "framework": "CCC",
            "domain": "Data Security",
            "title_en": "Data Classification in Cloud",
            "title_ar": "تصنيف البيانات في السحابة",
            "description_en": "Classify data stored in cloud environments based on sensitivity.",
            "description_ar": "تصنيف البيانات المخزنة في البيئات السحابية بناءً على الحساسية.",
            "control_type": "governance",
            "status": "active",
            "priority": "critical"
        },
        {
            "control_id": "CCC-1-2",
            "framework": "CCC",
            "domain": "Data Security",
            "title_en": "Cloud Data Encryption",
            "title_ar": "تشفير البيانات السحابية",
            "description_en": "Encrypt sensitive data at rest and in transit in cloud environments.",
            "description_ar": "تشفير البيانات الحساسة أثناء التخزين والنقل في البيئات السحابية.",
            "control_type": "technical",
            "status": "active",
            "priority": "critical"
        },
        {
            "control_id": "CCC-2-1",
            "framework": "CCC",
            "domain": "Identity and Access",
            "title_en": "Cloud IAM",
            "title_ar": "إدارة الهوية والوصول السحابي",
            "description_en": "Implement identity and access management for cloud services.",
            "description_ar": "تنفيذ إدارة الهوية والوصول للخدمات السحابية.",
            "control_type": "technical",
            "status": "active",
            "priority": "critical"
        },
        {
            "control_id": "CCC-3-1",
            "framework": "CCC",
            "domain": "Infrastructure Security",
            "title_en": "Cloud Security Architecture",
            "title_ar": "بنية الأمن السحابي",
            "description_en": "Design secure cloud architecture with defense in depth.",
            "description_ar": "تصميم بنية سحابية آمنة مع الدفاع في العمق.",
            "control_type": "technical",
            "status": "active",
            "priority": "high"
        },
        {
            "control_id": "CCC-4-1",
            "framework": "CCC",
            "domain": "Compliance",
            "title_en": "Cloud Compliance Monitoring",
            "title_ar": "مراقبة الامتثال السحابي",
            "description_en": "Monitor cloud services for compliance with regulations.",
            "description_ar": "مراقبة الخدمات السحابية للامتثال للأنظمة.",
            "control_type": "assessment",
            "status": "active",
            "priority": "high"
        },
    ]
    
    for control in ccc_controls:
        cursor.execute("""
            INSERT INTO controls (control_id, framework, domain, title_en, title_ar, 
                                description_en, description_ar, priority, status, 
                                maturity_level, evidence_types, related_controls)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 3, '[]', '{}')
        """, (
            control["control_id"],
            control["framework"],
            control["domain"],
            control["title_en"],
            control["title_ar"],
            control["description_en"],
            control["description_ar"],
            control["priority"],
            control["status"]
        ))
    
    print(f"   ✓ Loaded {len(ccc_controls)} CCC controls")
    
    # ============================================================================
    # 3. PDPL (Personal Data Protection Law)
    # ============================================================================
    print("🔒 Loading PDPL Framework...")
    
    pdpl_controls = [
        {
            "control_id": "PDPL-1",
            "framework": "PDPL",
            "domain": "Legal Basis",
            "title_en": "Lawful Processing of Personal Data",
            "title_ar": "المعالجة القانونية للبيانات الشخصية",
            "description_en": "Ensure personal data processing has valid legal basis (consent, contract, legal obligation).",
            "description_ar": "ضمان أن معالجة البيانات الشخصية لها أساس قانوني صحيح (موافقة، عقد، التزام قانوني).",
            "control_type": "governance",
            "status": "active",
            "priority": "critical"
        },
        {
            "control_id": "PDPL-2",
            "framework": "PDPL",
            "domain": "Data Subject Rights",
            "title_en": "Data Subject Rights Management",
            "title_ar": "إدارة حقوق صاحب البيانات",
            "description_en": "Implement processes for handling data subject access, correction, deletion requests.",
            "description_ar": "تنفيذ عمليات للتعامل مع طلبات الوصول والتصحيح والحذف من صاحب البيانات.",
            "control_type": "procedural",
            "status": "active",
            "priority": "critical"
        },
        {
            "control_id": "PDPL-3",
            "framework": "PDPL",
            "domain": "Consent Management",
            "title_en": "Consent Capture and Management",
            "title_ar": "الحصول على الموافقة وإدارتها",
            "description_en": "Obtain and manage explicit consent for personal data processing.",
            "description_ar": "الحصول على وإدارة موافقة صريحة لمعالجة البيانات الشخصية.",
            "control_type": "technical",
            "status": "active",
            "priority": "critical"
        },
        {
            "control_id": "PDPL-4",
            "framework": "PDPL",
            "domain": "Data Security",
            "title_en": "Personal Data Security",
            "title_ar": "أمن البيانات الشخصية",
            "description_en": "Implement technical and organizational measures to protect personal data.",
            "description_ar": "تنفيذ تدابير تقنية وتنظيمية لحماية البيانات الشخصية.",
            "control_type": "technical",
            "status": "active",
            "priority": "critical"
        },
        {
            "control_id": "PDPL-5",
            "framework": "PDPL",
            "domain": "Breach Notification",
            "title_en": "Data Breach Response",
            "title_ar": "الاستجابة لخرق البيانات",
            "description_en": "Notify SDAIA of personal data breaches within 72 hours.",
            "description_ar": "إخطار هيئة البيانات والذكاء الاصطناعي بخروقات البيانات الشخصية خلال 72 ساعة.",
            "control_type": "procedural",
            "status": "active",
            "priority": "critical"
        },
        {
            "control_id": "PDPL-6",
            "framework": "PDPL",
            "domain": "Records",
            "title_en": "Record of Processing Activities (RoPA)",
            "title_ar": "سجل أنشطة المعالجة",
            "description_en": "Maintain comprehensive record of personal data processing activities.",
            "description_ar": "الحفاظ على سجل شامل لأنشطة معالجة البيانات الشخصية.",
            "control_type": "governance",
            "status": "active",
            "priority": "high"
        },
        {
            "control_id": "PDPL-7",
            "framework": "PDPL",
            "domain": "Data Transfer",
            "title_en": "Cross-Border Data Transfer",
            "title_ar": "نقل البيانات عبر الحدود",
            "description_en": "Ensure appropriate safeguards for cross-border personal data transfers.",
            "description_ar": "ضمان ضمانات مناسبة لنقل البيانات الشخصية عبر الحدود.",
            "control_type": "governance",
            "status": "active",
            "priority": "high"
        },
        {
            "control_id": "PDPL-8",
            "framework": "PDPL",
            "domain": "DPO",
            "title_en": "Data Protection Officer",
            "title_ar": "مسؤول حماية البيانات",
            "description_en": "Appoint qualified Data Protection Officer with appropriate authority.",
            "description_ar": "تعيين مسؤول حماية بيانات مؤهل بصلاحيات مناسبة.",
            "control_type": "governance",
            "status": "active",
            "priority": "high"
        },
    ]
    
    for control in pdpl_controls:
        cursor.execute("""
            INSERT INTO controls (control_id, framework, domain, title_en, title_ar, 
                                description_en, description_ar, priority, status, 
                                maturity_level, evidence_types, related_controls)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 3, '[]', '{}')
        """, (
            control["control_id"],
            control["framework"],
            control["domain"],
            control["title_en"],
            control["title_ar"],
            control["description_en"],
            control["description_ar"],
            control["priority"],
            control["status"]
        ))
    
    print(f"   ✓ Loaded {len(pdpl_controls)} PDPL controls")
    
    # ============================================================================
    # 4. ISO 27001 Controls (International Benchmark)
    # ============================================================================
    print("🌍 Loading ISO 27001 Controls...")
    
    iso_controls = [
        {
            "control_id": "ISO-A.5.1",
            "framework": "ISO27001",
            "domain": "Organizational",
            "title_en": "Policies for Information Security",
            "title_ar": "سياسات أمن المعلومات",
            "description_en": "Information security policy shall be defined, approved by management, published and communicated.",
            "description_ar": "يجب تحديد سياسة أمن المعلومات والموافقة عليها من قبل الإدارة ونشرها وإبلاغها.",
            "control_type": "governance",
            "status": "active",
            "priority": "high"
        },
        {
            "control_id": "ISO-A.5.2",
            "framework": "ISO27001",
            "domain": "Organizational",
            "title_en": "Information Security Roles and Responsibilities",
            "title_ar": "أدوار ومسؤوليات أمن المعلومات",
            "description_en": "Information security roles and responsibilities shall be defined and allocated.",
            "description_ar": "يجب تحديد وتخصيص أدوار ومسؤوليات أمن المعلومات.",
            "control_type": "governance",
            "status": "active",
            "priority": "high"
        },
        {
            "control_id": "ISO-A.8.1",
            "framework": "ISO27001",
            "domain": "Asset Management",
            "title_en": "Inventory of Assets",
            "title_ar": "جرد الأصول",
            "description_en": "Assets associated with information shall be identified and inventory maintained.",
            "description_ar": "يجب تحديد الأصول المرتبطة بالمعلومات والحفاظ على جردها.",
            "control_type": "procedural",
            "status": "active",
            "priority": "high"
        },
    ]
    
    for control in iso_controls:
        cursor.execute("""
            INSERT INTO controls (control_id, framework, domain, title_en, title_ar, 
                                description_en, description_ar, priority, status, 
                                maturity_level, evidence_types, related_controls)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 3, '[]', '{}')
        """, (
            control["control_id"],
            control["framework"],
            control["domain"],
            control["title_en"],
            control["title_ar"],
            control["description_en"],
            control["description_ar"],
            control["priority"],
            control["status"]
        ))
    
    print(f"   ✓ Loaded {len(iso_controls)} ISO 27001 controls")
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("=" * 60)
    print("✅ Saudi Framework Loading Complete!")
    print(f"📊 Total Controls Loaded:")
    print(f"   - ECC: {len(ecc_controls)}")
    print(f"   - CCC: {len(ccc_controls)}")
    print(f"   - PDPL: {len(pdpl_controls)}")
    print(f"   - ISO 27001: {len(iso_controls)}")
    print(f"   - TOTAL: {len(ecc_controls) + len(ccc_controls) + len(pdpl_controls) + len(iso_controls)}")
    print("🇸🇦 Saudi Compliance Ready!")

if __name__ == "__main__":
    load_saudi_frameworks()
