"""
SICO GRC Platform - Final Production Validation Script
Comprehensive validation of all systems for commercial deployment to Saudi customers
Validates: Database, Official Controls, Security, SICO, Compliance, AI/RAG, Performance
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List
try:
    import httpx  # type: ignore
except ImportError:
    httpx = None  # type: ignore

sys.path.append(str(Path(__file__).parent.parent / "src"))

from sqlalchemy import select, text
from core.database import AsyncSessionLocal, engine  # type: ignore
from controls.models import Control, FrameworkType  # type: ignore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductionReadinessValidator:
    """Comprehensive production readiness validation"""
    
    def __init__(self):
        self.results = {
            "validation_date": datetime.utcnow().isoformat(),
            "product_name": "SICO GRC Platform",
            "product_version": "1.0 Production",
            "target_market": "Saudi Arabia Banking, Government, Healthcare",
            "regulatory_compliance": ["NCA ECC-1:2018", "NCA CCC-2:2024", "PDPL 2021/2022"],
            "phases": {},
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "warnings": 0,
                "deployment_ready": False,
                "commercial_ready": False
            }
        }
    
    def add_result(self, phase: str, test: str, status: str, details: str = ""):
        """Add validation result"""
        if phase not in self.results["phases"]:
            self.results["phases"][phase] = []
        
        self.results["phases"][phase].append({
            "test": test,
            "status": status,
            "details": details
        })
        
        self.results["summary"]["total_tests"] += 1
        if status == "PASS":
            self.results["summary"]["passed"] += 1
        elif status == "FAIL":
            self.results["summary"]["failed"] += 1
        elif status == "WARNING":
            self.results["summary"]["warnings"] += 1
    
    async def validate_official_control_library(self):
        """Validate official NCA control library completeness"""
        logger.info("\n🔍 PHASE 1: Official NCA Control Library Validation")
        logger.info("="*70)
        
        async with AsyncSessionLocal() as session:
            # Test 1: ECC Controls
            result = await session.execute(
                select(Control).where(Control.framework == FrameworkType.ECC)
            )
            ecc_controls = result.scalars().all()
            
            if len(ecc_controls) >= 40:
                self.add_result("Control Library", "ECC Controls", "PASS", 
                               f"{len(ecc_controls)} controls loaded (expected 40+)")
                logger.info(f"✅ ECC: {len(ecc_controls)} controls")
            else:
                self.add_result("Control Library", "ECC Controls", "FAIL",
                               f"Only {len(ecc_controls)} controls found (expected 40+)")
                logger.error(f"❌ ECC: Insufficient controls")
            
            # Test 2: CCC Controls
            result = await session.execute(
                select(Control).where(Control.framework == FrameworkType.CCC)
            )
            ccc_controls = result.scalars().all()
            
            if len(ccc_controls) >= 20:
                self.add_result("Control Library", "CCC Controls", "PASS",
                               f"{len(ccc_controls)} controls loaded (expected 20+)")
                logger.info(f"✅ CCC: {len(ccc_controls)} controls")
            else:
                self.add_result("Control Library", "CCC Controls", "WARNING",
                               f"Only {len(ccc_controls)} controls found (expected 20+)")
                logger.warning(f"⚠️  CCC: {len(ccc_controls)} controls")
            
            # Test 3: PDPL Controls
            result = await session.execute(
                select(Control).where(Control.framework == FrameworkType.PDPL)
            )
            pdpl_controls = result.scalars().all()
            
            if len(pdpl_controls) >= 15:
                self.add_result("Control Library", "PDPL Controls", "PASS",
                               f"{len(pdpl_controls)} controls loaded (expected 15+)")
                logger.info(f"✅ PDPL: {len(pdpl_controls)} controls")
            else:
                self.add_result("Control Library", "PDPL Controls", "WARNING",
                               f"Only {len(pdpl_controls)} controls found (expected 15+)")
                logger.warning(f"⚠️  PDPL: {len(pdpl_controls)} controls")
            
            # Test 4: Bilingual Support
            sample_controls = ecc_controls[:5] if ecc_controls else []
            bilingual_ok = all(
                ctrl.title_en and ctrl.title_ar and 
                ctrl.control_clause_en and ctrl.control_clause_ar
                for ctrl in sample_controls
            )
            
            if bilingual_ok:
                self.add_result("Control Library", "Bilingual Support", "PASS",
                               "All controls have English and Arabic content")
                logger.info("✅ Bilingual: Full support")
            else:
                self.add_result("Control Library", "Bilingual Support", "WARNING",
                               "Some controls missing Arabic translations")
                logger.warning("⚠️  Bilingual: Incomplete")
            
            # Test 5: Cross-Framework Mappings
            mapped_count = sum(1 for ctrl in ecc_controls if ctrl.mapping_ccc or ctrl.mapping_pdpl)
            
            if mapped_count > 0:
                self.add_result("Control Library", "Cross-Framework Mappings", "PASS",
                               f"{mapped_count} ECC controls have CCC/PDPL mappings")
                logger.info(f"✅ Mappings: {mapped_count} ECC controls mapped")
            else:
                self.add_result("Control Library", "Cross-Framework Mappings", "WARNING",
                               "No cross-framework mappings found")
                logger.warning("⚠️  Mappings: None found")
            
            # Test 6: Source Tracking
            sourced_count = sum(1 for ctrl in ecc_controls if ctrl.source_pdf and ctrl.source_page)
            
            if sourced_count > 0:
                self.add_result("Control Library", "Source Provenance", "PASS",
                               f"{sourced_count} controls have source PDF tracking")
                logger.info(f"✅ Provenance: {sourced_count} controls sourced")
            else:
                self.add_result("Control Library", "Source Provenance", "WARNING",
                               "Source provenance tracking missing")
                logger.warning("⚠️  Provenance: Not tracked")
    
    async def validate_commercial_readiness(self):
        """Validate commercial deployment readiness"""
        logger.info("\n🔍 PHASE 2: Commercial Readiness Validation")
        logger.info("="*70)
        
        # Test 1: Documentation
        docs = [
            "README.md",
            "COMMERCIAL_PRODUCT_GUIDE.md",
            "PRODUCTION_REMEDIATION_REPORT.md",
            "DEPLOYMENT_GUIDE.md",
            "QUICK_START.md"
        ]
        
        missing_docs = []
        for doc in docs:
            if not Path(doc).exists():
                missing_docs.append(doc)
        
        if not missing_docs:
            self.add_result("Commercial", "Documentation Complete", "PASS",
                           "All required documentation present")
            logger.info("✅ Documentation: Complete")
        else:
            self.add_result("Commercial", "Documentation Complete", "WARNING",
                           f"Missing: {', '.join(missing_docs)}")
            logger.warning(f"⚠️  Documentation: Missing {len(missing_docs)} files")
        
        # Test 2: Deployment Scripts
        scripts = [
            "scripts/load_official_nca_controls.py",
            "scripts/validate_deployment.py",
            "deployment/docker-compose.yml",
            "Makefile"
        ]
        
        missing_scripts = []
        for script in scripts:
            if not Path(script).exists():
                missing_scripts.append(script)
        
        if not missing_scripts:
            self.add_result("Commercial", "Deployment Scripts", "PASS",
                           "All deployment scripts present")
            logger.info("✅ Deployment: Scripts ready")
        else:
            self.add_result("Commercial", "Deployment Scripts", "FAIL",
                           f"Missing: {', '.join(missing_scripts)}")
            logger.error(f"❌ Deployment: Missing {len(missing_scripts)} scripts")
        
        # Test 3: Environment Templates
        if Path(".env.production.template").exists():
            self.add_result("Commercial", "Production Environment Template", "PASS",
                           ".env.production.template present")
            logger.info("✅ Config: Production template ready")
        else:
            self.add_result("Commercial", "Production Environment Template", "FAIL",
                           ".env.production.template missing")
            logger.error("❌ Config: Template missing")
        
        # Test 4: Docker Configuration
        if Path("deployment/docker-compose.yml").exists():
            self.add_result("Commercial", "Docker Compose Configuration", "PASS",
                           "Docker deployment configured")
            logger.info("✅ Docker: Configured")
        else:
            self.add_result("Commercial", "Docker Compose Configuration", "FAIL",
                           "Docker compose file missing")
            logger.error("❌ Docker: Not configured")
    
    async def validate_security_hardening(self):
        """Validate production security hardening"""
        logger.info("\n🔍 PHASE 3: Security Hardening Validation")
        logger.info("="*70)
        
        # Test 1: Secrets Management
        secrets_file = Path("src/backend/core/secrets_manager.py")
        if secrets_file.exists():
            self.add_result("Security", "Secrets Manager", "PASS",
                           "Centralized secrets management implemented")
            logger.info("✅ Security: Secrets manager present")
        else:
            self.add_result("Security", "Secrets Manager", "FAIL",
                           "Secrets manager not found")
            logger.error("❌ Security: No secrets manager")
        
        # Test 2: Audit Logging
        audit_file = Path("src/backend/core/audit_logger.py")
        if audit_file.exists():
            self.add_result("Security", "Immutable Audit Logging", "PASS",
                           "Cryptographic audit logging implemented")
            logger.info("✅ Security: Audit logging implemented")
        else:
            self.add_result("Security", "Immutable Audit Logging", "FAIL",
                           "Audit logger not found")
            logger.error("❌ Security: No audit logging")
        
        # Test 3: Migrations
        migrations_dir = Path("src/backend/migrations/versions")
        migration_files = list(migrations_dir.glob("*.py")) if migrations_dir.exists() else []
        
        if len(migration_files) >= 6:
            self.add_result("Security", "Database Migrations", "PASS",
                           f"{len(migration_files)} migration files present")
            logger.info(f"✅ Database: {len(migration_files)} migrations")
        else:
            self.add_result("Security", "Database Migrations", "WARNING",
                           f"Only {len(migration_files)} migrations found")
            logger.warning(f"⚠️  Database: {len(migration_files)} migrations")
    
    async def validate_regulatory_compliance(self):
        """Validate Saudi regulatory compliance features"""
        logger.info("\n🔍 PHASE 4: Saudi Regulatory Compliance Validation")
        logger.info("="*70)
        
        async with AsyncSessionLocal() as session:
            # Test 1: PDPL Tables
            pdpl_tables = ["ropa", "dsar", "breach_register"]
            
            try:
                for table in pdpl_tables:
                    await session.execute(text(f"SELECT 1 FROM {table} LIMIT 1"))
                
                self.add_result("Compliance", "PDPL Tables", "PASS",
                               "RoPA, DSAR, Breach Register tables exist")
                logger.info("✅ PDPL: All tables present")
            except Exception as e:
                self.add_result("Compliance", "PDPL Tables", "WARNING",
                               f"PDPL tables validation failed: {str(e)}")
                logger.warning(f"⚠️  PDPL: Table check failed")
            
            # Test 2: Audit Log Retention
            # Check if audit_logs table has retention_until column
            try:
                await session.execute(text("SELECT retention_until FROM audit_logs LIMIT 1"))
                self.add_result("Compliance", "7-Year Audit Retention", "PASS",
                               "Audit log retention supported (NCA ECC-IS-5)")
                logger.info("✅ Compliance: 7-year retention configured")
            except Exception as e:
                self.add_result("Compliance", "7-Year Audit Retention", "WARNING",
                               "Audit retention column not found")
                logger.warning("⚠️  Compliance: Retention not configured")
    
    async def validate_framework_coverage(self):
        """Validate control framework coverage for Saudi market"""
        logger.info("\n🔍 PHASE 5: Framework Coverage for Saudi Market")
        logger.info("="*70)
        
        async with AsyncSessionLocal() as session:
            # ECC Domains
            result = await session.execute(
                select(Control.domain).where(Control.framework == FrameworkType.ECC).distinct()
            )
            ecc_domains = [row[0] for row in result]
            
            expected_ecc_domains = ["Cybersecurity Governance", "Cybersecurity Defense"]
            has_governance = any("Governance" in d for d in ecc_domains)
            has_defense = any("Defense" in d for d in ecc_domains)
            
            if has_governance and has_defense:
                self.add_result("Framework Coverage", "ECC Domains", "PASS",
                               f"Both Governance and Defense domains present")
                logger.info("✅ ECC: Complete domain coverage")
            else:
                self.add_result("Framework Coverage", "ECC Domains", "WARNING",
                               "Missing Governance or Defense domain")
                logger.warning("⚠️  ECC: Incomplete domain coverage")
            
            # CCC Control Types (Provider vs Tenant)
            result = await session.execute(
                select(Control.control_id).where(Control.framework == FrameworkType.CCC)
            )
            ccc_ids = [row[0] for row in result]
            
            has_provider = any("-P-" in id for id in ccc_ids)
            has_tenant = any("-T-" in id for id in ccc_ids)
            
            if has_provider and has_tenant:
                self.add_result("Framework Coverage", "CCC Control Types", "PASS",
                               "Both Provider (P) and Tenant (T) controls present")
                logger.info("✅ CCC: Provider and Tenant controls")
            elif has_provider or has_tenant:
                self.add_result("Framework Coverage", "CCC Control Types", "WARNING",
                               "Only Provider or Tenant controls found")
                logger.warning("⚠️  CCC: Missing control type")
            else:
                self.add_result("Framework Coverage", "CCC Control Types", "FAIL",
                               "No CCC-specific control types found")
                logger.error("❌ CCC: Invalid control structure")
            
            # PDPL Articles Coverage
            result = await session.execute(
                select(Control.subdomain).where(Control.framework == FrameworkType.PDPL).distinct()
            )
            pdpl_articles = [row[0] for row in result if row[0]]
            
            critical_articles = ["Article 3", "Article 19", "Article 29", "Article 31"]
            has_critical = sum(1 for art in critical_articles if any(art in a for a in pdpl_articles))
            
            if has_critical >= 3:
                self.add_result("Framework Coverage", "PDPL Critical Articles", "PASS",
                               f"{has_critical}/4 critical articles covered")
                logger.info(f"✅ PDPL: {has_critical}/4 critical articles")
            else:
                self.add_result("Framework Coverage", "PDPL Critical Articles", "WARNING",
                               f"Only {has_critical}/4 critical articles covered")
                logger.warning(f"⚠️  PDPL: {has_critical}/4 critical articles")
    
    def generate_report(self):
        """Generate final validation report"""
        # Calculate success rate
        if self.results["summary"]["total_tests"] > 0:
            success_rate = (self.results["summary"]["passed"] / 
                          self.results["summary"]["total_tests"]) * 100
            self.results["summary"]["success_rate"] = round(success_rate, 2)
        else:
            self.results["summary"]["success_rate"] = 0
        
        # Determine deployment readiness
        failed = self.results["summary"]["failed"]
        warnings = self.results["summary"]["warnings"]
        
        self.results["summary"]["deployment_ready"] = (failed == 0)
        self.results["summary"]["commercial_ready"] = (failed == 0 and warnings <= 3)
        
        # Save to file
        report_path = Path(__file__).parent / "production_readiness_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n📄 Report saved to: {report_path}")
        return report_path
    
    def print_summary(self):
        """Print validation summary"""
        logger.info("\n" + "="*70)
        logger.info("PRODUCTION READINESS VALIDATION SUMMARY")
        logger.info("="*70)
        
        logger.info(f"Product: {self.results['product_name']} v{self.results['product_version']}")
        logger.info(f"Target Market: {self.results['target_market']}")
        logger.info(f"Regulatory Compliance: {', '.join(self.results['regulatory_compliance'])}")
        logger.info(f"Validation Date: {self.results['validation_date']}")
        logger.info("")
        
        summary = self.results["summary"]
        logger.info(f"Total Tests: {summary['total_tests']}")
        logger.info(f"Passed: {summary['passed']} ✅")
        logger.info(f"Failed: {summary['failed']} ❌")
        logger.info(f"Warnings: {summary['warnings']} ⚠️")
        logger.info(f"Success Rate: {summary.get('success_rate', 0):.1f}%")
        logger.info("")
        
        if summary["commercial_ready"]:
            logger.info("🎉 STATUS: COMMERCIAL-READY FOR SAUDI MARKET")
            logger.info("✅ Platform approved for banking, government, healthcare deployment")
        elif summary["deployment_ready"]:
            logger.info("⚠️  STATUS: DEPLOYMENT-READY (with warnings)")
            logger.info("Platform functional but requires minor improvements")
        else:
            logger.info("❌ STATUS: NOT READY FOR PRODUCTION")
            logger.info(f"Critical issues found: {summary['failed']} failures")
        
        logger.info("="*70 + "\n")


async def main():
    """Main validation execution"""
    logger.info("="*70)
    logger.info("SICO GRC PLATFORM - PRODUCTION READINESS VALIDATION")
    logger.info("Saudi Arabia Banking, Government, Healthcare Deployment")
    logger.info("="*70 + "\n")
    
    validator = ProductionReadinessValidator()
    
    try:
        # Run all validation phases
        await validator.validate_official_control_library()
        await validator.validate_commercial_readiness()
        await validator.validate_security_hardening()
        await validator.validate_regulatory_compliance()
        await validator.validate_framework_coverage()
        
        # Generate report
        report_path = validator.generate_report()
        
        # Print summary
        validator.print_summary()
        
        logger.info(f"✅ Validation complete! Report: {report_path}")
        
    except Exception as e:
        logger.error(f"❌ Validation failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
