"""
Direct Enterprise Database Creation Script
Creates all tables from enterprise_models.py
"""

import sqlite3
import os
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / "sico_grc.db"

def create_enterprise_database():
    """Create enterprise GRC database schema"""
    
    print(f"Creating enterprise database at: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Disable foreign keys temporarily for dropping
    cursor.execute("PRAGMA foreign_keys = OFF;")
    
    # Drop all existing enterprise tables
    print("Dropping existing tables...")
    tables = [
        'compliance_metrics', 'automated_evidences', 'integrations',
        'data_breaches', 'dsar_requests', 'ropa_records', 'vendors',
        'workflow_cases', 'control_exceptions', 'control_assessments',
        'audit_findings', 'audit_programs', 'evidences', 'risks',
        'evidence_templates', 'policies', 'audit_logs', 'assets', 'users', 'organizations'
    ]
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
    
    conn.commit()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # ============================================================================
    # 1. ORGANIZATIONS (MULTI-TENANCY)
    # ============================================================================
    print("Creating organizations table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS organizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_en VARCHAR(255) NOT NULL,
            name_ar VARCHAR(255) NOT NULL,
            org_type VARCHAR(50),
            parent_org_id INTEGER,
            license_type VARCHAR(50),
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_org_id) REFERENCES organizations(id)
        )
    """)
    
    # ============================================================================
    # 2. USERS (RBAC)
    # ============================================================================
    print("Creating users table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER NOT NULL,
            username VARCHAR(100) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            full_name_en VARCHAR(255),
            full_name_ar VARCHAR(255),
            role VARCHAR(50) NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            last_login TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES organizations(id)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_users_username ON users(username)")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_users_email ON users(email)")
    
    # ============================================================================
    # 3. ASSETS
    # ============================================================================
    print("Creating assets table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER NOT NULL,
            asset_id VARCHAR(100) UNIQUE NOT NULL,
            asset_type VARCHAR(50) NOT NULL,
            name_en VARCHAR(255) NOT NULL,
            name_ar VARCHAR(255),
            description_en TEXT,
            description_ar TEXT,
            criticality VARCHAR(20) NOT NULL,
            classification VARCHAR(20),
            owner_id INTEGER,
            location VARCHAR(255),
            environment VARCHAR(50),
            is_active BOOLEAN DEFAULT 1,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES organizations(id),
            FOREIGN KEY (owner_id) REFERENCES users(id)
        )
    """)
    
    # ============================================================================
    # 4. AUDIT LOGS
    # ============================================================================
    print("Creating audit_logs table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER NOT NULL,
            user_id INTEGER,
            action VARCHAR(100) NOT NULL,
            entity_type VARCHAR(50) NOT NULL,
            entity_id VARCHAR(100) NOT NULL,
            changes TEXT,
            ip_address VARCHAR(50),
            user_agent VARCHAR(500),
            timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES organizations(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_audit_logs_timestamp ON audit_logs(timestamp)")
    
    # ============================================================================
    # 5. POLICIES
    # ============================================================================
    print("Creating policies table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS policies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER NOT NULL,
            policy_id VARCHAR(100) UNIQUE NOT NULL,
            title_en VARCHAR(500) NOT NULL,
            title_ar VARCHAR(500),
            description_en TEXT,
            description_ar TEXT,
            version VARCHAR(20) NOT NULL,
            status VARCHAR(50) NOT NULL,
            policy_type VARCHAR(100),
            owner_id INTEGER,
            approver_id INTEGER,
            effective_date DATE,
            review_date DATE,
            document_url VARCHAR(500),
            mapped_controls TEXT,
            attestation_required BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            approved_at TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES organizations(id),
            FOREIGN KEY (owner_id) REFERENCES users(id),
            FOREIGN KEY (approver_id) REFERENCES users(id)
        )
    """)
    
    # ============================================================================
    # 6. EVIDENCE TEMPLATES
    # ============================================================================
    print("Creating evidence_templates table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evidence_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER,
            template_id VARCHAR(100) UNIQUE NOT NULL,
            name_en VARCHAR(255) NOT NULL,
            name_ar VARCHAR(255),
            description_en TEXT,
            description_ar TEXT,
            evidence_type VARCHAR(100) NOT NULL,
            required_fields TEXT,
            validity_period_days INTEGER,
            is_reusable BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES organizations(id)
        )
    """)
    
    # ============================================================================
    # 7. EVIDENCES
    # ============================================================================
    print("Creating evidences table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evidences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER NOT NULL,
            evidence_id VARCHAR(100) UNIQUE NOT NULL,
            template_id INTEGER,
            control_id INTEGER,
            title_en VARCHAR(500) NOT NULL,
            title_ar VARCHAR(500),
            description_en TEXT,
            description_ar TEXT,
            file_path VARCHAR(500),
            file_type VARCHAR(50),
            file_size_bytes INTEGER,
            file_hash VARCHAR(128),
            version VARCHAR(20),
            previous_version_id INTEGER,
            status VARCHAR(50) NOT NULL,
            validity_start_date DATE,
            validity_end_date DATE,
            is_expired BOOLEAN DEFAULT 0,
            uploaded_by_id INTEGER NOT NULL,
            reviewed_by_id INTEGER,
            approved_by_id INTEGER,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reviewed_at TIMESTAMP,
            approved_at TIMESTAMP,
            tags TEXT,
            metadata TEXT,
            FOREIGN KEY (organization_id) REFERENCES organizations(id),
            FOREIGN KEY (control_id) REFERENCES controls(id),
            FOREIGN KEY (template_id) REFERENCES evidence_templates(id),
            FOREIGN KEY (previous_version_id) REFERENCES evidences(id),
            FOREIGN KEY (uploaded_by_id) REFERENCES users(id),
            FOREIGN KEY (reviewed_by_id) REFERENCES users(id),
            FOREIGN KEY (approved_by_id) REFERENCES users(id)
        )
    """)
    
    # ============================================================================
    # 8. RISKS
    # ============================================================================
    print("Creating risks table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS risks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER NOT NULL,
risk_id VARCHAR(100) UNIQUE NOT NULL,
            risk_type VARCHAR(50) NOT NULL,
            risk_category VARCHAR(100),
            title_en VARCHAR(500) NOT NULL,
            title_ar VARCHAR(500),
            description_en TEXT NOT NULL,
            description_ar TEXT,
            likelihood_inherent INTEGER NOT NULL,
            impact_inherent INTEGER NOT NULL,
            risk_score_inherent REAL,
            risk_level_inherent VARCHAR(20),
            likelihood_residual INTEGER,
            impact_residual INTEGER,
            risk_score_residual REAL,
            risk_level_residual VARCHAR(20),
            risk_appetite_level VARCHAR(20),
            is_within_appetite BOOLEAN,
            risk_owner_id INTEGER NOT NULL,
            mitigation_strategy TEXT,
            mitigation_controls TEXT,
            action_plan TEXT,
            status VARCHAR(50) DEFAULT 'open',
            review_frequency_days INTEGER DEFAULT 90,
            last_review_date DATE,
            next_review_date DATE,
            related_assets TEXT,
            related_risks TEXT,
            related_incidents TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by_id INTEGER,
            FOREIGN KEY (organization_id) REFERENCES organizations(id),
            FOREIGN KEY (risk_owner_id) REFERENCES users(id),
            FOREIGN KEY (created_by_id) REFERENCES users(id)
        )
    """)
    
    # ============================================================================
    # 9. AUDIT PROGRAMS
    # ============================================================================
    print("Creating audit_programs table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_programs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER NOT NULL,
            program_id VARCHAR(100) UNIQUE NOT NULL,
            title_en VARCHAR(500) NOT NULL,
            title_ar VARCHAR(500),
            audit_type VARCHAR(50) NOT NULL,
            framework VARCHAR(50),
            scope_description TEXT,
            planned_start_date DATE,
            planned_end_date DATE,
            actual_start_date DATE,
            actual_end_date DATE,
            lead_auditor_id INTEGER,
            status VARCHAR(50) DEFAULT 'planned',
            controls_in_scope TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES organizations(id),
            FOREIGN KEY (lead_auditor_id) REFERENCES users(id)
        )
    """)
    
    # ============================================================================
    # 10. AUDIT FINDINGS
    # ============================================================================
    print("Creating audit_findings table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_findings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER NOT NULL,
            finding_id VARCHAR(100) UNIQUE NOT NULL,
            audit_program_id INTEGER,
            control_id INTEGER,
            title_en VARCHAR(500) NOT NULL,
            title_ar VARCHAR(500),
            description_en TEXT NOT NULL,
            description_ar TEXT,
            severity VARCHAR(20) NOT NULL,
            risk_rating VARCHAR(20),
            remediation_plan_en TEXT,
            remediation_plan_ar TEXT,
            remediation_owner_id INTEGER,
            target_closure_date DATE,
            actual_closure_date DATE,
            is_overdue BOOLEAN DEFAULT 0,
            status VARCHAR(20) DEFAULT 'open',
            verification_evidence_ids TEXT,
            verified_by_id INTEGER,
            verified_at TIMESTAMP,
            identified_by_id INTEGER,
            identified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES organizations(id),
            FOREIGN KEY (audit_program_id) REFERENCES audit_programs(id),
            FOREIGN KEY (control_id) REFERENCES controls(id),
            FOREIGN KEY (remediation_owner_id) REFERENCES users(id),
            FOREIGN KEY (verified_by_id) REFERENCES users(id),
            FOREIGN KEY (identified_by_id) REFERENCES users(id)
        )
    """)
    
    # ============================================================================
    # 11. CONTROL ASSESSMENTS
    # ============================================================================
    print("Creating control_assessments table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS control_assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER NOT NULL,
            control_id INTEGER NOT NULL,
            assessment_date DATE NOT NULL,
            assessor_id INTEGER NOT NULL,
            test_result VARCHAR(20) NOT NULL,
            maturity_score VARCHAR(30),
            effectiveness_score REAL,
            findings_summary_en TEXT,
            findings_summary_ar TEXT,
            gaps_identified TEXT,
            recommendations_en TEXT,
            recommendations_ar TEXT,
            evidence_sufficient BOOLEAN,
            attached_evidence_ids TEXT,
            status VARCHAR(50) DEFAULT 'draft',
            approved_by_id INTEGER,
            approved_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES organizations(id),
            FOREIGN KEY (control_id) REFERENCES controls(id),
            FOREIGN KEY (assessor_id) REFERENCES users(id),
            FOREIGN KEY (approved_by_id) REFERENCES users(id)
        )
    """)
    
    # ============================================================================
    # 12. CONTROL EXCEPTIONS
    # ============================================================================
    print("Creating control_exceptions table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS control_exceptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER NOT NULL,
            exception_id VARCHAR(100) UNIQUE NOT NULL,
            control_id INTEGER NOT NULL,
            justification_en TEXT NOT NULL,
            justification_ar TEXT,
            risk_acceptance_statement TEXT,
            compensating_controls TEXT,
            requested_by_id INTEGER NOT NULL,
            approved_by_id INTEGER,
            approval_date DATE,
            effective_date DATE NOT NULL,
            expiry_date DATE NOT NULL,
            is_expired BOOLEAN DEFAULT 0,
            renewal_required BOOLEAN DEFAULT 1,
            status VARCHAR(50) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES organizations(id),
            FOREIGN KEY (control_id) REFERENCES controls(id),
            FOREIGN KEY (requested_by_id) REFERENCES users(id),
            FOREIGN KEY (approved_by_id) REFERENCES users(id)
        )
    """)
    
    # ============================================================================
    # 13. WORKFLOW CASES
    # ============================================================================
    print("Creating workflow_cases table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workflow_cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER NOT NULL,
            case_id VARCHAR(100) UNIQUE NOT NULL,
            case_type VARCHAR(50) NOT NULL,
            title_en VARCHAR(500) NOT NULL,
            title_ar VARCHAR(500),
            description_en TEXT,
            description_ar TEXT,
            priority VARCHAR(20),
            assigned_to_id INTEGER,
            assigned_by_id INTEGER,
            assigned_at TIMESTAMP,
            sla_hours INTEGER,
            due_date TIMESTAMP,
            is_overdue BOOLEAN DEFAULT 0,
            escalation_level INTEGER DEFAULT 0,
            escalated_to_id INTEGER,
            status VARCHAR(20) DEFAULT 'open',
            resolution_notes TEXT,
            resolved_at TIMESTAMP,
            closed_at TIMESTAMP,
            related_entity_type VARCHAR(50),
            related_entity_id INTEGER,
            attachments TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES organizations(id),
            FOREIGN KEY (assigned_to_id) REFERENCES users(id),
            FOREIGN KEY (assigned_by_id) REFERENCES users(id),
            FOREIGN KEY (escalated_to_id) REFERENCES users(id)
        )
    """)
    
    # ============================================================================
    # 14. VENDORS
    # ============================================================================
    print("Creating vendors table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER NOT NULL,
            vendor_id VARCHAR(100) UNIQUE NOT NULL,
            name_en VARCHAR(255) NOT NULL,
            name_ar VARCHAR(255),
            vendor_type VARCHAR(100),
            criticality VARCHAR(20) NOT NULL,
            contact_person VARCHAR(255),
            contact_email VARCHAR(255),
            contact_phone VARCHAR(50),
            last_assessment_date DATE,
            next_assessment_date DATE,
            risk_score REAL,
            risk_level VARCHAR(20),
            is_data_processor BOOLEAN DEFAULT 0,
            dpa_signed BOOLEAN DEFAULT 0,
            dpa_expiry_date DATE,
            data_transfer_countries TEXT,
            contract_start_date DATE,
            contract_end_date DATE,
            contract_value REAL,
            status VARCHAR(50) DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES organizations(id)
        )
    """)
    
    # ============================================================================
    # 15. ROPA (PDPL)
    # ============================================================================
    print("Creating ropa_records table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ropa_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER NOT NULL,
            ropa_id VARCHAR(100) UNIQUE NOT NULL,
            activity_name_en VARCHAR(500) NOT NULL,
            activity_name_ar VARCHAR(500),
            purpose_en TEXT NOT NULL,
            purpose_ar TEXT,
            legal_basis VARCHAR(100) NOT NULL,
            data_categories TEXT,
            data_subjects TEXT,
            retention_period VARCHAR(100),
            international_transfers BOOLEAN DEFAULT 0,
            transfer_countries TEXT,
            transfer_safeguards TEXT,
            data_recipients TEXT,
            processors TEXT,
            security_measures TEXT,
            dpia_required BOOLEAN DEFAULT 0,
            dpia_completed BOOLEAN DEFAULT 0,
            dpia_reference VARCHAR(100),
            data_controller_id INTEGER,
            dpo_id INTEGER,
            status VARCHAR(50) DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES organizations(id),
            FOREIGN KEY (data_controller_id) REFERENCES users(id),
            FOREIGN KEY (dpo_id) REFERENCES users(id)
        )
    """)
    
    # ============================================================================
    # 16. DSAR (PDPL)
    # ============================================================================
    print("Creating dsar_requests table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dsar_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER NOT NULL,
            request_id VARCHAR(100) UNIQUE NOT NULL,
            request_type VARCHAR(50) NOT NULL,
            subject_name VARCHAR(255) NOT NULL,
            subject_email VARCHAR(255),
            subject_phone VARCHAR(50),
            identity_verified BOOLEAN DEFAULT 0,
            request_description TEXT,
            received_date DATE NOT NULL,
            sla_days INTEGER DEFAULT 30,
            due_date DATE NOT NULL,
            is_overdue BOOLEAN DEFAULT 0,
            assigned_to_id INTEGER,
            response_provided TEXT,
            response_date DATE,
            status VARCHAR(20) DEFAULT 'open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES organizations(id),
            FOREIGN KEY (assigned_to_id) REFERENCES users(id)
        )
    """)
    
    # ============================================================================
    # 17. DATA BREACHES (PDPL)
    # ============================================================================
    print("Creating data_breaches table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS data_breaches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER NOT NULL,
            breach_id VARCHAR(100) UNIQUE NOT NULL,
            breach_date TIMESTAMP NOT NULL,
            discovery_date TIMESTAMP NOT NULL,
            breach_type VARCHAR(100),
            description_en TEXT NOT NULL,
            description_ar TEXT,
            affected_data_subjects_count INTEGER,
            data_categories_affected TEXT,
            severity VARCHAR(20) NOT NULL,
            sdaia_notified BOOLEAN DEFAULT 0,
            sdaia_notification_date TIMESTAMP,
            subjects_notified BOOLEAN DEFAULT 0,
            notification_method VARCHAR(100),
            containment_measures TEXT,
            remediation_plan TEXT,
            lessons_learned TEXT,
            status VARCHAR(50) DEFAULT 'open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES organizations(id)
        )
    """)
    
    # ============================================================================
    # 18. INTEGRATIONS
    # ============================================================================
    print("Creating integrations table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS integrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER NOT NULL,
            integration_name VARCHAR(100) NOT NULL,
            integration_type VARCHAR(50),
            endpoint_url VARCHAR(500),
            api_key_encrypted VARCHAR(500),
            is_active BOOLEAN DEFAULT 1,
            last_sync_at TIMESTAMP,
            sync_frequency_minutes INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES organizations(id)
        )
    """)
    
    # ============================================================================
    # 19. AUTOMATED EVIDENCES
    # ============================================================================
    print("Creating automated_evidences table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS automated_evidences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER NOT NULL,
            control_id INTEGER NOT NULL,
            integration_id INTEGER,
            evidence_rule TEXT,
            collection_frequency VARCHAR(50),
            last_collected_at TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES organizations(id),
            FOREIGN KEY (control_id) REFERENCES controls(id),
            FOREIGN KEY (integration_id) REFERENCES integrations(id)
        )
    """)
    
    # ============================================================================
    # 20. COMPLIANCE METRICS
    # ============================================================================
    print("Creating compliance_metrics table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS compliance_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER NOT NULL,
            metric_date DATE NOT NULL,
            framework VARCHAR(50),
            total_controls INTEGER,
            compliant_controls INTEGER,
            partial_controls INTEGER,
            non_compliant_controls INTEGER,
            compliance_percentage REAL,
            total_risks INTEGER,
            critical_risks INTEGER,
            high_risks INTEGER,
            risks_within_appetite INTEGER,
            open_findings INTEGER,
            overdue_findings INTEGER,
            avg_remediation_days REAL,
            evidence_sufficiency_score REAL,
            expired_evidences INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES organizations(id)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_compliance_metrics_metric_date ON compliance_metrics(metric_date)")
    
    conn.commit()
    conn.close()
    
    print(" ✅ Enterprise GRC Database Created Successfully!")
    print(f"📊 20+ enterprise tables created at: {DB_PATH}")
    print("🔒 Multi-tenancy, RBAC, Full audit trail enabled")
    print("🎯 ServiceNow GRC / RSA Archer equivalent schema ready")
    
if __name__ == "__main__":
    create_enterprise_database()
