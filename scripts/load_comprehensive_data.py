import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
import uuid

sys.path.append(str(Path(__file__).parent.parent / "src" / "backend"))

from sqlalchemy.ext.asyncio import AsyncSession
from core.database import AsyncSessionLocal
from controls.models import Control, FrameworkType, ControlStatus
from evidence.models import Evidence, EvidenceType, EvidenceStatus

async def load_comprehensive_controls():
    """Load comprehensive control library"""
    
    async with AsyncSessionLocal() as session:
        additional_controls = [
            # More ECC Controls
            {
                "control_id": "ECC-AM-1",
                "framework": FrameworkType.ECC,
                "domain": "Asset Management",
                "title_en": "Asset Inventory Management",
                "title_ar": "إدارة جرد الأصول",
                "description_en": "Maintain comprehensive inventory of all information assets",
                "description_ar": "الحفاظ على جرد شامل لجميع أصول المعلومات",
                "priority": "high",
                "status": ControlStatus.IN_PROGRESS,
                "maturity_level": 3,
            },
            {
                "control_id": "ECC-BC-1",
                "framework": FrameworkType.ECC,
                "domain": "Business Continuity",
                "title_en": "Business Continuity Plan",
                "title_ar": "خطة استمرارية الأعمال",
                "description_en": "Develop and maintain business continuity and disaster recovery plans",
                "description_ar": "تطوير والحفاظ على خطط استمرارية الأعمال والتعافي من الكوارث",
                "priority": "critical",
                "status": ControlStatus.COMPLIANT,
                "maturity_level": 4,
            },
            {
                "control_id": "ECC-IR-1",
                "framework": FrameworkType.ECC,
                "domain": "Incident Response",
                "title_en": "Incident Response Plan",
                "title_ar": "خطة الاستجابة للحوادث",
                "description_en": "Establish incident response procedures and team",
                "description_ar": "إنشاء إجراءات وفريق الاستجابة للحوادث",
                "priority": "critical",
                "status": ControlStatus.IN_PROGRESS,
                "maturity_level": 3,
            },
            {
                "control_id": "ECC-NW-1",
                "framework": FrameworkType.ECC,
                "domain": "Network Security",
                "title_en": "Network Segmentation",
                "title_ar": "تقسيم الشبكة",
                "description_en": "Implement network segmentation and isolation controls",
                "description_ar": "تنفيذ ضوابط تقسيم وعزل الشبكة",
                "priority": "high",
                "status": ControlStatus.COMPLIANT,
                "maturity_level": 4,
            },
            {
                "control_id": "ECC-CR-1",
                "framework": FrameworkType.ECC,
                "domain": "Cryptography",
                "title_en": "Encryption Standards",
                "title_ar": "معايير التشفير",
                "description_en": "Implement encryption for data at rest and in transit",
                "description_ar": "تنفيذ التشفير للبيانات أثناء السكون والنقل",
                "priority": "critical",
                "status": ControlStatus.COMPLIANT,
                "maturity_level": 4,
            },
            
            # More CCC Controls
            {
                "control_id": "CCC-MON-01",
                "framework": FrameworkType.CCC,
                "domain": "Monitoring",
                "title_en": "Cloud Security Monitoring",
                "title_ar": "مراقبة أمن السحابة",
                "description_en": "Implement continuous monitoring and logging for cloud services",
                "description_ar": "تنفيذ المراقبة والتسجيل المستمر لخدمات السحابة",
                "priority": "high",
                "status": ControlStatus.IN_PROGRESS,
                "maturity_level": 3,
            },
            {
                "control_id": "CCC-NET-01",
                "framework": FrameworkType.CCC,
                "domain": "Network Security",
                "title_en": "Cloud Network Security",
                "title_ar": "أمن شبكة السحابة",
                "description_en": "Configure network security groups and firewalls in cloud",
                "description_ar": "تكوين مجموعات أمان الشبكة وجدران الحماية في السحابة",
                "priority": "critical",
                "status": ControlStatus.COMPLIANT,
                "maturity_level": 4,
            },
            {
                "control_id": "CCC-BACK-01",
                "framework": FrameworkType.CCC,
                "domain": "Backup & Recovery",
                "title_en": "Cloud Backup Strategy",
                "title_ar": "استراتيجية النسخ الاحتياطي السحابي",
                "description_en": "Implement automated backup and recovery for cloud resources",
                "description_ar": "تنفيذ النسخ الاحتياطي والاسترداد الآلي لموارد السحابة",
                "priority": "high",
                "status": ControlStatus.IN_PROGRESS,
                "maturity_level": 3,
            },
            
            # More PDPL Controls
            {
                "control_id": "PDPL-25",
                "framework": FrameworkType.PDPL,
                "domain": "Data Transfer",
                "title_en": "Cross-Border Data Transfer",
                "title_ar": "نقل البيانات عبر الحدود",
                "description_en": "Establish controls for international data transfers",
                "description_ar": "إنشاء ضوابط لنقل البيانات الدولية",
                "priority": "critical",
                "status": ControlStatus.NON_COMPLIANT,
                "maturity_level": 1,
            },
            {
                "control_id": "PDPL-30",
                "framework": FrameworkType.PDPL,
                "domain": "Privacy Impact",
                "title_en": "Privacy Impact Assessment",
                "title_ar": "تقييم تأثير الخصوصية",
                "description_en": "Conduct privacy impact assessments for new systems",
                "description_ar": "إجراء تقييمات تأثير الخصوصية للأنظمة الجديدة",
                "priority": "high",
                "status": ControlStatus.NON_COMPLIANT,
                "maturity_level": 1,
            },
            {
                "control_id": "PDPL-35",
                "framework": FrameworkType.PDPL,
                "domain": "Data Minimization",
                "title_en": "Data Minimization Policy",
                "title_ar": "سياسة تقليل البيانات",
                "description_en": "Implement data minimization and purpose limitation",
                "description_ar": "تنفيذ تقليل البيانات وتحديد الغرض",
                "priority": "medium",
                "status": ControlStatus.IN_PROGRESS,
                "maturity_level": 2,
            },
        ]
        
        for control_data in additional_controls:
            control = Control(**control_data)
            session.add(control)
            print(f"✅ Added {control_data['control_id']} - {control_data['title_en']}")
        
        try:
            await session.commit()
            print(f"\n✨ Successfully loaded {len(additional_controls)} additional controls!")
        except Exception as e:
            print(f"❌ Error: {e}")
            await session.rollback()

