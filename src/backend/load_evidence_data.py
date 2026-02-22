"""
SICO GRC - Evidence Data Loader
Creates comprehensive evidence records linked to controls
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "sico_grc.db"

def load_evidence_data():
    """Load comprehensive evidence records"""
    
    print("📄 Loading Evidence Records...")
    print("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get some control IDs to link evidence to
    cursor.execute("SELECT control_id FROM controls LIMIT 20")
    control_ids = [row[0] for row in cursor.fetchall()]
    
    evidence_records = [
        # ECC Evidence
        {
            "evidence_id": "EV-2024-001",
            "title_en": "Information Security Policy Document",
            "title_ar": "وثيقة سياسة أمن المعلومات",
            "description_en": "Approved information security policy covering all ECC requirements",
            "description_ar": "سياسة أمن المعلومات المعتمدة التي تغطي جميع متطلبات الضوابط الأساسية",
            "file_type": "pdf",
            "control_id": control_ids[0] if control_ids else 1,
            "status": "Approved",
            "file_path":"/evidence/policies/info_sec_policy_2024.pdf",
            "file_size_bytes": 1048576,
            "validity_start_date": "2024-01-15",
            "validity_end_date": "2025-01-15",
            "version": "2.0"
        },
        {
            "evidence_id": "EV-2024-002",
            "title_en": "Access Control Logs - January 2024",
            "title_ar": "سجلات التحكم في الوصول - يناير 2024",
            "description_en": "System access logs showing user authentication and authorization",
            "description_ar": "سجلات وصول النظام توضح مصادقة المستخدم والتفويض",
            "file_type": "zip",
            "control_id": control_ids[1] if len(control_ids) > 1 else 1,
            "status": "Approved",
            "file_path": "/evidence/logs/access_logs_jan2024.zip",
            "file_size_bytes": 52428800,
            "validity_start_date": "2024-02-01",
            "version": "1.0"
        },
        {
            "evidence_id": "EV-2024-003",
            "title_en": "MFA Implementation Screenshots",
            "title_ar": "لقطات شاشة تطبيق المصادقة متعددة العوامل",
            "description_en": "Screenshots demonstrating MFA enabled for privileged accounts",
            "description_ar": "لقطات شاشة توضح تمكين المصادقة متعددة العوامل للحسابات المميزة",
            "file_type": "png",
            "control_id": control_ids[2] if len(control_ids) > 2 else 1,
            "status": "Under Review",
            "file_path": "/evidence/screenshots/mfa_config.png",
            "file_size_bytes": 2097152,
            "validity_start_date": "2024-02-10",
            "version": "1.0"
        },
        {
            "evidence_id": "EV-2024-004",
            "title_en": "Incident Response Plan",
            "title_ar": "خطة الاستجابة للحوادث",
            "description_en": "Documented incident response procedures and contact list",
            "description_ar": "إجراءات الاستجابة للحوادث الموثقة وقائمة جهات الاتصال",
            "file_type": "pdf",
            "control_id": control_ids[3] if len(control_ids) > 3 else 1,
            "status": "Approved",
            "file_path": "/evidence/procedures/incident_response_plan.pdf",
            "file_size_bytes": 3145728,
            "validity_start_date": "2024-01-20",
            "validity_end_date": "2025-01-20",
            "version": "1.5"
        },
        {
            "evidence_id": "EV-2024-005",
            "title_en": "Vulnerability Scan Report - February 2024",
            "title_ar": "تقرير فحص الثغرات - فبراير 2024",
            "description_en": "Monthly vulnerability scan results from Qualys scanner",
            "description_ar": "نتائج فحص الثغرات الشهري من أداة Qualys",
            "file_type": "pdf",
            "control_id": control_ids[4] if len(control_ids) > 4 else 1,
            "status": "Approved",
            "file_path": "/evidence/reports/vuln_scan_feb2024.pdf",
            "file_size_bytes": 4194304,
            "validity_start_date": "2024-02-15",
            "version": "1.0"
        },
        {
            "evidence_id": "EV-2024-006",
            "title_en": "Backup Test Results",
            "title_ar": "نتائج اختبار النسخ الاحتياطي",
            "description_en": "Quarterly backup and recovery test results",
            "description_ar": "نتائج اختبار النسخ الاحتياطي والاستعادة الربع سنوية",
            "file_type": "pdf",
            "control_id": control_ids[5] if len(control_ids) > 5 else 1,
            "status": "Approved",
            "file_path": "/evidence/test_results/backup_test_q1_2024.pdf",
            "file_size_bytes": 1572864,
            "validity_start_date": "2024-02-01",
            "version": "1.0"
        },
        {
            "evidence_id": "EV-2024-007",
            "title_en": "PDPL Data Processing Agreement",
            "title_ar": "اتفاقية معالجة البيانات PDPL",
            "description_en": "Data processing agreement with cloud service provider",
            "description_ar": "اتفاقية معالجة البيانات مع مزود الخدمات السحابية",
            "file_type": "pdf",
            "control_id": control_ids[6] if len(control_ids) > 6 else 1,
            "status": "Approved",
            "file_path": "/evidence/contracts/dpa_cloud_provider.pdf",
            "file_size_bytes": 524288,
            "validity_start_date": "2024-01-10",
            "validity_end_date": "2026-01-10",
            "version": "1.0"
        },
        {
            "evidence_id": "EV-2024-008",
            "title_en": "Security Awareness Training Completion Report",
            "title_ar": "تقرير إنجاز التدريب على التوعية الأمنية",
            "description_en": "Report showing 95% staff completion of mandatory security training",
            "description_ar": "تقرير يوضح إنجاز 95% من الموظفين للتدريب الأمني الإلزامي",
            "file_type": "pdf",
            "control_id": control_ids[7] if len(control_ids) > 7 else 1,
            "status": "Approved",
            "file_path": "/evidence/training/awareness_training_q1_2024.pdf",
            "file_size_bytes": 2097152,
            "validity_start_date": "2024-02-01",
            "version": "1.0"
        },
        {
            "evidence_id": "EV-2024-009",
            "title_en": "Penetration Test Report",
            "title_ar": "تقرير اختبار الاختراق",
            "description_en": "Annual penetration test report from external firm",
            "description_ar": "تقرير اختبار الاختراق السنوي من شركة خارجية",
            "file_type": "pdf",
            "control_id": control_ids[8] if len(control_ids) > 8 else 1,
            "status": "Approved",
            "file_path": "/evidence/reports/pentest_2024.pdf",
            "file_size_bytes": 8388608,
            "validity_start_date": "2024-01-30",
            "version": "1.0"
        },
        {
            "evidence_id": "EV-2024-010",
            "title_en": "Asset Inventory Spreadsheet",
            "title_ar": "جدول جرد الأصول",
            "description_en": "Complete inventory of IT assets with classification",
            "description_ar": "جرد كامل للأصول التقنية مع التصنيف",
            "file_type": "xlsx",
            "control_id": control_ids[9] if len(control_ids) > 9 else 1,
            "status": "Approved",
            "file_path": "/evidence/inventory/asset_inventory_feb2024.xlsx",
            "file_size_bytes": 262144,
            "validity_start_date": "2024-02-01",
            "version": "1.0"
        },
    ]
    
    for ev in evidence_records:
        cursor.execute("""
            INSERT INTO evidences (
                organization_id, evidence_id, control_id, title_en, title_ar, 
                description_en, description_ar, file_type, status,
                validity_start_date, validity_end_date, file_path, file_size_bytes, 
                version, uploaded_by_id
            ) VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 2)
        """, (
            ev["evidence_id"],
            ev["control_id"],
            ev["title_en"],
            ev["title_ar"],
            ev["description_en"],
            ev["description_ar"],
            ev["file_type"],
            ev["status"],
            ev["validity_start_date"],
            ev.get("validity_end_date"),
            ev["file_path"],
            ev["file_size_bytes"],
            ev["version"]
        ))
    
    conn.commit()
    conn.close()
    
    print(f"   ✓ Loaded {len(evidence_records)} evidence records")
    print("=" * 60)
    print("✅ Evidence Loading Complete!")

if __name__ == "__main__":
    load_evidence_data()
