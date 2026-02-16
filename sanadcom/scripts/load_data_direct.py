import sys
from pathlib import Path
from datetime import datetime, timedelta
import uuid
import sqlite3

# Direct SQLite connection for reliability
db_path = Path(__file__).parent.parent / "src" / "backend" / "sico_dev.db"

def load_controls():
    """Load comprehensive control library using direct SQLite"""
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    additional_controls = [
        # ECC Controls
        ("ECC-AM-1", "ECC", "Asset Management", "Asset Inventory Management", "إدارة جرد الأصول", 
         "Maintain comprehensive inventory of all information assets", 
         "الحفاظ على جرد شامل لجميع أصول المعلومات", "high", "in_progress", 3),
        
        ("ECC-BC-1", "ECC", "Business Continuity", "Business Continuity Plan", "خطة استمرارية الأعمال",
         "Develop and maintain business continuity and disaster recovery plans",
         "تطوير والحفاظ على خطط استمرارية الأعمال والتعافي من الكوارث", "critical", "compliant", 4),
        
        ("ECC-IR-1", "ECC", "Incident Response", "Incident Response Plan", "خطة الاستجابة للحوادث",
         "Establish incident response procedures and team",
         "إنشاء إجراءات وفريق الاستجابة للحوادث", "critical", "in_progress", 3),
        
        ("ECC-NW-1", "ECC", "Network Security", "Network Segmentation", "تقسيم الشبكة",
         "Implement network segmentation and isolation controls",
         "تنفيذ ضوابط تقسيم وعزل الشبكة", "high", "compliant", 4),
        
        ("ECC-CR-1", "ECC", "Cryptography", "Encryption Standards", "معايير التشفير",
         "Implement encryption for data at rest and in transit",
         "تنفيذ التشفير للبيانات أثناء السكون والنقل", "critical", "compliant", 4),
        
        # CCC Controls
        ("CCC-MON-01", "CCC", "Monitoring", "Cloud Security Monitoring", "مراقبة أمن السحابة",
         "Implement continuous monitoring and logging for cloud services",
         "تنفيذ المراقبة والتسجيل المستمر لخدمات السحابة", "high", "in_progress", 3),
        
        ("CCC-NET-01", "CCC", "Network Security", "Cloud Network Security", "أمن شبكة السحابة",
         "Configure network security groups and firewalls in cloud",
         "تكوين مجموعات أمان الشبكة وجدران الحماية في السحابة", "critical", "compliant", 4),
        
        ("CCC-BACK-01", "CCC", "Backup & Recovery", "Cloud Backup Strategy", "استراتيجية النسخ الاحتياطي السحابي",
         "Implement automated backup and recovery for cloud resources",
         "تنفيذ النسخ الاحتياطي والاسترداد الآلي لموارد السحابة", "high", "in_progress", 3),
        
        # PDPL Controls
        ("PDPL-25", "PDPL", "Data Transfer", "Cross-Border Data Transfer", "نقل البيانات عبر الحدود",
         "Establish controls for international data transfers",
         "إنشاء ضوابط لنقل البيانات الدولية", "critical", "non_compliant", 1),
        
        ("PDPL-30", "PDPL", "Privacy Impact", "Privacy Impact Assessment", "تقييم تأثير الخصوصية",
         "Conduct privacy impact assessments for new systems",
         "إجراء تقييمات تأثير الخصوصية للأنظمة الجديدة", "high", "non_compliant", 1),
        
        ("PDPL-35", "PDPL", "Data Minimization", "Data Minimization Policy", "سياسة تقليل البيانات",
         "Implement data minimization and purpose limitation",
         "تنفيذ تقليل البيانات وتحديد الغرض", "medium", "in_progress", 2),
    ]
    
    added = 0
    for control in additional_controls:
        try:
            # Check if exists
            cursor.execute("SELECT id FROM controls WHERE control_id = ?", (control[0],))
            if cursor.fetchone():
                print(f"⏭️  {control[0]} already exists")
                continue
            
            cursor.execute("""
                INSERT INTO controls (control_id, framework, domain, title_en, title_ar, 
                                     description_en, description_ar, priority, status, maturity_level,
                                     created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (*control, datetime.utcnow(), datetime.utcnow()))
            print(f"✅ Added {control[0]} - {control[3]}")
            added += 1
        except Exception as e:
            print(f"❌ Error adding {control[0]}: {e}")
    
    conn.commit()
    conn.close()
    print(f"\n✨ Successfully added {added} new controls!")
    return added

def check_total():
    """Check total controls in database"""
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM controls")
    total = cursor.fetchone()[0]
    conn.close()
    return total

if __name__ == "__main__":
    print("=" * 60)
    print("SICO GRC - Direct Database Loader")
    print("=" * 60)
    
    print(f"\nDatabase: {db_path}")
    print(f"Current controls: {check_total()}")
    
    print("\n📋 Loading additional controls...")
    added = load_controls()
    
    print(f"\n📊 Final count: {check_total()} controls")
    print("=" * 60)
    print("✨ Done! Refresh your browser to see updates.")
    print("=" * 60)