async def load_comprehensive_evidence():
    """Load comprehensive evidence records"""
    
    async with AsyncSessionLocal() as session:
        additional_evidence = [
            # ECC Evidence
            {
                "evidence_id": f"EVD-{uuid.uuid4().hex[:8].upper()}",
                "control_id": "ECC-AM-1",
                "title_en": "Asset Inventory Report",
                "title_ar": "تقرير جرد الأصول",
                "description_en": "Complete inventory of all IT assets including hardware, software, and data",
                "description_ar": "جرد كامل لجميع أصول تكنولوجيا المعلومات بما في ذلك الأجهزة والبرامج والبيانات",
                "evidence_type": EvidenceType.REPORT,
                "file_path": "/evidence/assets/inventory_2026.xlsx",
                "file_name": "asset_inventory_feb_2026.xlsx",
                "file_size": 1024000,
                "file_format": "XLSX",
                "status": EvidenceStatus.VALIDATED,
                "collection_date": datetime.now() - timedelta(days=7),
                "validated_by": "admin@sico.sa",
                "validated_at": datetime.now() - timedelta(days=5),
            },
            {
                "evidence_id": f"EVD-{uuid.uuid4().hex[:8].upper()}",
                "control_id": "ECC-BC-1",
                "title_en": "Business Continuity Plan Document",
                "title_ar": "وثيقة خطة استمرارية الأعمال",
                "description_en": "Comprehensive BCP including RPO/RTO and recovery procedures",
                "description_ar": "خطة شاملة لاستمرارية الأعمال تتضمن RPO/RTO وإجراءات الاسترداد",
                "evidence_type": EvidenceType.POLICY,
                "file_path": "/evidence/bc/bcp_2026.pdf",
                "file_name": "business_continuity_plan_v3.pdf",
                "file_size": 3072000,
                "file_format": "PDF",
                "status": EvidenceStatus.VALIDATED,
                "collection_date": datetime.now() - timedelta(days=60),
                "validated_by": "admin@sico.sa",
                "validated_at": datetime.now() - timedelta(days=55),
            },
            {
                "evidence_id": f"EVD-{uuid.uuid4().hex[:8].upper()}",
                "control_id": "ECC-IR-1",
                "title_en": "Incident Response Playbook",
                "title_ar": "كتيب الاستجابة للحوادث",
                "description_en": "Step-by-step incident response procedures and escalation matrix",
                "description_ar": "إجراءات الاستجابة للحوادث خطوة بخطوة ومصفوفة التصعيد",
                "evidence_type": EvidenceType.PROCEDURE,
                "file_path": "/evidence/ir/playbook_v2.pdf",
                "file_name": "incident_response_playbook.pdf",
                "file_size": 2048000,
                "file_format": "PDF",
                "status": EvidenceStatus.VALIDATED,
                "collection_date": datetime.now() - timedelta(days=45),
                "validated_by": "security@sico.sa",
                "validated_at": datetime.now() - timedelta(days=40),
            },
            {
                "evidence_id": f"EVD-{uuid.uuid4().hex[:8].upper()}",
                "control_id": "ECC-NW-1",
                "title_en": "Network Architecture Diagram",
                "title_ar": "مخطط البنية التحتية للشبكة",
                "description_en": "Network segmentation diagram showing VLANs and security zones",
                "description_ar": "مخطط تقسيم الشبكة يوضح VLANs ومناطق الأمان",
                "evidence_type": EvidenceType.SCREENSHOT,
                "file_path": "/evidence/network/architecture_diagram.png",
                "file_name": "network_segmentation_diagram.png",
                "file_size": 2560000,
                "file_format": "PNG",
                "status": EvidenceStatus.VALIDATED,
                "collection_date": datetime.now() - timedelta(days=30),
                "validated_by": "network@sico.sa",
                "validated_at": datetime.now() - timedelta(days=28),
            },
            {
                "evidence_id": f"EVD-{uuid.uuid4().hex[:8].upper()}",
                "control_id": "ECC-CR-1",
                "title_en": "Encryption Policy Document",
                "title_ar": "وثيقة سياسة التشفير",
                "description_en": "Encryption standards, key management, and algorithm specifications",
                "description_ar": "معايير التشفير وإدارة المفاتيح ومواصفات الخوارزمية",
                "evidence_type": EvidenceType.POLICY,
                "file_path": "/evidence/crypto/encryption_policy.pdf",
                "file_name": "encryption_standards_policy.pdf",
                "file_size": 1536000,
                "file_format": "PDF",
                "status": EvidenceStatus.VALIDATED,
                "collection_date": datetime.now() - timedelta(days=90),
                "validated_by": "admin@sico.sa",
                "validated_at": datetime.now() - timedelta(days=85),
            },
            
            # CCC Evidence
            {
                "evidence_id": f"EVD-{uuid.uuid4().hex[:8].upper()}",
                "control_id": "CCC-MON-01",
                "title_en": "Cloud Monitoring Dashboard",
                "title_ar": "لوحة معلومات مراقبة السحابة",
                "description_en": "Screenshot of cloud monitoring alerts and metrics",
                "description_ar": "لقطة شاشة لتنبيهات ومقاييس مراقبة السحابة",
                "evidence_type": EvidenceType.SCREENSHOT,
                "file_path": "/evidence/cloud/monitoring_dashboard.png",
                "file_name": "cloud_monitoring_setup.png",
                "file_size": 1024000,
                "file_format": "PNG",
                "status": EvidenceStatus.VALIDATED,
                "collection_date": datetime.now() - timedelta(days=14),
                "validated_by": "cloud@sico.sa",
                "validated_at": datetime.now() - timedelta(days=12),
            },
            {
                "evidence_id": f"EVD-{uuid.uuid4().hex[:8].upper()}",
                "control_id": "CCC-NET-01",
                "title_en": "Cloud Firewall Rules Export",
                "title_ar": "تصدير قواعد جدار حماية السحابة",
                "description_en": "Export of cloud firewall and security group configurations",
                "description_ar": "تصدير تكوينات جدار الحماية ومجموعة الأمان السحابية",
                "evidence_type": EvidenceType.LOG,
                "file_path": "/evidence/cloud/firewall_rules.json",
                "file_name": "cloud_firewall_config.json",
                "file_size": 256000,
                "file_format": "JSON",
                "status": EvidenceStatus.VALIDATED,
                "collection_date": datetime.now() - timedelta(days=10),
                "validated_by": "cloud@sico.sa",
                "validated_at": datetime.now() - timedelta(days=8),
            },
            {
                "evidence_id": f"EVD-{uuid.uuid4().hex[:8].upper()}",
                "control_id": "CCC-BACK-01",
                "title_en": "Backup Verification Report",
                "title_ar": "تقرير التحقق من النسخ الاحتياطي",
                "description_en": "Automated backup verification and restore test results",
                "description_ar": "نتائج التحقق الآلي من النسخ الاحتياطي واختبار الاسترداد",
                "evidence_type": EvidenceType.REPORT,
                "file_path": "/evidence/cloud/backup_verification.pdf",
                "file_name": "backup_test_report_jan2026.pdf",
                "file_size": 512000,
                "file_format": "PDF",
                "status": EvidenceStatus.PENDING,
                "collection_date": datetime.now() - timedelta(days=3),
            },
            
            # PDPL Evidence
            {
                "evidence_id": f"EVD-{uuid.uuid4().hex[:8].upper()}",
                "control_id": "PDPL-25",
                "title_en": "Data Transfer Agreement",
                "title_ar": "اتفاقية نقل البيانات",
                "description_en": "Standard contractual clauses for international data transfers",
                "description_ar": "البنود التعاقدية القياسية لنقل البيانات الدولية",
                "evidence_type": EvidenceType.POLICY,
                "file_path": "/evidence/pdpl/data_transfer_agreement.pdf",
                "file_name": "scc_data_transfer.pdf",
                "file_size": 768000,
                "file_format": "PDF",
                "status": EvidenceStatus.PENDING,
                "collection_date": datetime.now() - timedelta(days=5),
            },
            {
                "evidence_id": f"EVD-{uuid.uuid4().hex[:8].upper()}",
                "control_id": "PDPL-30",
                "title_en": "Privacy Impact Assessment Template",
                "title_ar": "قالب تقييم تأثير الخصوصية",
                "description_en": "PIA template for new system implementations",
                "description_ar": "قالب تقييم تأثير الخصوصية لتطبيقات النظام الجديدة",
                "evidence_type": EvidenceType.PROCEDURE,
                "file_path": "/evidence/pdpl/pia_template.docx",
                "file_name": "privacy_impact_assessment_template.docx",
                "file_size": 384000,
                "file_format": "DOCX",
                "status": EvidenceStatus.PENDING,
                "collection_date": datetime.now() - timedelta(days=2),
            },
            {
                "evidence_id": f"EVD-{uuid.uuid4().hex[:8].upper()}",
                "control_id": "PDPL-35",
                "title_en": "Data Minimization Guidelines",
                "title_ar": "إرشادات تقليل البيانات",
                "description_en": "Internal guidelines for data minimization practices",
                "description_ar": "الإرشادات الداخلية لممارسات تقليل البيانات",
                "evidence_type": EvidenceType.PROCEDURE,
                "file_path": "/evidence/pdpl/minimization_guidelines.pdf",
                "file_name": "data_minimization_guide.pdf",
                "file_size": 640000,
                "file_format": "PDF",
                "status": EvidenceStatus.VALIDATED,
                "collection_date": datetime.now() - timedelta(days=20),
                "validated_by": "privacy@sico.sa",
                "validated_at": datetime.now() - timedelta(days=18),
            },
        ]
        
        for evidence_data in additional_evidence:
            evidence = Evidence(**evidence_data)
            session.add(evidence)
            print(f"✅ Added evidence: {evidence_data['title_en']} (Control: {evidence_data['control_id']})")
        
        try:
            await session.commit()
            print(f"\n✨ Successfully loaded {len(additional_evidence)} evidence records!")
        except Exception as e:
            print(f"❌ Error: {e}")
            await session.rollback()

async def main():
    print("=" * 60)
    print("SICO GRC - Comprehensive Data Loader")
    print("=" * 60)
    
    print("\n📋 Loading additional controls...")
    await load_comprehensive_controls()
    
    print("\n📎 Loading additional evidence...")
    await load_comprehensive_evidence()
    
    print("\n" + "=" * 60)
    print("✨ Comprehensive data loading complete!")
    print("\nDatabase now contains:")
    print("  • 25+ controls across ECC, CCC, PDPL")
    print("  • 19+ evidence records")
    print("  • Multiple domains and priorities")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
