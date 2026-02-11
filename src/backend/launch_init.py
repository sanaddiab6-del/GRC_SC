"""
SICO GRC Platform - Enterprise Launch Initialization
Initializes complete platform with all data, users, and configurations
For production-ready deployment
"""

import asyncio
import uuid
from datetime import datetime, timedelta, date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from core.config import settings
from core.database import Base, AsyncSessionLocal
from auth.models import User, Role, Permission
from auth.security import get_password_hash
from enterprise_models import (
    Organization, Asset, Control, Risk, Evidence, Policy,
    ControlAssessment, AuditProgram, AuditFinding, Vendor,
    RecordOfProcessingActivity, DataSubjectRequest, DataBreach,
    ControlException, WorkflowCase, Integration, ComplianceMetric,
    EvidenceTemplate, FrameworkType, ControlStatus, ControlMaturity,
    RiskLevel, TestResult, AssetCriticality, DataClassification,
    FindingSeverity, CaseStatus
)


async def initialize_platform():
    """Complete platform initialization for launch"""
    print("\n" + "="*80)
    print("🚀 SICO GRC PLATFORM - ENTERPRISE LAUNCH INITIALIZATION")
    print("="*80)
    
    # Phase 1: Database tables
    print("\n📊 Phase 1: Creating database schema...")
    try:
        async with AsyncSessionLocal() as db:
            pass  # Just test connection
        
        # Create all tables
        from core.database import engine
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("   ✓ Database schema created")
    except Exception as e:
        print(f"   ✗ Database schema creation failed: {str(e)}")
        raise
    
    # Phase 2: Initialize RBAC
    print("\n🔐 Phase 2: Initializing RBAC system...")
    async with AsyncSessionLocal() as db:
        # Create default roles
        roles_data = [
            ("Admin", "Full system access", "完全なシステムアクセス"),
            ("Compliance Officer", "Compliance and audit management", "コンプライアンスおよび監査管理"),
            ("Control Owner", "Own and manage assigned controls", "割り当てられたコントロールを管理"),
            ("Risk Owner", "Own and manage assigned risks", "割り当てられたリスクを管理"),
            ("Auditor", "Conduct audits and testing", "監査とテストの実施"),
            ("SOC Analyst", "Manage incidents and SOC operations", "インシデント管理とSOC運用"),
            ("Executive", "View-only executive access", "ビューのみのエグゼクティブアクセス"),
            ("Regulator", "External regulatory access (read-only)", "外部規制アクセス（読み取り専用）"),
        ]
        
        for role_name, desc_en, desc_ar in roles_data:
            existing = await db.execute(select(Role).where(Role.role_name == role_name))
            if not existing.scalar_one_or_none():
                new_role = Role(
                    role_name=role_name,
                    description_en=desc_en,
                    description_ar=desc_ar
                )
                db.add(new_role)
        
        await db.commit()
        print(f"   ✓ Created {len(roles_data)} roles")
    
    # Phase 3: Create master organization
    print("\n🏢 Phase 3: Setting up organization...")
    async with AsyncSessionLocal() as db:
        existing_org = await db.execute(select(Organization))
        if not existing_org.scalar_one_or_none():
            master_org = Organization(
                name_en="SICO Master Organization",
                name_ar="منظمة SICO الرئيسية",
                org_type="group",
                license_type="enterprise",
                is_active=True
            )
            db.add(master_org)
            await db.commit()
            print("   ✓ Master organization created")
            org_id = master_org.id
        else:
            orgs = await db.execute(select(Organization).limit(1))
            org_id = orgs.scalar_one().id
    
    # Phase 4: Create admin user
    print("\n👤 Phase 4: Creating admin user...")
    async with AsyncSessionLocal() as db:
        existing_admin = await db.execute(select(User).filter(User.username == "admin"))
        if not existing_admin.scalar_one_or_none():
            admin_role = await db.execute(select(Role).where(Role.role_name == "Admin"))
            admin = User(
                organization_id=org_id,
                username="admin",
                email="admin@sico-grc.local",
                password_hash=get_password_hash("AdminPassword123!"),
                full_name_en="System Administrator",
                full_name_ar="مسؤول النظام",
                role="admin",
                is_active=True,
                is_verified=True
            )
            db.add(admin)
            await db.commit()
            print("   ✓ Admin user created (username: admin, password: AdminPassword123!)")
        else:
            print("   ℹ Admin user already exists")
    
    # Phase 5: Create assets
    print("\n📦 Phase 5: Initializing asset registry...")
    async with AsyncSessionLocal() as db:
        assets_data = [
            ("APP-001", "application", "Core GRC Platform", "منصة GRC الأساسية", AssetCriticality.CRITICAL),
            ("DB-001", "database", "PostgreSQL Database", "قاعدة بيانات PostgreSQL", AssetCriticality.CRITICAL),
            ("CLOUD-001", "cloud_service", "Azure Cloud", "سحابة Azure", AssetCriticality.HIGH),
            ("NET-001", "network_device", "Firewall", "جدار الحماية", AssetCriticality.CRITICAL),
        ]
        
        for asset_id, asset_type, name_en, name_ar, criticality in assets_data:
            existing = await db.execute(select(Asset).where(Asset.asset_id == asset_id))
            if not existing.scalar_one_or_none():
                asset = Asset(
                    organization_id=org_id,
                    asset_id=asset_id,
                    asset_type=asset_type,
                    name_en=name_en,
                    name_ar=name_ar,
                    criticality=criticality,
                    classification=DataClassification.CONFIDENTIAL,
                    environment="production",
                    is_active=True
                )
                db.add(asset)
        
        await db.commit()
        print(f"   ✓ Created {len(assets_data)} critical assets")
    
    # Phase 6: Load control frameworks
    print("\n📋 Phase 6: Loading regulatory control frameworks...")
    async with AsyncSessionLocal() as db:
        # ECC samples
        ecc_controls = [
            ("ECC-IS-1", "Authentication and Authorization", "نظام المصادقة والتفويض", 
             "Implement strong authentication mechanisms", "تطبيق آليات مصادقة قوية"),
            ("ECC-IS-3", "Cryptographic Controls", "ضوابط التشفير",
             "Use encryption for sensitive data", "استخدام التشفير للبيانات الحساسة"),
            ("ECC-IS-5", "Incident Response", "الاستجابة للحوادث",
             "Establish incident response procedures", "إنشاء إجراءات الاستجابة للحوادث"),
            ("ECC-RM-1", "Risk Management Framework", "إطار إدارة المخاطر",
             "Maintain risk register and assessments", "الحفاظ على سجل المخاطر والتقييمات"),
        ]
        
        for control_id, title_en, title_ar, desc_en, desc_ar in ecc_controls:
            existing = await db.execute(select(Control).where(Control.control_id == control_id))
            if not existing.scalar_one_or_none():
                control = Control(
                    organization_id=org_id,
                    control_id=control_id,
                    framework=FrameworkType.ECC,
                    domain="Information Security",
                    domain_ar="أمن المعلومات",
                    title_en=title_en,
                    title_ar=title_ar,
                    description_en=desc_en,
                    description_ar=desc_ar,
                    status=ControlStatus.ACTIVE,
                    maturity_level=ControlMaturity.MANAGED,
                    is_applicable=True,
                    test_frequency_days=90
                )
                db.add(control)
        
        await db.commit()
        print(f"   ✓ Loaded ECC control framework (4 core controls)")
    
    # Phase 7: Create sample risks
    print("\n⚠️ Phase 7: Establishing risk register...")
    async with AsyncSessionLocal() as db:
        # Get admin user ID
        admin_user = await db.execute(select(User).filter(User.username == "admin"))
        admin_id = admin_user.scalar_one().user_id if hasattr(admin_user.scalar_one(), 'user_id') else admin_user.scalar_one().id
        
        risks_data = [
            ("RISK-2024-001", "Data Breach", "تسرب البيانات",
             "Unauthorized access to customer data", RiskLevel.CRITICAL),
            ("RISK-2024-002", "System Outage", "توقف النظام",
             "Extended platform unavailability", RiskLevel.HIGH),
            ("RISK-2024-003", "Compliance Violation", "انتهاك الامتثال",
             "Failure to meet regulatory requirements", RiskLevel.HIGH),
        ]
        
        for risk_id, title_en, title_ar, desc_en, risk_level in risks_data:
            existing = await db.execute(select(Risk).where(Risk.risk_id == risk_id))
            if not existing.scalar_one_or_none():
                risk = Risk(
                    organization_id=org_id,
                    risk_id=risk_id,
                    risk_type="cyber",
                    title_en=title_en,
                    title_ar=title_ar,
                    description_en=desc_en,
                    description_ar="",
                    likelihood_inherent=3,
                    impact_inherent=4,
                    risk_score_inherent=12.0,
                    risk_level_inherent=risk_level,
                    risk_appetite_level=RiskLevel.HIGH,
                    status="open"
                )
                db.add(risk)
        
        await db.commit()
        print(f"   ✓ Created {len(risks_data)} risks in register")
    
    # Phase 8: Initialize PDPL records
    print("\n📜 Phase 8: Setting up PDPL compliance...")
    async with AsyncSessionLocal() as db:
        ropa = RecordOfProcessingActivity(
            organization_id=org_id,
            ropa_id="ROPA-2024-001",
            activity_name_en="Customer Data Processing",
            activity_name_ar="معالجة بيانات العملاء",
            purpose_en="Business operations and service delivery",
            purpose_ar="العمليات التجارية وتقديم الخدمات",
            legal_basis="legitimate_interest",
            data_categories=["customer", "contact", "transaction"],
            data_subjects=["customers", "partners"],
            retention_period="3 years",
            security_measures="Encryption, access control, audit logging",
            dpia_required=False
        )
        db.add(ropa)
        await db.commit()
        print("   ✓ Created Record of Processing Activity (RoPA)")
    
    # Phase 9: Initialize audit program
    print("\n📑 Phase 9: Setting up audit programs...")
    async with AsyncSessionLocal() as db:
        audit_program = AuditProgram(
            organization_id=org_id,
            program_id="AUDIT-2024-01",
            title_en="Annual ECC Compliance Audit",
            title_ar="مراجعة امتثال ECC السنوية",
            audit_type="internal",
            framework=FrameworkType.ECC,
            scope_description="Full scope audit of ECC controls",
            planned_start_date=date.today(),
            planned_end_date=date.today() + timedelta(days=30),
            status="planned"
        )
        db.add(audit_program)
        await db.commit()
        print("   ✓ Created annual audit program")
    
    # Phase 10: Initialize metrics baseline
    print("\n📊 Phase 10: Establishing compliance metrics...")
    async with AsyncSessionLocal() as db:
        metric = ComplianceMetric(
            organization_id=org_id,
            metric_date=date.today(),
            framework=FrameworkType.ECC,
            total_controls=4,
            compliant_controls=3,
            partial_controls=1,
            non_compliant_controls=0,
            compliance_percentage=75.0,
            total_risks=3,
            critical_risks=1,
            high_risks=2,
            risks_within_appetite=2,
            open_findings=0,
            overdue_findings=0
        )
        db.add(metric)
        await db.commit()
        print("   ✓ Baseline compliance metrics established")
    
    print("\n" + "="*80)
    print("✅ SICO GRC PLATFORM - LAUNCH INITIALIZATION COMPLETE")
    print("="*80)
    print("\n📋 Platform Status:")
    print("   ✓ Database schema: Created")
    print("   ✓ RBAC system: Initialized (8 roles)")
    print("   ✓ Organization hierarchy: Configured")
    print("   ✓ Admin user: Ready (admin / AdminPassword123!)")
    print("   ✓ Asset registry: Populated (4 critical assets)")
    print("   ✓ Control frameworks: Loaded (ECC baseline)")
    print("   ✓ Risk register: Initialized (3 material risks)")
    print("   ✓ PDPL compliance: Records created")
    print("   ✓ Audit program: Scheduled")
    print("   ✓ Compliance metrics: Baseline established")
    
    print("\n🚀 Ready for production deployment!")
    print("\nAccess points:")
    print("   API: http://localhost:8000/api/v1")
    print("   Frontend: http://localhost:3000")
    print("   API Docs: http://localhost:8000/docs")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(initialize_platform())
