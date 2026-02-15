import asyncio
import sys
from pathlib import Path

# Add src/backend to path
sys.path.append(str(Path(__file__).parent.parent / "src" / "backend"))

from sqlalchemy.ext.asyncio import AsyncSession
from core.database import AsyncSessionLocal
from controls.models import Control, FrameworkType, ControlStatus

async def load_more_controls():
    """Load additional sample controls for demonstration"""
    
    async with AsyncSessionLocal() as session:
        # Additional ECC controls
        ecc_controls = [
            {
                "control_id": "ECC-GV-2",
                "framework": FrameworkType.ECC,
                "title_en": "Risk Management Framework",
                "title_ar": "إطار إدارة المخاطر",
                "description_en": "Establish and maintain a comprehensive risk management framework",
                "description_ar": "إنشاء والحفاظ على إطار شامل لإدارة المخاطر",
                "domain": "Governance",
                "status": ControlStatus.IN_PROGRESS,
                "priority": "high",
                "maturity_level": 3,
            },
            {
                "control_id": "ECC-AC-1",
                "framework": FrameworkType.ECC,
                "title_en": "Access Control Policy",
                "title_ar": "سياسة التحكم في الوصول",
                "description_en": "Implement access control policy and procedures",
                "description_ar": "تنفيذ سياسة وإجراءات التحكم في الوصول",
                "domain": "Access Control",
                "status": ControlStatus.COMPLIANT,
                "priority": "critical",
                "maturity_level": 4,
            },
            {
                "control_id": "ECC-RM-1",
                "framework": FrameworkType.ECC,
                "title_en": "Risk Assessment",
                "title_ar": "تقييم المخاطر",
                "description_en": "Conduct regular risk assessments",
                "description_ar": "إجراء تقييمات منتظمة للمخاطر",
                "domain": "Risk Management",
                "status": ControlStatus.IN_PROGRESS,
                "priority": "high",
                "maturity_level": 3,
            },
        ]
        
        # Additional CCC controls
        ccc_controls = [
            {
                "control_id": "CCC-IAM-01",
                "framework": FrameworkType.CCC,
                "title_en": "Cloud Identity Management",
                "title_ar": "إدارة الهوية السحابية",
                "description_en": "Implement cloud identity and access management",
                "description_ar": "تنفيذ إدارة الهوية والوصول السحابية",
                "domain": "Identity & Access",
                "status": ControlStatus.COMPLIANT,
                "priority": "critical",
                "maturity_level": 4,
            },
            {
                "control_id": "CCC-DATA-01",
                "framework": FrameworkType.CCC,
                "title_en": "Cloud Data Encryption",
                "title_ar": "تشفير البيانات السحابية",
                "description_en": "Encrypt data at rest and in transit in cloud",
                "description_ar": "تشفير البيانات أثناء التخزين والنقل في السحابة",
                "domain": "Data Security",
                "status": ControlStatus.IN_PROGRESS,
                "priority": "critical",
                "maturity_level": 3,
            },
        ]
        
        # Additional PDPL controls
        pdpl_controls = [
            {
                "control_id": "PDPL-10",
                "framework": FrameworkType.PDPL,
                "title_en": "Data Retention Policy",
                "title_ar": "سياسة الاحتفاظ بالبيانات",
                "description_en": "Establish data retention and disposal policy",
                "description_ar": "إنشاء سياسة الاحتفاظ بالبيانات والتخلص منها",
                "domain": "Data Management",
                "status": ControlStatus.NON_COMPLIANT,
                "priority": "high",
                "maturity_level": 2,
            },
            {
                "control_id": "PDPL-15",
                "framework": FrameworkType.PDPL,
                "title_en": "Consent Management",
                "title_ar": "إدارة الموافقات",
                "description_en": "Implement consent collection and management system",
                "description_ar": "تنفيذ نظام جمع وإدارة الموافقات",
                "domain": "Consent & Rights",
                "status": ControlStatus.NON_COMPLIANT,
                "priority": "critical",
                "maturity_level": 1,
            },
            {
                "control_id": "PDPL-20",
                "framework": FrameworkType.PDPL,
                "title_en": "Data Breach Response",
                "title_ar": "الاستجابة لخرق البيانات",
                "description_en": "Establish data breach notification procedures",
                "description_ar": "إنشاء إجراءات الإخطار بخرق البيانات",
                "domain": "Incident Response",
                "status": ControlStatus.IN_PROGRESS,
                "priority": "critical",
                "maturity_level": 2,
            },
        ]
        
        all_controls = ecc_controls + ccc_controls + pdpl_controls
        
        for control_data in all_controls:
            control = Control(**control_data)
            session.add(control)
            print(f"✅ Added {control_data['control_id']} - {control_data['title_en']}")
        
        try:
            await session.commit()
            print(f"\n✨ Successfully loaded {len(all_controls)} additional controls!")
        except Exception as e:
            print(f"❌ Error loading controls: {e}")
            await session.rollback()

if __name__ == "__main__":
    asyncio.run(load_more_controls())
