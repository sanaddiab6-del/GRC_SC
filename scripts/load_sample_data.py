#!/usr/bin/env python3
"""
Sample Data Loader Script
Loads sample ECC, CCC, and PDPL controls into the database
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src/backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "backend"))

from sqlalchemy.ext.asyncio import AsyncSession
from core.database import AsyncSessionLocal, init_db
from controls.models import Control, FrameworkType, ControlStatus


SAMPLE_CONTROLS = [
    {
        "control_id": "ECC-GV-1",
        "framework": FrameworkType.ECC,
        "domain": "Governance",
        "title_en": "Governance Framework",
        "title_ar": "إطار الحوكمة",
        "description_en": "The institution shall establish and maintain a comprehensive governance framework that ensures effective oversight, accountability, and decision-making processes.",
        "description_ar": "يجب على المؤسسة إنشاء والحفاظ على إطار حوكمة شامل يضمن الرقابة الفعالة والمساءلة وعمليات اتخاذ القرار.",
        "policy_guidance_en": "Develop a board-approved governance policy that defines roles, responsibilities, and reporting structures. Include cybersecurity governance in the framework.",
        "policy_guidance_ar": "تطوير سياسة حوكمة معتمدة من مجلس الإدارة تحدد الأدوار والمسؤوليات وهياكل الإبلاغ. تضمين حوكمة الأمن السيبراني في الإطار.",
        "procedure_guidance_en": "1. Document organizational structure\n2. Define decision-making authority\n3. Establish reporting lines\n4. Conduct quarterly governance reviews",
        "procedure_guidance_ar": "1. توثيق الهيكل التنظيمي\n2. تحديد سلطة اتخاذ القرار\n3. إنشاء خطوط الإبلاغ\n4. إجراء مراجعات ربع سنوية للحوكمة",
        "priority": "critical",
        "status": ControlStatus.COMPLIANT,
        "maturity_level": 4,
        "evidence_types": ["governance_policy", "organizational_chart", "board_minutes"],
        "related_controls": {"CCC": ["CCC-GOV-01"], "PDPL": ["PDPL-1"]},
    },
    {
        "control_id": "ECC-IS-1",
        "framework": FrameworkType.ECC,
        "domain": "Information Security",
        "title_en": "Information Security Policy",
        "title_ar": "سياسة أمن المعلومات",
        "description_en": "Establish and maintain a comprehensive information security policy that covers all aspects of cybersecurity.",
        "description_ar": "إنشاء والحفاظ على سياسة شاملة لأمن المعلومات تغطي جميع جوانب الأمن السيبراني.",
        "policy_guidance_en": "Create an information security policy approved by senior management, covering confidentiality, integrity, and availability.",
        "policy_guidance_ar": "إنشاء سياسة أمن المعلومات معتمدة من الإدارة العليا، تغطي السرية والنزاهة والتوافر.",
        "priority": "high",
        "status": ControlStatus.IN_PROGRESS,
        "maturity_level": 3,
        "evidence_types": ["policy", "approval_document"],
        "related_controls": {"CCC": ["CCC-SEC-01"]},
    },
    {
        "control_id": "CCC-GOV-01",
        "framework": FrameworkType.CCC,
        "domain": "Governance",
        "title_en": "Cloud Governance Framework",
        "title_ar": "إطار حوكمة الحوسبة السحابية",
        "description_en": "Establish governance framework for cloud computing services including roles, responsibilities, and oversight mechanisms.",
        "description_ar": "إنشاء إطار حوكمة لخدمات الحوسبة السحابية يتضمن الأدوار والمسؤوليات وآليات الرقابة.",
        "priority": "high",
        "status": ControlStatus.NOT_STARTED,
        "maturity_level": 2,
        "evidence_types": ["cloud_governance_policy", "role_definition"],
        "related_controls": {"ECC": ["ECC-GV-1"]},
    },
    {
        "control_id": "CCC-SEC-01",
        "framework": FrameworkType.CCC,
        "domain": "Security",
        "title_en": "Cloud Security Controls",
        "title_ar": "ضوابط أمن السحابة",
        "description_en": "Implement appropriate security controls for cloud computing environments including access control, encryption, and monitoring.",
        "description_ar": "تنفيذ ضوابط الأمان المناسبة لبيئات الحوسبة السحابية بما في ذلك التحكم في الوصول والتشفير والمراقبة.",
        "priority": "critical",
        "status": ControlStatus.IN_PROGRESS,
        "maturity_level": 3,
        "evidence_types": ["security_config", "access_logs", "encryption_cert"],
        "related_controls": {"ECC": ["ECC-IS-1"]},
    },
    {
        "control_id": "PDPL-1",
        "framework": FrameworkType.PDPL,
        "domain": "Data Protection",
        "title_en": "Personal Data Processing Policy",
        "title_ar": "سياسة معالجة البيانات الشخصية",
        "description_en": "Establish policies and procedures for processing personal data in compliance with PDPL requirements.",
        "description_ar": "إنشاء سياسات وإجراءات لمعالجة البيانات الشخصية وفقًا لمتطلبات نظام حماية البيانات الشخصية.",
        "policy_guidance_en": "Document data processing activities, purposes, legal basis, and retention periods.",
        "policy_guidance_ar": "توثيق أنشطة معالجة البيانات والأغراض والأساس القانوني وفترات الاحتفاظ.",
        "priority": "critical",
        "status": ControlStatus.NON_COMPLIANT,
        "maturity_level": 1,
        "evidence_types": ["data_processing_policy", "privacy_notice", "consent_forms"],
        "related_controls": {"ECC": ["ECC-GV-1"]},
    },
    {
        "control_id": "PDPL-5",
        "framework": FrameworkType.PDPL,
        "domain": "Data Subject Rights",
        "title_en": "Data Subject Rights Management",
        "title_ar": "إدارة حقوق أصحاب البيانات",
        "description_en": "Implement procedures to handle data subject rights requests including access, correction, and deletion.",
        "description_ar": "تنفيذ إجراءات للتعامل مع طلبات حقوق أصحاب البيانات بما في ذلك الوصول والتصحيح والحذف.",
        "priority": "high",
        "status": ControlStatus.NOT_STARTED,
        "maturity_level": 1,
        "evidence_types": ["rights_request_procedure", "request_logs"],
        "related_controls": {},
    },
]


async def load_sample_controls(session: AsyncSession):
    """Load sample controls into database"""
    print("Loading sample controls...")
    
    for control_data in SAMPLE_CONTROLS:
        # Check if control already exists
        existing = await session.get(Control, control_data["control_id"])
        
        if existing:
            print(f"  ⚠️  Control {control_data['control_id']} already exists, skipping")
            continue
        
        # Create new control
        control = Control(**control_data)
        session.add(control)
        print(f"  ✅ Added {control_data['control_id']}: {control_data['title_en']}")
    
    await session.commit()
    print(f"\n✅ Successfully loaded {len(SAMPLE_CONTROLS)} sample controls")


async def main():
    """Main function"""
    print("SICO GRC - Sample Data Loader")
    print("=" * 50)
    
    # Initialize database
    print("\n1. Initializing database...")
    await init_db()
    print("   ✅ Database initialized")
    
    # Load sample data
    print("\n2. Loading sample controls...")
    async with AsyncSessionLocal() as session:
        await load_sample_controls(session)
    
    print("\n" + "=" * 50)
    print("✨ Sample data loading complete!")
    print("\nYou can now:")
    print("  - Visit http://localhost:8000/docs to see the API")
    print("  - Visit http://localhost:3000 to see the frontend")
    print("  - Query controls: GET /api/v1/controls")
    print("  - View dashboard: GET /api/v1/dashboard")


if __name__ == "__main__":
    asyncio.run(main())
