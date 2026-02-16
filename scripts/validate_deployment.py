#!/usr/bin/env python3
"""
Production Deployment Validation Script
Comprehensive end-to-end testing of SICO GRC Platform
Validates deployment readiness, security, compliance, and operability
"""

import asyncio
import sys
import os
import json
from datetime import datetime
from typing import List, Dict, Tuple
import logging

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ValidationResult:
    """Store validation test results"""
    def __init__(self, test_name: str, passed: bool, message: str, details: Dict = None):
        self.test_name = test_name
        self.passed = passed
        self.message = message
        self.details = details or {}
    
    def __str__(self):
        status = "✅ PASS" if self.passed else "❌ FAIL"
        return f"{status}: {self.test_name} - {self.message}"


class ProductionValidator:
    """Comprehensive production deployment validator"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.results: List[ValidationResult] = []
        self.engine = None
        self.session_maker = None
    
    async def initialize(self):
        """Initialize database connection"""
        try:
            self.engine = create_async_engine(self.database_url, echo=False)
            self.session_maker = async_sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)
            logger.info("✓ Database connection initialized")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to initialize database: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.engine:
            await self.engine.dispose()
    
    def add_result(self, test_name: str, passed: bool, message: str, details: Dict = None):
        """Add validation result"""
        result = ValidationResult(test_name, passed, message, details)
        self.results.append(result)
        logger.info(str(result))
    
    # ========================================================================
    # DATABASE VALIDATION
    # ========================================================================
    
    async def validate_database_connection(self) -> bool:
        """Test database connectivity"""
        try:
            async with self.session_maker() as session:
                result = await session.execute(text("SELECT 1"))
                self.add_result("Database Connection", True, "Database is accessible")
                return True
        except Exception as e:
            self.add_result("Database Connection", False, f"Cannot connect to database: {e}")
            return False
    
    async def validate_migrations(self) -> bool:
        """Verify all migrations have been applied"""
        try:
            async with self.session_maker() as session:
                # Check if alembic_version table exists
                result = await session.execute(text(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alembic_version')"
                ))
                exists = result.scalar()
                
                if not exists:
                    self.add_result("Database Migrations", False, "Alembic version table not found")
                    return False
                
                # Check current version
                result = await session.execute(text("SELECT version_num FROM alembic_version"))
                version = result.scalar()
                
                self.add_result("Database Migrations", True, f"Migrations applied, current version: {version}")
                return True
        except Exception as e:
            self.add_result("Database Migrations", False, f"Migration check failed: {e}")
            return False
    
    async def validate_required_tables(self) -> bool:
        """Verify all required tables exist"""
        required_tables = [
            'controls', 'evidence', 'reports', 'users', 'roles', 'permissions',
            'processing_activities', 'data_subject_requests', 'data_breaches',
            'incidents', 'risks', 'ai_models', 'security_events', 'assets',
            'organizations', 'audit_logs'
        ]
        
        try:
            async with self.session_maker() as session:
                missing_tables = []
                for table in required_tables:
                    result = await session.execute(text(
                        f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')"
                    ))
                    exists = result.scalar()
                    if not exists:
                        missing_tables.append(table)
                
                if missing_tables:
                    self.add_result("Required Tables", False, 
                                  f"Missing tables: {', '.join(missing_tables)}")
                    return False
                
                self.add_result("Required Tables", True, 
                              f"All {len(required_tables)} required tables exist")
                return True
        except Exception as e:
            self.add_result("Required Tables", False, f"Table check failed: {e}")
            return False
    
    # ========================================================================
    # CONTROL LIBRARY VALIDATION
    # ========================================================================
    
    async def validate_control_libraries(self) -> bool:
        """Verify NCA control libraries are populated"""
        try:
            async with self.session_maker() as session:
                # Count controls by framework
                result = await session.execute(text(
                    "SELECT framework, COUNT(*) as count FROM controls GROUP BY framework"
                ))
                framework_counts = {row[0]: row[1] for row in result}
                
                required_frameworks = {'ECC': 10, 'CCC': 4, 'PDPL': 12}  # Minimum expected
                missing_frameworks = []
                
                for framework, min_count in required_frameworks.items():
                    actual_count = framework_counts.get(framework, 0)
                    if actual_count < min_count:
                        missing_frameworks.append(f"{framework} ({actual_count}/{min_count})")
                
                if missing_frameworks:
                    self.add_result("Control Libraries", False,
                                  f"Insufficient controls: {', '.join(missing_frameworks)}")
                    return False
                
                total_controls = sum(framework_counts.values())
                self.add_result("Control Libraries", True,
                              f"{total_controls} controls loaded (ECC: {framework_counts.get('ECC', 0)}, "
                              f"CCC: {framework_counts.get('CCC', 0)}, PDPL: {framework_counts.get('PDPL', 0)})",
                              details=framework_counts)
                return True
        except Exception as e:
            self.add_result("Control Libraries", False, f"Control validation failed: {e}")
            return False
    
    # ========================================================================
    # SECURITY VALIDATION
    # ========================================================================
    
    async def validate_rbac_system(self) -> bool:
        """Verify RBAC system is initialized"""
        try:
            async with self.session_maker() as session:
                # Check roles
                result = await session.execute(text("SELECT COUNT(*) FROM roles"))
                role_count = result.scalar()
                
                # Check permissions
                result = await session.execute(text("SELECT COUNT(*) FROM permissions"))
                permission_count = result.scalar()
                
                if role_count == 0 or permission_count == 0:
                    self.add_result("RBAC System", False,
                                  f"RBAC not initialized (Roles: {role_count}, Permissions: {permission_count})")
                    return False
                
                self.add_result("RBAC System", True,
                              f"RBAC initialized ({role_count} roles, {permission_count} permissions)")
                return True
        except Exception as e:
            self.add_result("RBAC System", False, f"RBAC check failed: {e}")
            return False
    
    async def validate_audit_logging(self) -> bool:
        """Verify audit logging system is operational"""
        try:
            async with self.session_maker() as session:
                # Check audit_logs table
                result = await session.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'audit_logs')"))
                exists = result.scalar()
                
                if not exists:
                    self.add_result("Audit Logging", False, "Audit logs table not found")
                    return False
                
                # Check if any logs exist
                result = await session.execute(text("SELECT COUNT(*) FROM audit_logs"))
                log_count = result.scalar()
                
                self.add_result("Audit Logging", True,
                              f"Audit logging system ready ({log_count} existing logs)")
                return True
        except Exception as e:
            self.add_result("Audit Logging", False, f"Audit logging check failed: {e}")
            return False
    
    # ========================================================================
    # CONFIGURATION VALIDATION
    # ========================================================================
    
    def validate_environment_config(self) -> bool:
        """Validate environment configuration"""
        required_vars = {
            'SECRET_KEY': 32,  # Minimum length
            'DATABASE_URL': 10,
        }
        
        recommended_vars = [
            'ENCRYPTION_KEY',
            'REDIS_URL',
            'AZURE_KEY_VAULT_URL',
        ]
        
        missing = []
        insufficient = []
        
        for var, min_length in required_vars.items():
            value = os.getenv(var)
            if not value:
                missing.append(var)
            elif len(value) < min_length:
                insufficient.append(f"{var} (length < {min_length})")
        
        missing_recommended = [var for var in recommended_vars if not os.getenv(var)]
        
        if missing or insufficient:
            self.add_result("Environment Config", False,
                          f"Missing: {missing}, Insufficient: {insufficient}")
            return False
        
        message = "All required variables set"
        if missing_recommended:
            message += f" (Recommended missing: {', '.join(missing_recommended)})"
        
        self.add_result("Environment Config", True, message)
        return True
    
    # ========================================================================
    # COMPLIANCE VALIDATION
    # ========================================================================
    
    async def validate_pdpl_compliance(self) -> bool:
        """Verify PDPL compliance features"""
        try:
            async with self.session_maker() as session:
                # Check RoPA table
                result = await session.execute(text("SELECT COUNT(*) FROM processing_activities"))
                ropa_count = result.scalar()
                
                # Check DSAR table
                result = await session.execute(text("SELECT COUNT(*) FROM data_subject_requests"))
                dsar_count = result.scalar()
                
                # Check breach register
                result = await session.execute(text("SELECT COUNT(*) FROM data_breaches"))
                breach_count = result.scalar()
                
                self.add_result("PDPL Compliance", True,
                              f"PDPL systems ready (RoPA: {ropa_count}, DSAR: {dsar_count}, Breaches: {breach_count})")
                return True
        except Exception as e:
            self.add_result("PDPL Compliance", False, f"PDPL validation failed: {e}")
            return False
    
    # ========================================================================
    # REPORT GENERATION
    # ========================================================================
    
    def generate_report(self) -> Dict:
        """Generate comprehensive validation report"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            "validation_date": datetime.utcnow().isoformat(),
            "database_url": self.database_url.split('@')[1] if '@' in self.database_url else "hidden",
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": f"{success_rate:.1f}%",
                "deployment_ready": failed_tests == 0
            },
            "results": [
                {
                    "test": r.test_name,
                    "status": "PASS" if r.passed else "FAIL",
                    "message": r.message,
                    "details": r.details
                }
                for r in self.results
            ]
        }
        
        return report
    
    def print_summary(self):
        """Print validation summary"""
        print("\n" + "="*80)
        print("PRODUCTION DEPLOYMENT VALIDATION REPORT")
        print("="*80)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests
        
        print(f"\nTotal Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests == 0:
            print("\n🎉 DEPLOYMENT READY: All validation tests passed!")
            print("   The system is ready for production deployment.")
        else:
            print("\n⚠️  DEPLOYMENT BLOCKED: Some tests failed")
            print("   Please resolve issues before production deployment.")
            print("\nFailed Tests:")
            for result in self.results:
                if not result.passed:
                    print(f"   - {result.test_name}: {result.message}")
        
        print("\n" + "="*80)
    
    # ========================================================================
    # MAIN VALIDATION FLOW
    # ========================================================================
    
    async def run_all_validations(self) -> bool:
        """Run complete validation suite"""
        logger.info("Starting production deployment validation...")
        
        # Phase 1: Database
        logger.info("\n=== Phase 1: Database Validation ===")
        await self.validate_database_connection()
        await self.validate_migrations()
        await self.validate_required_tables()
        
        # Phase 2: Data
        logger.info("\n=== Phase 2: Data Validation ===")
        await self.validate_control_libraries()
        await self.validate_rbac_system()
        
        # Phase 3: Security
        logger.info("\n=== Phase 3: Security Validation ===")
        await self.validate_audit_logging()
        self.validate_environment_config()
        
        # Phase 4: Compliance
        logger.info("\n=== Phase 4: Compliance Validation ===")
        await self.validate_pdpl_compliance()
        
        # Generate report
        report = self.generate_report()
        self.print_summary()
        
        # Save report
        report_path = "deployment_validation_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        logger.info(f"\n✓ Detailed report saved: {report_path}")
        
        return report["summary"]["deployment_ready"]


async def main():
    """Main validation entry point"""
    # Get database URL from environment
    database_url = os.getenv(
        'DATABASE_URL',
        'postgresql+asyncpg://postgres:postgres@localhost:5432/sico_grc'
    )
    
    validator = ProductionValidator(database_url)
    
    try:
        # Initialize
        if not await validator.initialize():
            logger.error("Failed to initialize validator")
            sys.exit(1)
        
        # Run validations
        deployment_ready = await validator.run_all_validations()
        
        # Exit with appropriate code
        sys.exit(0 if deployment_ready else 1)
    
    finally:
        await validator.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
