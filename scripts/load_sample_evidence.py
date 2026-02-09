import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src/backend to path
sys.path.append(str(Path(__file__).parent.parent / "src" / "backend"))

from sqlalchemy.ext.asyncio import AsyncSession
from core.database import AsyncSessionLocal
from evidence.models import Evidence, EvidenceType, EvidenceStatus
import uuid

async def load_sample_evidence():
    """Load sample evidence records for demonstration"""
    
    async with AsyncSessionLocal() as session:
        sample_evidence = [
            {
                "evidence_id": f"EVD-{uuid.uuid4().hex[:8].upper()}",
                "control_id": "ECC-GV-1",
                "title_en": "Governance Framework Document",
                "title_ar": "وثيقة إطار الحوكمة",
                "description_en": "Official governance framework policy document approved by board",
                "description_ar": "وثيقة سياسة إطار الحوكمة الرسمية المعتمدة من قبل المجلس",
                "evidence_type": EvidenceType.POLICY,
                "file_path": "/evidence/governance/framework_v1.pdf",
                "file_name": "governance_framework_v1.pdf",
                "file_size": 2048000,
                "file_format": "PDF",
                "status": EvidenceStatus.VALIDATED,
                "collection_date": datetime.now() - timedelta(days=30),
                "validated_by": "admin@sico.sa",
                "validated_at": datetime.now() - timedelta(days=25),
            },
            {
                "evidence_id": f"EVD-{uuid.uuid4().hex[:8].upper()}",
                "control_id": "ECC-IS-1",
                "title_en": "Information Security Policy v2.0",
                "title_ar": "سياسة أمن المعلومات الإصدار 2.0",
                "description_en": "Updated information security policy document",
                "description_ar": "وثيقة سياسة أمن المعلومات المحدثة",
                "evidence_type": EvidenceType.POLICY,
                "file_path": "/evidence/security/is_policy_v2.pdf",
                "file_name": "is_policy_v2.pdf",
                "file_size": 1536000,
                "file_format": "PDF",
                "status": EvidenceStatus.VALIDATED,
                "collection_date": datetime.now() - timedelta(days=20),
                "validated_by": "admin@sico.sa",
                "validated_at": datetime.now() - timedelta(days=18),
            },
            {
                "evidence_id": f"EVD-{uuid.uuid4().hex[:8].upper()}",
                "control_id": "CCC-GOV-01",
                "title_en": "Cloud Governance Charter",
                "title_ar": "ميثاق حوكمة السحابة",
                "description_en": "Cloud governance framework and responsibilities",
                "description_ar": "إطار حوكمة السحابة والمسؤوليات",
                "evidence_type": EvidenceType.POLICY,
                "file_path": "/evidence/cloud/governance_charter.pdf",
                "file_name": "cloud_governance_charter.pdf",
                "file_size": 1024000,
                "file_format": "PDF",
                "status": EvidenceStatus.VALIDATED,
                "collection_date": datetime.now() - timedelta(days=15),
                "validated_by": "admin@sico.sa",
                "validated_at": datetime.now() - timedelta(days=10),
            },
            {
                "evidence_id": f"EVD-{uuid.uuid4().hex[:8].upper()}",
                "control_id": "CCC-SEC-01",
                "title_en": "Cloud Security Configuration",
                "title_ar": "تكوين أمان السحابة",
                "description_en": "Screenshot of cloud security settings and configurations",
                "description_ar": "لقطة شاشة لإعدادات وتكوينات أمان السحابة",
                "evidence_type": EvidenceType.SCREENSHOT,
                "file_path": "/evidence/cloud/security_config.png",
                "file_name": "cloud_security_config.png",
                "file_size": 512000,
                "file_format": "PNG",
                "status": EvidenceStatus.VALIDATED,
                "collection_date": datetime.now() - timedelta(days=5),
                "validated_by": "admin@sico.sa",
                "validated_at": datetime.now() - timedelta(days=3),
            },
            {
                "evidence_id": f"EVD-{uuid.uuid4().hex[:8].upper()}",
                "control_id": "PDPL-1",
                "title_en": "Data Processing Register",
                "title_ar": "سجل معالجة البيانات",
                "description_en": "Register of all personal data processing activities",
                "description_ar": "سجل جميع أنشطة معالجة البيانات الشخصية",
                "evidence_type": EvidenceType.REPORT,
                "file_path": "/evidence/pdpl/processing_register.xlsx",
                "file_name": "data_processing_register.xlsx",
                "file_size": 256000,
                "file_format": "XLSX",
                "status": EvidenceStatus.PENDING,
                "collection_date": datetime.now() - timedelta(days=2),
            },
            {
                "evidence_id": f"EVD-{uuid.uuid4().hex[:8].upper()}",
                "control_id": "PDPL-5",
                "title_en": "Data Subject Rights Procedure",
                "title_ar": "إجراء حقوق صاحب البيانات",
                "description_en": "Draft procedure for handling data subject requests",
                "description_ar": "مسودة إجراء معالجة طلبات أصحاب البيانات",
                "evidence_type": EvidenceType.PROCEDURE,
                "file_path": "/evidence/pdpl/dsr_procedure_draft.pdf",
                "file_name": "dsr_procedure_draft.pdf",
                "file_size": 768000,
                "file_format": "PDF",
                "status": EvidenceStatus.PENDING,
                "collection_date": datetime.now() - timedelta(days=1),
            },
            {
                "evidence_id": f"EVD-{uuid.uuid4().hex[:8].upper()}",
                "control_id": "ECC-AC-1",
                "title_en": "Access Control Matrix",
                "title_ar": "مصفوفة التحكم في الوصول",
                "description_en": "Current access control matrix and role assignments",
                "description_ar": "مصفوفة التحكم في الوصول الحالية وتعيينات الأدوار",
                "evidence_type": EvidenceType.REPORT,
                "file_path": "/evidence/access/control_matrix.xlsx",
                "file_name": "access_control_matrix.xlsx",
                "file_size": 358000,
                "file_format": "XLSX",
                "status": EvidenceStatus.VALIDATED,
                "collection_date": datetime.now() - timedelta(days=10),
                "validated_by": "admin@sico.sa",
                "validated_at": datetime.now() - timedelta(days=8),
            },
            {
                "evidence_id": f"EVD-{uuid.uuid4().hex[:8].upper()}",
                "control_id": "CCC-IAM-01",
                "title_en": "Cloud IAM Configuration",
                "title_ar": "تكوين إدارة الهوية والوصول السحابية",
                "description_en": "Cloud identity and access management configuration export",
                "description_ar": "تصدير تكوين إدارة الهوية والوصول السحابية",
                "evidence_type": EvidenceType.LOG,
                "file_path": "/evidence/cloud/iam_config.json",
                "file_name": "cloud_iam_config.json",
                "file_size": 128000,
                "file_format": "JSON",
                "status": EvidenceStatus.VALIDATED,
                "collection_date": datetime.now() - timedelta(days=7),
                "validated_by": "admin@sico.sa",
                "validated_at": datetime.now() - timedelta(days=5),
            },
        ]
        
        for evidence_data in sample_evidence:
            evidence = Evidence(**evidence_data)
            session.add(evidence)
            print(f"✅ Added evidence: {evidence_data['title_en']} (Control: {evidence_data['control_id']})")
        
        try:
            await session.commit()
            print(f"\n✨ Successfully loaded {len(sample_evidence)} evidence records!")
        except Exception as e:
            print(f"❌ Error loading evidence: {e}")
            await session.rollback()

if __name__ == "__main__":
    asyncio.run(load_sample_evidence())
