"""
Enterprise GRC Platform - Sample Data Loader
Populates database with realistic Tier-1 enterprise data
"""

import sqlite3
import json
from datetime import datetime, timedelta, date
from pathlib import Path

DB_PATH = Path(__file__).parent / "sico_dev.db"

def load_enterprise_sample_data():
    """Load comprehensive enterprise sample data"""
    
    print("🚀 Loading enterprise sample data...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn. cursor()
    
    # ============================================================================
    # 1. ORGANIZATIONS (Multi-tenant structure)
    # ============================================================================
    print("📊 Creating organizations...")
    
    # Main organization
    cursor.execute("""
        INSERT INTO organizations (id, name_en, name_ar, org_type, license_type, is_active)
        VALUES (1, 'Saudi Investment Corporation', 'المؤسسة السعودية للاستثمار', 'group', 'enterprise', 1)
    """)
    
    # Business units
    cursor.execute("""
        INSERT INTO organizations (id, name_en, name_ar, org_type, parent_org_id, license_type, is_active)
        VALUES 
        (2, 'Corporate Banking Division', 'قطاع الخدمات المصرفية للشركات', 'business_unit', 1, 'enterprise', 1),
        (3, 'Retail Banking Division', 'قطاع الخدمات المصرفية للأفراد', 'business_unit', 1, 'enterprise', 1),
        (4, 'Information Technology', 'تقنية المعلومات', 'business_unit', 1, 'enterprise', 1),
        (5, 'Compliance & Risk Management', 'الامتثال وإدارة المخاطر', 'business_unit', 1, 'enterprise', 1)
    """)
    
    # ============================================================================
    # 2. USERS (8 RBAC roles)
    # ============================================================================
    print("👥 Creating users with RBAC...")
    
    users = [
        (1, 1, 'admin', 'admin@sico.sa', 'System Administrator', 'مدير النظام', 'admin'),
        (2, 1, 'compliance_owner', 'compliance@sico.sa', 'Compliance Director', 'مدير الامتثال', 'compliance_owner'),
        (3, 1, 'control_owner', 'controls@sico.sa', 'Control Owner', 'مسؤول الضوابط', 'control_owner'),
        (4, 1, 'risk_owner', 'risk@sico.sa', 'Risk Manager', 'مدير المخاطر', 'risk_owner'),
        (5, 1, 'auditor', 'auditor@sico.sa', 'Internal Auditor', 'مدقق داخلي', 'auditor'),
        (6, 1, 'soc_analyst', 'soc@sico.sa', 'SOC Analyst', 'محلل مركز العمليات الأمنية', 'soc_analyst'),
        (7, 1, 'executive', 'ceo@sico.sa', 'Chief Executive Officer', 'الرئيس التنفيذي', 'executive'),
        (8, 1, 'dpo', 'dpo@sico.sa', 'Data Protection Officer', 'مسؤول حماية البيانات', 'compliance_owner')
    ]
    
    cursor.executemany("""
        INSERT INTO users (id, organization_id, username, email, full_name_en, full_name_ar, role, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, 1)
    """, users)
    
    # ============================================================================
    # 3. ASSETS (Critical IT infrastructure)
    # ============================================================================
    print("💻 Creating assets...")
    
    assets = [
        (1, 1, 'ASSET-001', 'application', 'Core Banking System', 'نظام البنوك الأساسي', 'Core banking application', 'critical', 'confidential', 3, 'Data Center - Riyadh', 'production'),
        (2, 1, 'ASSET-002', 'database', 'Customer Database', 'قاعدة بيانات العملاء', 'Primary customer data repository', 'critical', 'restricted', 4, 'Data Center - Riyadh', 'production'),
        (3, 1, 'ASSET-003', 'cloud_service', 'Azure Cloud Platform', 'منصة أزور السحابية', 'Cloud infrastructure', 'high', 'internal', 4, 'Azure - Middle East', 'production'),
        (4, 1, 'ASSET-004', 'application', 'Mobile Banking App', 'تطبيق الخدمات المصرفية', 'Customer mobile application', 'high', 'public', 3, 'App Stores', 'production'),
        (5, 1, 'ASSET-005', 'server', 'Active Directory Server', 'خادم الدليل النشط', 'Identity management server', 'critical', 'internal', 4, 'Data Center - Riyadh', 'production')
    ]
    
    cursor.executemany("""
        INSERT INTO assets (id, organization_id, asset_id, asset_type, name_en, name_ar, description_en, criticality, classification, owner_id, location, environment, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
    """, assets)
    
    # ============================================================================
    # 4. POLICIES
    # ============================================================================
    print("📜 Creating policies...")
    
    cursor.execute("""
        INSERT INTO policies (id, organization_id, policy_id, title_en, title_ar, description_en, version, status, policy_type, owner_id, effective_date, review_date, mapped_controls)
        VALUES 
        (1, 1, 'POL-SEC-001', 'Information Security Policy', 'سياسة أمن المعلومات', 'Enterprise information security policy', '2.0', 'approved', 'security', 2, '2024-01-01', '2025-01-01', '["ECC-GV-1-1","ECC-IS-1-1"]'),
        (2, 1, 'POL-PDPL-001', 'Personal Data Protection Policy', 'سياسة حماية البيانات الشخصية', 'PDPL compliance policy', '1.0', 'approved', 'privacy', 8, '2024-01-01', '2025-01-01', '["PDPL-1","PDPL-2"]'),
        (3, 1, 'POL-ACCESS-001', 'Access Control Policy', 'سياسة التحكم في الوصول', 'User access management policy', '3.0', 'approved', 'security', 2, '2024-01-01', '2025-01-01', '["ECC-IS-2-1"]')
    """)
    
    # ============================================================================
    # 5. RISKS (Enterprise Risk Management)
    # ============================================================================
    print("⚠️ Creating risks...")
    
    cursor.execute("""
        INSERT INTO risks (id, organization_id, risk_id, risk_type, risk_category, title_en, description_en, title_ar, description_ar,
                          likelihood_inherent, impact_inherent, risk_score_inherent, risk_level_inherent,
                          likelihood_residual, impact_residual, risk_score_residual, risk_level_residual,
                          risk_appetite_level, risk_owner_id, mitigation_strategy, mitigation_controls, status)
        VALUES 
        (1, 1, 'RISK-001', 'cyber', 'Security Threats', 'Unauthorized access to banking system', 'وصول غير مصرح إلى النظام المصرفي', 'تهديدات أمنية', 'Unauthorized access to banking system',
         4, 5, 20.0, 'critical', 3, 4, 12.0, 'high', 'high', 4, 'Implement MFA and enhanced monitoring', '["ECC-IS-2-1"]', 'open'),
        
        (2, 1, 'RISK-002', 'compliance', 'PDPL Non-Compliance', 'Failure to comply with PDPL requirements', 'عدم الامتثال لمتطلبات نظام حماية البيانات', 'عدم الامتثال لنظام حماية البيانات', 'Failure to comply with PDPL requirements',
         3, 5, 15.0, 'high', 2, 3, 6.0, 'medium', 'medium', 2, 'Implement data protection measures', '["PDPL-1","PDPL-2"]', 'open'),
        
        (3, 1, 'RISK-003', 'operational', 'System Downtime', 'Core banking system outage',  'توقف نظام البنوك الأساسي', 'تعطل النظام', 'Core banking system outage',
         2, 5, 10.0, 'high', 1, 3, 3.0, 'low', 'low', 4, 'Implement HA/DR solutions', '["ECC-RM-1-1"]', 'open')
    """)
    
    # ============================================================================
    # 6. AUDIT PROGRAMS
    # ============================================================================
    print("🔍 Creating audit programs...")
    
    cursor.execute("""
        INSERT INTO audit_programs (id, organization_id, program_id, title_en, title_ar, audit_type, framework, 
                                   planned_start_date, planned_end_date, lead_auditor_id, status, controls_in_scope)
        VALUES 
        (1, 1, 'AUDIT-2024-Q1', 'Q1 2024 ECC Compliance Audit', 'مراجعة الامتثال للضوابط الأساسية للأمن السيبراني للربع الأول 2024', 
         'internal', 'ECC', '2024-01-01', '2024-03-31', 5, 'in_progress', '["ECC-GV-1-1","ECC-IS-1-1","ECC-IS-2-1"]'),
        
        (2, 1, 'AUDIT-2024-PDPL', 'PDPL Compliance Assessment', 'تقييم الامتثال لنظام حماية البيانات الشخصية', 
         'external', 'PDPL', '2024-02-01', '2024-04-30', 5, 'planned', '["PDPL-1","PDPL-2","PDPL-3"]')
    """)
    
    # ============================================================================
    # 7. AUDIT FINDINGS
    # ============================================================================
    print("📋 Creating audit findings...")
    
    cursor.execute("""
        INSERT INTO audit_findings (id, organization_id, finding_id, audit_program_id, title_en, title_ar, 
                                   description_en, severity, risk_rating, remediation_owner_id, target_closure_date, status)
        VALUES 
        (1, 1, 'FIND-001', 1, 'Weak Password Policy', 'سياسة كلمات المرور الضعيفة', 
         'Current password policy does not enforce complexity requirements', 'high', 'high', 3, '2024-03-31', 'open'),
        
        (2, 1, 'FIND-002', 1, 'Missing MFA Implementation', 'عدم تطبيق المصادقة متعددة العوامل', 
         'Multi-factor authentication not implemented for privileged accounts', 'critical', 'critical', 4, '2024-02-28', 'in_progress')
    """)
    
    # ============================================================================
    # 8. WORKFLOW CASES
    # ============================================================================
    print("⚙️ Creating workflow cases...")
    
    cursor.execute("""
        INSERT INTO workflow_cases (id, organization_id, case_id, case_type, title_en, title_ar, priority, 
                                   assigned_to_id, sla_hours, due_date, status)
        VALUES 
        (1, 1, 'CASE-001', 'audit_finding', 'Remediate Password Policy Finding', 'معالجة اكتشاف سياسة كلمات المرور', 
         'high', 3, 720, '2024-03-31 23:59:59', 'in_progress'),
        
        (2, 1, 'CASE-002', 'evidence_request', 'Collect MFA Implementation Evidence', 'جمع أدلة تطبيق المصادقة متعددة العوامل', 
         'critical', 4, 168, '2024-02-15 23:59:59', 'open')
    """)
    
    # ============================================================================
    # 9. VENDORS (Third-party risk)
    # ============================================================================
    print("🤝 Creating vendors...")
    
    cursor.execute("""
        INSERT INTO vendors (id, organization_id, vendor_id, name_en, name_ar, vendor_type, criticality, 
                           contact_email, risk_score, risk_level, is_data_processor, dpa_signed, status)
        VALUES 
        (1, 1, 'VENDOR-001', 'Cloud Services Provider', 'مزود الخدمات السحابية', 'technology', 'critical', 
         'support@cloudprovider.com', 75.0, 'medium', 1, 1, 'active'),
        
        (2, 1, 'VENDOR-002', 'External Auditor', 'مدقق خارجي', 'consulting', 'high', 
         'audit@external.com', 40.0, 'low', 0, 0, 'active')
    """)
    
    # ============================================================================
    # 10. PDPL - RoPA RECORDS
    # ============================================================================
    print("🔒 Creating RoPA records...")
    
    cursor.execute("""
        INSERT INTO ropa_records (id, organization_id, ropa_id, activity_name_en, activity_name_ar, 
                                 purpose_en, purpose_ar, legal_basis, data_categories, data_subjects, 
                                 retention_period, data_controller_id, dpo_id, status)
        VALUES 
        (1, 1, 'ROPA-001', 'Customer Account Management', 'إدارة حسابات العملاء', 
         'Managing customer banking accounts and transactions', 'إدارة حسابات العملاء المصرفية والمعاملات', 
         'contract', '["personal","financial"]', '["customers"]', '7 years', 2, 8, 'active'),
        
        (2, 1, 'ROPA-002', 'Employee HR Records', 'سجلات الموارد البشرية للموظفين', 
         'Managing employee personal and employment data', 'إدارة البيانات الشخصية والوظيفية للموظفين', 
         'legal_obligation', '["personal","employment"]', '["employees"]', '10 years', 2, 8, 'active')
    """)
    
    # ============================================================================
    # 11. PDPL - DSAR REQUESTS
    # ============================================================================
    print("📨 Creating DSAR requests...")
    
    today = date.today()
    due_date = today + timedelta(days=30)
    
    cursor.execute("""
        INSERT INTO dsar_requests (id, organization_id, request_id, request_type, subject_name, subject_email, 
                                  received_date, sla_days, due_date, assigned_to_id, status)
        VALUES 
        (1, 1, 'DSAR-001', 'access', 'Ahmed Al-Otaibi', 'ahmed@example.com', 
         '2024-02-01', 30, '2024-03-02', 8, 'in_progress'),
        
        (2, 1, 'DSAR-002', 'erasure', 'Fatima Al-Harbi', 'fatima@example.com', 
         '2024-02-05', 30, '2024-03-06', 8, 'open')
    """)
    
    # ============================================================================
    # 12. PDPL - DATA BREACHES
    # ============================================================================
    print("🚨 Creating data breach records...")
    
    cursor.execute("""
        INSERT INTO data_breaches (id, organization_id, breach_id, breach_date, discovery_date, breach_type, 
                                  description_en, description_ar, affected_data_subjects_count, severity, 
                                  sdaia_notified, status)
        VALUES 
        (1, 1, 'BREACH-2024-001', '2024-01-15 10:00:00', '2024-01-15 14:00:00', 'unauthorized_access', 
         'Unauthorized access to customer email addresses via compromised employee account', 
         'وصول غير مصرح به إلى عناوين البريد الإلكتروني للعملاء عبر حساب موظف مخترق', 
         150, 'medium', 1, 'closed')
    """)
    
    # ============================================================================
    # 13. INTEGRATIONS
    # ============================================================================
    print("🔗 Creating integrations...")
    
    cursor.execute("""
        INSERT INTO integrations (id, organization_id, integration_name, integration_type, endpoint_url, is_active, sync_frequency_minutes)
        VALUES 
        (1, 1, 'Microsoft Sentinel SIEM', 'siem', 'https://sentinel.azure.com/api', 1, 15),
        (2, 1, 'Azure Active Directory', 'iam', 'https://graph.microsoft.com/v1.0', 1, 30),
        (3, 1, 'ServiceNow ITSM', 'itsm', 'https://company.service-now.com/api', 1, 60)
    """)
    
    # ============================================================================
    # 14. COMPLIANCE METRICS
    # ============================================================================
    print("📈 Creating compliance metrics...")
    
    cursor.execute("""
        INSERT INTO compliance_metrics (id, organization_id, metric_date, framework, total_controls, 
                                       compliant_controls, partial_controls, non_compliant_controls, 
                                       compliance_percentage, total_risks, critical_risks, high_risks, 
                                       open_findings, overdue_findings)
        VALUES 
        (1, 1, '2024-02-01', 'ECC', 114, 89, 15, 10, 78.07, 12, 2, 5, 8, 2),
        (2, 1, '2024-02-01', 'CCC', 85, 70, 10, 5, 82.35, 8, 1, 3, 5, 1),
        (3, 1, '2024-02-01', 'PDPL', 46, 38, 6, 2, 82.61, 5, 0, 2, 3, 0)
    """)
    
    # ============================================================================
    # 15. EVIDENCE TEMPLATES
    # ============================================================================
    print("📎 Creating evidence templates...")
    
    cursor.execute("""
        INSERT INTO evidence_templates (id, organization_id, template_id, name_en, name_ar, 
                                       evidence_type, validity_period_days, is_reusable)
        VALUES 
        (1, 1, 'TMPL-POL', 'Policy Document', 'وثيقة السياسة', 'policy', 365, 1),
        (2, 1, 'TMPL-CERT', 'Security Certificate', 'شهادة أمنية', 'certificate', 365, 1),
        (3, 1, 'TMPL-LOG', 'System Log', 'سجل النظام', 'log', 30, 0),
        (4, 1, 'TMPL-SCREEN', 'Screenshot Evidence', 'لقطة شاشة كدليل', 'screenshot', 90, 0)
    """)
    
    # ============================================================================
    # 16. EVIDENCES
    # ============================================================================
    print("📄 Creating evidence records...")
    
    cursor.execute("""
        INSERT INTO evidences (id, organization_id, evidence_id, template_id, title_en, title_ar, 
                             description_en, status, validity_start_date, validity_end_date, uploaded_by_id)
        VALUES 
        (1, 1, 'EVID-001', 1, 'Information Security Policy v2.0', 'سياسة أمن المعلومات الإصدار 2.0', 
         'Approved information security policy document', 'approved', '2024-01-01', '2025-01-01', 2),
        
        (2, 1, 'EVID-002', 2, 'ISO 27001 Certificate', 'شهادة ISO 27001', 
         'ISO 27001:2022 certification', 'approved', '2024-01-01', '2025-01-01', 2),
        
        (3, 1, 'EVID-003', 3, 'Access Control Logs - January 2024', 'سجلات التحكم في الوصول - يناير 2024', 
         'System access logs for January 2024', 'approved', '2024-01-01', '2024-01-31', 4)
    """)
    
    # ============================================================================
    # 17. CONTROL ASSESSMENTS
    # ============================================================================
    print("✅ Creating control assessments...")
    
    cursor.execute("""
        INSERT INTO control_assessments (id, organization_id, control_id, assessment_date, assessor_id, 
                                        test_result, effectiveness_score, evidence_sufficient, status)
        VALUES 
        (1, 1, 1, '2024-02-01', 5, 'pass', 85.0, 1, 'approved'),
        (2, 1, 2, '2024-02-01', 5, 'partial', 65.0, 0, 'approved'),
        (3, 1, 3, '2024-02-01', 5, 'fail', 35.0, 0, 'approved')
    """)
    
    conn.commit()
    conn.close()
    
    print("\n✅ Enterprise sample data loaded successfully!")
    print("📊 Summary:")
    print("   - 5 Organizations (multi-tenant hierarchy)")
    print("   - 8 Users (8 RBAC roles)")
    print("   - 5 Critical Assets")
    print("   - 3 Policies")
    print("   - 3 Enterprise Risks")
    print("   - 2 Audit Programs")
    print("   - 2 Audit Findings")
    print("   - 2 Workflow Cases")
    print("   - 2 Vendors")
    print("   - 2 RoPA Records (PDPL)")
    print("   - 2 DSAR Requests (PDPL)")
    print("   - 1 Data Breach (PDPL)")
    print("   - 3 System Integrations")
    print("   - 3 Compliance Metrics")
    print("   - 4 Evidence Templates")
    print("   - 3 Evidence Records")
    print("   - 3 Control Assessments")
    print("\n🎯 Ready for Tier-1 Enterprise GRC Operations!")

if __name__ == "__main__":
    load_enterprise_sample_data()
