#!/usr/bin/env python3
"""
Enterprise GRC Demo Data Loader
Loads comprehensive, professional-grade demo data for SICO platform
Includes: Risk Management, Compliance, Audits, Vendors, PDPL, Incidents

Author: SICO Team
Compliance: NCA ECC/CCC, PDPL, ISO 27001
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional
import random

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "backend"))

from sqlalchemy.ext.asyncio import AsyncSession
from core.database import AsyncSessionLocal, init_db
from auth.security import get_password_hash
from auth.models import User
from enterprise_models import (
    Organization, Asset, Risk, Control, AuditProgram, AuditFinding,
    Evidence, Policy, Vendor, WorkflowCase,
    RecordOfProcessingActivity, DataSubjectRequest, DataBreach, ControlAssessment,
    AssetCriticality, DataClassification, RiskLevel, TestResult, FindingSeverity, CaseStatus,
    FrameworkType, ControlStatus
)


class EnterpriseDataLoader:
    """Professional enterprise demo data loader"""
    
    def __init__(self):
        self.session: Optional[AsyncSession] = None
        self.org: Optional[Organization] = None
        self.users = {}
        self.assets = {}
        self.controls = {}
        self.risks = {}

    def _require_org(self) -> Organization:
        if not self.org:
            raise RuntimeError("Organization is not initialized")
        return self.org
        
    async def load_all(self):
        """Load complete enterprise demo dataset"""
        print("=" * 80)
        print("🏢 SICO Enterprise GRC Platform - Professional Demo Data Loader")
        print("=" * 80)
        
        async with AsyncSessionLocal() as session:
            self.session = session
            
            try:
                # Core entities
                await self.create_organization()
                await self.create_users()
                
                # Asset Management
                await self.create_assets()
                
                # Control Framework
                await self.create_controls()
                await self.create_control_tests()
                
                # Risk Management
                await self.create_risks()
                await self.create_risk_treatments()
                
                # Compliance & Audit
                await self.create_audit_programs()
                await self.create_audit_findings()
                await self.create_evidence()
                
                # Vendor Management
                await self.create_vendors()
                
                # Policy Management
                await self.create_policies()
                
                # PDPL Compliance
                await self.create_pdpl_records()
                await self.create_dsar()
                await self.create_data_breaches()
                
                # Incident Management
                await self.create_incidents()
                
                await session.commit()
                
                print("\n" + "=" * 80)
                print("✅ Enterprise demo data loaded successfully!")
                print("=" * 80)
                await self.print_summary()
                
            except Exception as e:
                await session.rollback()
                print(f"\n❌ Error: {e}")
                import traceback
                traceback.print_exc()
                raise
    
    async def create_organization(self):
        """Create Saudi organization"""
        print("\n📊 Creating Organization...")
        assert self.session is not None
        
        self.org = Organization(
            name_en="Saudi National Bank",
            name_ar="البنك الأهلي السعودي",
            industry_en="Banking & Financial Services",
            industry_ar="الخدمات المصرفية والمالية",
            country="Saudi Arabia",
            city="Riyadh",
            employee_count=5000,
            revenue=Decimal("2500000000"),  # 2.5 billion SAR
            compliance_frameworks=["NCA_ECC", "NCA_CCC", "PDPL", "ISO_27001", "PCI_DSS"],
            data_classification_levels=["Public", "Internal", "Confidential", "Restricted"],
            is_active=True
        )
        self.session.add(self.org)
        await self.session.flush()
        print(f"   ✓ Organization: {self.org.name_en} (ID: {self.org.id})")
    
    async def create_users(self):
        """Create user accounts with different roles"""
        print("\n👥 Creating Users...")
        assert self.session is not None
        
        users_data = [
            ("admin@snb.sa", "Admin User", "مدير النظام"),
            ("ciso@snb.sa", "Mohammed Al-Rashid", "محمد الراشد"),
            ("compliance@snb.sa", "Fatima Al-Qasim", "فاطمة القاسم"),
            ("auditor@snb.sa", "Ahmed Al-Mutairi", "أحمد المطيري"),
            ("risk@snb.sa", "Sara Al-Fahad", "سارة الفهد"),
            ("analyst@snb.sa", "Khalid Al-Shahrani", "خالد الشهراني"),
        ]
        
        for email, name_en, name_ar in users_data:
            user = User(
                email=email,
                password_hash=get_password_hash("Password123!"),
                full_name_en=name_en,
                full_name_ar=name_ar,
                is_active=True,
                is_verified=True,
                failed_login_attempts=0
            )
            self.session.add(user)
            # Store by email key since auth User doesn't have username
            self.users[email.split('@')[0]] = user
            print(f"   ✓ User: {name_en} ({email})")
        
        await self.session.flush()
    
    async def create_assets(self):
        """Create comprehensive asset inventory"""
        print("\n💾 Creating Asset Inventory...")
        assert self.session is not None
        org = self._require_org()
        
        assets_data = [
            # Critical Infrastructure
            ("CORE-BANKING-01", "Core Banking System", "نظام الخدمات المصرفية الأساسي",
             "application", "critical", "AWS RDS", "172.16.10.50", self.users["ciso"].id, "operational"),
            
            ("PAYMENT-GW-01", "Payment Gateway", "بوابة الدفع",
             "application", "critical", "Azure Cloud", "10.20.30.40", self.users["ciso"].id, "operational"),
            
            ("DB-PROD-01", "Production Database Cluster", "قاعدة بيانات الإنتاج",
             "database", "critical", "On-Premise DC1", "192.168.1.100", self.users["ciso"].id, "operational"),
            
            # Infrastructure
            ("FW-EDGE-01", "Edge Firewall", "جدار الحماية الخارجي",
             "network", "high", "DMZ", "203.0.113.1", self.users["ciso"].id, "operational"),
            
            ("AD-DOMAIN-01", "Active Directory Domain Controller", "خادم الأدوار",
             "server", "high", "On-Premise DC1", "192.168.1.10", self.users["ciso"].id, "operational"),
            
            # Applications
            ("CRM-SYSTEM", "Customer Relationship Management", "إدارة علاقات العملاء",
             "application", "medium", "Azure Cloud", "10.50.60.70", self.users["analyst"].id, "operational"),
            
            ("HR-PORTAL", "HR Self-Service Portal", "بوابة الموارد البشرية",
             "application", "medium", "On-Premise", "192.168.2.50", self.users["analyst"].id, "operational"),
            
            # Data Assets
            ("CUSTOMER-DB", "Customer PII Database", "قاعدة بيانات العملاء",
             "data", "critical", "Encrypted Storage", "192.168.1.101", self.users["ciso"].id, "operational"),
            
            ("TRANSACTION-LOGS", "Transaction Audit Logs", "سجلات المعاملات",
             "data", "high", "S3 Bucket", "s3://snb-audit-logs", self.users["auditor"].id, "operational"),
        ]
        
        for asset_id, name_en, name_ar, asset_type, criticality, location, ip, owner_id, status in assets_data:
            asset = Asset(
                organization_id=org.id,
                asset_id=asset_id,
                name_en=name_en,
                name_ar=name_ar,
                asset_type=asset_type,
                criticality=AssetCriticality(criticality),
                location=location,
                owner_id=owner_id,
                classification=DataClassification.CONFIDENTIAL if criticality == "critical" else DataClassification.INTERNAL,
                environment="production",
                asset_metadata={
                    "ip_address": ip,
                    "status": status,
                    "last_assessment_date": (datetime.utcnow() - timedelta(days=random.randint(10, 90))).isoformat()
                }
            )
            self.session.add(asset)
            self.assets[asset_id] = asset
            print(f"   ✓ Asset: {name_en} [{criticality}]")
        
        await self.session.flush()
    
    async def create_controls(self):
        """Create NCA ECC/CCC control library"""
        print("\n🛡️ Creating Control Framework...")
        assert self.session is not None
        org = self._require_org()
        
        controls_data = [
            # NCA ECC Controls
            ("ECC-GV-1", "Information Security Governance Framework", "إطار حوكمة أمن المعلومات",
             "NCA_ECC", "Governance", "Board-level IS governance", "implemented", 85),
            
            ("ECC-GV-2", "Information Security Strategy", "استراتيجية أمن المعلومات",
             "NCA_ECC", "Governance", "Documented IS strategy aligned with business", "implemented", 90),
            
            ("ECC-RM-1", "Risk Management Framework", "إطار إدارة المخاطر",
             "NCA_ECC", "Risk Management", "Enterprise risk management program", "implemented", 88),
            
            ("ECC-RM-2", "Risk Assessment Methodology", "منهجية تقييم المخاطر",
             "NCA_ECC", "Risk Management", "Systematic risk identification and assessment", "implemented", 92),
            
            ("ECC-IS-1", "Access Control Policy", "سياسة التحكم في الوصول",
             "NCA_ECC", "Information Security", "Least privilege and need-to-know access", "implemented", 87),
            
            ("ECC-IS-2", "Multi-Factor Authentication", "المصادقة متعددة العوامل",
             "NCA_ECC", "Information Security", "MFA for all privileged accounts", "implemented", 95),
            
            ("ECC-IS-3", "Encryption Standards", "معايير التشفير",
             "NCA_ECC", "Information Security", "TLS 1.2+, AES-256 for data at rest", "implemented", 100),
            
            ("ECC-IS-4", "Security Monitoring", "مراقبة الأمن",
             "NCA_ECC", "Information Security", "24/7 SOC with SIEM integration", "implemented", 90),
            
            ("ECC-IS-5", "Incident Response Plan", "خطة الاستجابة للحوادث",
             "NCA_ECC", "Information Security", "Documented IRP with annual testing", "implemented", 85),
            
            # NCA CCC Controls
            ("CCC-CR-1", "Cryptographic Key Management", "إدارة المفاتيح التشفيرية",
             "NCA_CCC", "Cryptography", "HSM-based key management", "implemented", 88),
            
            ("CCC-CR-2", "Encryption at Rest", "التشفير أثناء التخزين",
             "NCA_CCC", "Cryptography", "All sensitive data encrypted", "implemented", 92),
            
            # PDPL Controls
            ("PDPL-1", "Data Protection Impact Assessment", "تقييم أثر حماية البيانات",
             "PDPL", "Privacy", "DPIA for high-risk processing", "implemented", 85),
            
            ("PDPL-2", "Consent Management", "إدارة الموافقات",
             "PDPL", "Privacy", "Granular consent with withdrawal mechanism", "implemented", 90),
            
            ("PDPL-3", "Data Subject Rights", "حقوق صاحب البيانات",
             "PDPL", "Privacy", "DSAR process within 30 days", "implemented", 88),
            
            ("PDPL-4", "Breach Notification", "إخطار الانتهاكات",
             "PDPL", "Privacy", "72-hour breach notification to SDAIA", "implemented", 95),
            
            # ISO 27001 Controls
            ("ISO-5.1", "Information Security Policy", "سياسة أمن المعلومات",
             "ISO_27001", "Policy", "Board-approved IS policy reviewed annually", "implemented", 90),
            
            ("ISO-8.1", "Asset Management", "إدارة الأصول",
             "ISO_27001", "Assets", "Complete asset inventory with classification", "implemented", 85),
            
            ("ISO-12.1", "Operational Security", "الأمن التشغيلي",
             "ISO_27001", "Operations", "Documented operational procedures", "implemented", 87),
        ]
        
        for ctrl_id, name_en, name_ar, framework, domain, desc, status, effectiveness in controls_data:
            framework_enum = {
                "NCA_ECC": FrameworkType.ECC,
                "NCA_CCC": FrameworkType.CCC,
                "PDPL": FrameworkType.PDPL,
                "ISO_27001": FrameworkType.ISO_27001,
            }.get(framework, FrameworkType.CUSTOM)

            control = Control(
                organization_id=org.id,
                control_id=ctrl_id,
                title_en=name_en,
                title_ar=name_ar,
                framework=framework_enum,
                domain=domain,
                description_en=desc,
                description_ar=desc,
                status=ControlStatus.ACTIVE,
                effectiveness_score=effectiveness,
                control_owner_id=self.users["ciso"].id,
                last_assessment_date=(datetime.utcnow() - timedelta(days=random.randint(30, 180))).date(),
                next_assessment_date=(datetime.utcnow() + timedelta(days=180)).date(),
                last_assessment_result=TestResult.PASS
            )
            self.session.add(control)
            self.controls[ctrl_id] = control
            print(f"   ✓ Control: {ctrl_id} - {name_en} [{effectiveness}%]")
        
        await self.session.flush()
    
    async def create_control_tests(self):
        """Create control effectiveness tests"""
        print("\n🧪 Creating Control Tests...")
        assert self.session is not None
        org = self._require_org()
        
        test_count = 0
        for ctrl_id, control in list(self.controls.items())[:10]:  # Test first 10 controls
            test = ControlAssessment(
                organization_id=org.id,
                control_id=control.id,
                assessment_date=(datetime.utcnow() - timedelta(days=random.randint(1, 60))).date(),
                assessor_id=self.users["auditor"].id,
                test_result=TestResult.PASS if random.random() > 0.15 else TestResult.FAIL,
                effectiveness_score=random.randint(70, 95),
                findings_summary_en=(
                    f"Control test for {ctrl_id} completed successfully"
                    if random.random() > 0.15
                    else f"Control gap identified in {ctrl_id}"
                ),
                findings_summary_ar=f"اختبار الضوابط {ctrl_id} مكتمل",
                status="approved"
            )
            self.session.add(test)
            test_count += 1
        
        print(f"   ✓ Created {test_count} control tests")
        await self.session.flush()
    
    async def create_risks(self):
        """Create comprehensive risk register"""
        print("\n⚠️ Creating Risk Register...")
        assert self.session is not None
        org = self._require_org()
        org = self._require_org()
        
        risks_data = [
            # Cyber Risks
            ("RSK-2024-001", "Ransomware Attack", "هجوم فدية إلكترونية",
             "cyber", "External threat actor deploys ransomware via phishing",
             5, 5, 25, 2, 3, 6, "open", self.users["ciso"].id, "CORE-BANKING-01"),
            
            ("RSK-2024-002", "Data Breach of Customer PII", "اختراق بيانات العملاء",
             "privacy", "Unauthorized access to customer database",
             4, 5, 20, 2, 4, 8, "open", self.users["compliance"].id, "CUSTOMER-DB"),
            
            ("RSK-2024-003", "DDoS Attack on Public Services", "هجوم حجب الخدمة",
             "cyber", "Distributed denial of service targeting online banking",
             3, 4, 12, 1, 3, 3, "mitigated", self.users["ciso"].id, "PAYMENT-GW-01"),
            
            ("RSK-2024-004", "Insider Threat", "تهديد داخلي",
             "operational", "Privileged user abuses access to steal data",
             3, 5, 15, 2, 4, 8, "open", self.users["ciso"].id, "DB-PROD-01"),
            
            ("RSK-2024-005", "Third-Party Vendor Breach", "اختراق عبر طرف ثالث",
             "third_party", "Security incident at cloud service provider",
             4, 4, 16, 2, 3, 6, "open", self.users["risk"].id, "CRM-SYSTEM"),
            
            # Compliance Risks
            ("RSK-2024-006", "NCA ECC Non-Compliance", "عدم امتثال ECC",
             "compliance", "Failure to meet NCA essential cybersecurity controls",
             3, 5, 15, 1, 3, 3, "mitigated", self.users["compliance"].id, None),
            
            ("RSK-2024-007", "PDPL Violation", "مخالفة نظام حماية البيانات",
             "compliance", "Inadequate consent management for customer data",
             4, 4, 16, 2, 3, 6, "open", self.users["compliance"].id, "CUSTOMER-DB"),
            
            # Operational Risks
            ("RSK-2024-008", "System Availability Failure", "فشل توفر النظام",
             "operational", "Critical system outage exceeding RTO",
             3, 4, 12, 2, 3, 6, "open", self.users["ciso"].id, "CORE-BANKING-01"),
            
            ("RSK-2024-009", "Backup Failure", "فشل النسخ الاحتياطي",
             "operational", "Inability to restore from backups during disaster",
             4, 5, 20, 2, 3, 6, "open", self.users["ciso"].id, "DB-PROD-01"),
            
            # Strategic Risks
            ("RSK-2024-010", "Emerging Threat (AI-Powered Attacks)", "تهديدات ذكاء اصطناعي",
             "strategic", "Sophisticated AI-driven social engineering attacks",
             4, 4, 16, 3, 4, 12, "accepted", self.users["ciso"].id, None),
        ]
        
        for (risk_id, name_en, name_ar, category, desc, 
             likelihood, impact, score, res_like, res_imp, res_score, 
             status, owner_id, asset_id) in risks_data:
            
            asset = self.assets.get(asset_id) if asset_id else None
            
            risk = Risk(
                organization_id=org.id,
                risk_id=risk_id,
                title_en=name_en,
                title_ar=name_ar,
                risk_type=category,
                description_en=desc,
                description_ar=desc,
                likelihood_inherent=likelihood,
                impact_inherent=impact,
                risk_score_inherent=score,
                risk_level_inherent=RiskLevel.HIGH if score >= 15 else RiskLevel.MEDIUM,
                likelihood_residual=res_like,
                impact_residual=res_imp,
                risk_score_residual=res_score,
                risk_level_residual=RiskLevel.MEDIUM if res_score >= 8 else RiskLevel.LOW,
                risk_owner_id=owner_id,
                related_assets=[asset.asset_id] if asset else None,
                status=status,
                last_review_date=(datetime.utcnow() - timedelta(days=random.randint(1, 60))).date(),
                next_review_date=(datetime.utcnow() + timedelta(days=90)).date(),
                action_plan=f"Implement additional controls to mitigate {name_en}"
            )
            self.session.add(risk)
            self.risks[risk_id] = risk
            print(f"   ✓ Risk: {risk_id} - {name_en} [Inherent: {score}, Residual: {res_score}]")
        
        await self.session.flush()
    
    async def create_risk_treatments(self):
        """Create risk treatment plans"""
        print("\n📋 Creating Risk Treatment Plans...")
        # Treatment plans are embedded in risks above
        print("   ✓ Risk treatments defined in risk register")
    
    async def create_audit_programs(self):
        """Create audit programs"""
        print("\n📝 Creating Audit Programs...")
        assert self.session is not None
        org = self._require_org()
        
        programs_data = [
            ("AUD-2024-NCA-ECC", "NCA ECC Compliance Audit", "تدقيق امتثال ECC",
             "compliance", "NCA_ECC", datetime.utcnow() - timedelta(days=30),
             datetime.utcnow() + timedelta(days=30), self.users["auditor"].id, "in_progress"),
            
            ("AUD-2024-PDPL", "PDPL Privacy Audit", "تدقيق حماية البيانات الشخصية",
             "compliance", "PDPL", datetime.utcnow() - timedelta(days=15),
             datetime.utcnow() + timedelta(days=45), self.users["auditor"].id, "in_progress"),
            
            ("AUD-2024-ISO", "ISO 27001 Certification Audit", "تدقيق شهادة ISO 27001",
             "certification", "ISO_27001", datetime.utcnow() + timedelta(days=60),
             datetime.utcnow() + timedelta(days=90), self.users["auditor"].id, "planned"),
        ]
        
        for prog_id, name_en, name_ar, audit_type, scope, start, end, lead_id, status in programs_data:
            framework_enum = {
                "NCA_ECC": FrameworkType.ECC,
                "NCA_CCC": FrameworkType.CCC,
                "PDPL": FrameworkType.PDPL,
                "ISO_27001": FrameworkType.ISO_27001,
            }.get(scope, FrameworkType.CUSTOM)
            program = AuditProgram(
                organization_id=org.id,
                program_id=prog_id,
                title_en=name_en,
                title_ar=name_ar,
                audit_type=audit_type,
                framework=framework_enum,
                planned_start_date=start.date(),
                planned_end_date=end.date(),
                lead_auditor_id=lead_id,
                status=status,
                scope_description=f"Comprehensive audit of {name_en}"
            )
            self.session.add(program)
            print(f"   ✓ Audit Program: {prog_id} - {name_en} [{status}]")
        
        await self.session.flush()
    
    async def create_audit_findings(self):
        """Create audit findings"""
        print("\n🔍 Creating Audit Findings...")
        assert self.session is not None
        org = self._require_org()
        
        findings_data = [
            ("FIND-2024-001", "Missing MFA on Admin Accounts", "عدم تفعيل MFA للحسابات الإدارية",
             "high", "ECC-IS-2", "5 admin accounts without MFA enabled", "open"),
            
            ("FIND-2024-002", "Outdated Antivirus Signatures", "تحديثات برامج مكافحة الفيروسات قديمة",
             "medium", "ECC-IS-4", "12 workstations with outdated AV definitions", "open"),
            
            ("FIND-2024-003", "Incomplete Asset Inventory", "قائمة الأصول غير مكتملة",
             "medium", "ISO-8.1", "Asset register missing 45 shadow IT applications", "in_progress"),
            
            ("FIND-2024-004", "No DPIA for New CRM System", "عدم إجراء تقييم أثر الخصوصية",
             "high", "PDPL-1", "New CRM processes customer PII without DPIA", "open"),
            
            ("FIND-2024-005", "Weak Password Policy", "سياسة كلمات المرور ضعيفة",
             "low", "ECC-IS-1", "Password complexity insufficient", "resolved"),
        ]
        
        for find_id, title_en, title_ar, severity, control_id, desc, status in findings_data:
            control = self.controls.get(control_id)
            severity_enum = {
                "high": FindingSeverity.HIGH,
                "medium": FindingSeverity.MEDIUM,
                "low": FindingSeverity.LOW,
            }.get(severity, FindingSeverity.MEDIUM)
            status_enum = {
                "open": CaseStatus.OPEN,
                "in_progress": CaseStatus.IN_PROGRESS,
                "resolved": CaseStatus.RESOLVED,
            }.get(status, CaseStatus.OPEN)
            finding = AuditFinding(
                organization_id=org.id,
                finding_id=find_id,
                control_id=control.id if control else None,
                title_en=title_en,
                title_ar=title_ar,
                description_en=desc,
                description_ar=desc,
                severity=severity_enum,
                risk_rating=RiskLevel.HIGH if severity == "high" else RiskLevel.MEDIUM,
                remediation_plan_en=f"Remediate finding {find_id}",
                remediation_owner_id=self.users["ciso"].id if severity == "high" else self.users["analyst"].id,
                target_closure_date=(datetime.utcnow() + timedelta(days=30)).date(),
                status=status_enum,
                identified_by_id=self.users["auditor"].id,
                identified_at=datetime.utcnow() - timedelta(days=random.randint(10, 60))
            )
            self.session.add(finding)
            print(f"   ✓ Finding: {find_id} - {title_en} [{severity}]")
        
        await self.session.flush()
    
    async def create_evidence(self):
        """Create evidence repository"""
        print("\n📎 Creating Evidence Repository...")
        assert self.session is not None
        org = self._require_org()
        
        evidence_count = 0
        for ctrl_id, control in list(self.controls.items())[:8]:
            evidence = Evidence(
                organization_id=org.id,
                evidence_id=f"EVID-{ctrl_id}",
                control_id=control.id,
                title_en=f"Evidence for {ctrl_id}",
                title_ar=f"دليل للضابط {ctrl_id}",
                file_path=f"/evidence/{ctrl_id}/{ctrl_id}_policy_v1.0.pdf",
                status="approved",
                uploaded_at=datetime.utcnow() - timedelta(days=random.randint(1, 90)),
                uploaded_by_id=self.users["auditor"].id
            )
            self.session.add(evidence)
            evidence_count += 1
        
        print(f"   ✓ Created {evidence_count} evidence items")
        await self.session.flush()
    
    async def create_vendors(self):
        """Create vendor risk assessments"""
        print("\n🏢 Creating Vendor Risk Assessments...")
        assert self.session is not None
        org = self._require_org()
        
        vendors_data = [
            ("VEN-001", "AWS Cloud Services", "خدمات أمازون السحابية", "critical", "active",
             15, "CORE-BANKING-01", "Infrastructure hosting", "annual", 85),
            
            ("VEN-002", "Microsoft Azure", "مايكروسوفت أزور", "high", "active",
             12, "CRM-SYSTEM", "Cloud applications", "annual", 88),
            
            ("VEN-003", "Symantec Endpoint Protection", "حماية نقاط النهاية", "medium", "active",
             8, None, "Antivirus and endpoint security", "quarterly", 82),
            
            ("VEN-004", "Splunk SIEM", "نظام إدارة المعلومات الأمنية", "high", "active",
             10, None, "Security monitoring and SIEM", "semi_annual", 90),
        ]
        
        for (vendor_id, name_en, name_ar, criticality, status, score, 
             asset_id, services, review, compliance) in vendors_data:
            
            asset = self.assets.get(asset_id) if asset_id else None
            
            vendor = Vendor(
                organization_id=org.id,
                vendor_id=vendor_id,
                name_en=name_en,
                name_ar=name_ar,
                vendor_type="technology",
                criticality=AssetCriticality(criticality),
                status=status,
                risk_score=score,
                risk_level=RiskLevel.HIGH if score >= 12 else RiskLevel.MEDIUM,
                last_assessment_date=(datetime.utcnow() - timedelta(days=random.randint(30, 180))).date(),
                next_assessment_date=(datetime.utcnow() + timedelta(days=365)).date()
            )
            self.session.add(vendor)
            print(f"   ✓ Vendor: {vendor_id} - {name_en} [Risk: {score}]")
        
        await self.session.flush()
    
    async def create_policies(self):
        """Create policy management system"""
        print("\n📜 Creating Policy Library...")
        assert self.session is not None
        org = self._require_org()
        
        policies_data = [
            ("POL-IS-001", "Information Security Policy", "سياسة أمن المعلومات",
             "Board-approved master IS policy", "security", "approved", self.users["ciso"].id),
            
            ("POL-AC-001", "Access Control Policy", "سياسة التحكم في الوصول",
             "Least privilege access control policy", "security", "approved", self.users["ciso"].id),
            
            ("POL-DR-001", "Disaster Recovery Policy", "سياسة استعادة الأعمال",
             "Business continuity and disaster recovery", "operational", "approved", self.users["ciso"].id),
            
            ("POL-PR-001", "Privacy Policy", "سياسة الخصوصية",
             "PDPL-compliant data privacy policy", "privacy", "approved", self.users["compliance"].id),
        ]
        
        for policy_id, name_en, name_ar, desc, category, status, owner_id in policies_data:
            policy = Policy(
                organization_id=org.id,
                policy_id=policy_id,
                title_en=name_en,
                title_ar=name_ar,
                description_en=desc,
                description_ar=desc,
                policy_type=category,
                status=status,
                version="1.0",
                owner_id=owner_id,
                approved_at=datetime.utcnow() - timedelta(days=365),
                effective_date=(datetime.utcnow() - timedelta(days=365)).date(),
                review_date=(datetime.utcnow() + timedelta(days=365)).date()
            )
            self.session.add(policy)
            print(f"   ✓ Policy: {policy_id} - {name_en} [v1.0]")
        
        await self.session.flush()
    
    async def create_pdpl_records(self):
        """Create PDPL Records of Processing Activities"""
        print("\n🗄️ Creating PDPL Processing Records...")
        assert self.session is not None
        org = self._require_org()
        
        ropa_data = [
            ("ROPA-2024-001", "Customer Onboarding", "تسجيل العملاء الجدد",
             "Customer KYC data collection", ["Name", "ID Number", "Address", "Phone"], 
             "Service Delivery", "customers", "legitimate_interest", True, "Banking Services", 7),
            
            ("ROPA-2024-002", "Transaction Processing", "معالجة المعاملات",
             "Payment and transaction data processing", ["Account Number", "Transaction Amount", "Timestamp"],
             "Transaction Processing", "customers", "contract", True, "Payment Provider", 5),
            
            ("ROPA-2024-003", "Marketing Communications", "الاتصالات التسويقية",
             "Customer marketing preferences and communications", ["Email", "Phone", "Marketing Preferences"],
             "Marketing", "customers", "consent", False, None, 2),
        ]
        
        for (ropa_id, name_en, name_ar, desc, data_cats, purpose, 
             subjects, legal_basis, shared, recipients, retention) in ropa_data:
            
            ropa = RecordOfProcessingActivity(
                organization_id=org.id,
                ropa_id=ropa_id,
                activity_name_en=name_en,
                activity_name_ar=name_ar,
                purpose_en=desc,
                purpose_ar=desc,
                data_categories=data_cats,
                data_subjects=[subjects],
                legal_basis=legal_basis,
                data_recipients=[recipients] if shared and recipients else None,
                retention_period=f"{retention} years",
                status="active",
                created_at=datetime.utcnow() - timedelta(days=random.randint(30, 180))
            )
            self.session.add(ropa)
            print(f"   ✓ RoPA: {ropa_id} - {name_en} [{legal_basis}]")
        
        await self.session.flush()
    
    async def create_dsar(self):
        """Create Data Subject Access Requests"""
        print("\n👤 Creating PDPL Data Subject Requests...")
        assert self.session is not None
        org = self._require_org()
        
        dsar_data = [
            ("DSAR-2024-001", "access", "in_progress", "Customer requests copy of all personal data"),
            ("DSAR-2024-002", "deletion", "completed", "Customer requests deletion after account closure"),
            ("DSAR-2024-003", "correction", "in_progress", "Customer requests correction of address"),
        ]
        
        for dsar_id, request_type, status, desc in dsar_data:
            dsar = DataSubjectRequest(
                organization_id=org.id,
                request_id=dsar_id,
                request_type=request_type,
                status=(CaseStatus.IN_PROGRESS if status == "in_progress" else CaseStatus.RESOLVED),
                subject_name="Customer Name",
                subject_email=f"customer{dsar_id[-3:]}@example.com",
                request_description=desc,
                received_date=(datetime.utcnow() - timedelta(days=random.randint(5, 25))).date(),
                due_date=(datetime.utcnow() + timedelta(days=5)).date(),
                assigned_to_id=self.users["compliance"].id
            )
            self.session.add(dsar)
            print(f"   ✓ DSAR: {dsar_id} - {request_type} [{status}]")
        
        await self.session.flush()
    
    async def create_data_breaches(self):
        """Create data breach incidents"""
        print("\n🚨 Creating Data Breach Incidents...")
        assert self.session is not None
        org = self._require_org()
        
        breach = DataBreach(
            organization_id=org.id,
            breach_id="BREACH-2024-001",
            description_en="Contractor accessed production database using test credentials",
            description_ar="وصل مقاول إلى قاعدة البيانات الإنتاجية باستخدام بيانات اختبار",
            breach_type="unauthorized_access",
            severity=FindingSeverity.MEDIUM,
            affected_data_subjects_count=150,
            data_categories_affected=["Email", "Phone"],
            breach_date=datetime.utcnow() - timedelta(days=45),
            discovery_date=datetime.utcnow() - timedelta(days=44),
            sdaia_notified=True,
            sdaia_notification_date=datetime.utcnow() - timedelta(days=42),
            subjects_notified=True,
            notification_method="email",
            containment_measures="Revoked credentials and isolated access",
            remediation_plan="Implemented privileged access management",
            lessons_learned="Enforce credential rotation and monitoring"
        )
        self.session.add(breach)
        print("   ✓ Breach: BREACH-2024-001 - Unauthorized Access [resolved]")
        
        await self.session.flush()
    
    async def create_incidents(self):
        """Create security incident cases"""
        print("\n🔴 Creating Security Incidents...")
        assert self.session is not None
        org = self._require_org()
        
        incidents_data = [
            ("INC-2024-001", "Phishing Email Campaign", "حملة تصيد احتيالي",
             "security", "high", "in_progress", "Multiple employees received phishing emails"),
            
            ("INC-2024-002", "Failed Login Attempts", "محاولات تسجيل دخول فاشلة",
             "security", "medium", "investigating", "1000+ failed login attempts detected from foreign IP"),
            
            ("INC-2024-003", "Malware Detected on Workstation", "برمجية خبيثة على محطة عمل",
             "security", "medium", "resolved", "Endpoint protection detected and quarantined malware"),
        ]
        
        for inc_id, title_en, title_ar, case_type, priority, status, desc in incidents_data:
            status_enum = {
                "in_progress": CaseStatus.IN_PROGRESS,
                "investigating": CaseStatus.IN_PROGRESS,
                "resolved": CaseStatus.RESOLVED,
            }.get(status, CaseStatus.OPEN)
            incident = WorkflowCase(
                organization_id=org.id,
                case_id=inc_id,
                title_en=title_en,
                title_ar=title_ar,
                case_type=case_type,
                priority=priority,
                status=status_enum,
                description_en=desc,
                description_ar=desc,
                assigned_to_id=self.users["ciso"].id if priority == "high" else self.users["analyst"].id
            )
            self.session.add(incident)
            print(f"   ✓ Incident: {inc_id} - {title_en} [{priority}]")
        
        await self.session.flush()
    
    async def print_summary(self):
        """Print demo data summary"""
        from sqlalchemy import select, func
        org = self._require_org()
        assert self.session is not None
        
        print("\n📊 DEMO DATA SUMMARY")
        print("-" * 80)
        
        # Count all entities
        counts = {
            "Organizations": Organization,
            "Users": User,
            "Assets": Asset,
            "Controls": Control,
            "Control Tests": ControlAssessment,
            "Risks": Risk,
            "Audit Programs": AuditProgram,
            "Audit Findings": AuditFinding,
            "Evidence Items": Evidence,
            "Vendors": Vendor,
            "Policies": Policy,
            "PDPL RoPA Records": RecordOfProcessingActivity,
            "PDPL DSARs": DataSubjectRequest,
            "Data Breaches": DataBreach,
            "Security Incidents": WorkflowCase,
        }
        
        for name, model in counts.items():
            result = await self.session.execute(
                select(func.count()).select_from(model)
            )
            count = result.scalar()
            print(f"   {name:.<40} {count:>3}")
        
        print("-" * 80)
        print("\n🎯 KEY METRICS")
        print(f"   Organization: {org.name_en}")
        print(f"   Industry: {org.industry_en}")
        print(f"   Employees: {org.employee_count:,}")
        print(f"   Frameworks: {', '.join(org.compliance_frameworks)}")
        
        # Risk statistics
        high_risks = await self.session.execute(
            select(func.count()).select_from(Risk).where(Risk.risk_score_inherent >= 15)
        )
        print(f"\n   High Risks: {high_risks.scalar()}")
        
        # Control effectiveness
        avg_effectiveness = await self.session.execute(
            select(func.avg(Control.effectiveness_score)).select_from(Control)
        )
        print(f"   Avg Control Effectiveness: {avg_effectiveness.scalar():.1f}%")
        
        print("\n" + "=" * 80)
        print("✅ Platform ready for demonstration!")
        print("\n🌐 Access Points:")
        print("   Frontend: http://localhost:3000")
        print("   Backend API: http://localhost:8000")
        print("   API Docs: http://localhost:8000/docs")
        print("\n👥 Demo Users:")
        print("   Admin: admin / Password123!")
        print("   CISO: ciso / Password123!")
        print("   Compliance Officer: compliance / Password123!")
        print("=" * 80)


async def main():
    """Main entry point"""
    print("Initializing database...")
    await init_db()
    
    loader = EnterpriseDataLoader()
    await loader.load_all()


if __name__ == "__main__":
    asyncio.run(main())
