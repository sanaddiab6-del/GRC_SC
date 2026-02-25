"""
Quick Database Initialization for Demo/Testing
Creates essential tables directly without complex migrations
"""
import sqlite3
import os
from pathlib import Path

# Get database path
db_path = Path(__file__).parent / "sico_grc.db"

print(f"Initializing database: {db_path}")

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create controls table
cursor.execute("""
CREATE TABLE IF NOT EXISTS controls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    control_id VARCHAR(50) NOT NULL UNIQUE,
    framework VARCHAR(10) NOT NULL,
    domain VARCHAR(100) NOT NULL,
    title_en VARCHAR(500) NOT NULL,
    title_ar VARCHAR(500) NOT NULL,
    description_en TEXT NOT NULL,
    description_ar TEXT NOT NULL,
    policy_guidance_en TEXT,
    policy_guidance_ar TEXT,
    procedure_guidance_en TEXT,
    procedure_guidance_ar TEXT,
    priority VARCHAR(20),
    status VARCHAR(20) DEFAULT 'not_implemented',
    maturity_level INTEGER DEFAULT 1,
    evidence_types TEXT,
    related_controls TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# Create evidence table
cursor.execute("""
CREATE TABLE IF NOT EXISTS evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    control_id VARCHAR(50) NOT NULL,
    evidence_type VARCHAR(50) NOT NULL,
    title_en VARCHAR(500) NOT NULL,
    title_ar VARCHAR(500) NOT NULL,
    description_en TEXT,
    description_ar TEXT,
    file_path VARCHAR(500),
    file_name VARCHAR(255),
    file_size INTEGER,
    mime_type VARCHAR(100),
    uploaded_by VARCHAR(100),
    upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending',
    review_notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (control_id) REFERENCES controls (control_id)
)
""")

# Insert sample controls
sample_controls = [
    ('ECC-1-1', 'ECC', 'Security Policies', 
     'Information Security Policies', 'سياسات أمن المعلومات',
     'Develop and maintain information security policies', 'تطوير وصيانة سياسات أمن المعلومات',
     'High'),
    ('ECC-2-1', 'ECC', 'Organization of Information Security',
     'Roles and Responsibilities', 'الأدوار والمسؤوليات',
     'Define information security roles and responsibilities', 'تحديد أدوار ومسؤوليات أمن المعلومات',
     'High'),
    ('CCC-1-1', 'CCC', 'Cloud Security',
     'Cloud Service Provider Selection', 'اختيار مزود الخدمة السحابية',
     'Evaluate and select cloud service providers', 'تقييم واختيار مزودي الخدمات السحابية',
     'High'),
    ('PDPL-1-1', 'PDPL', 'Data Protection',
     'Personal Data Processing', 'معالجة البيانات الشخصية',
     'Ensure lawful processing of personal data', 'ضمان المعالجة القانونية للبيانات الشخصية',
     'Critical'),
]

for control in sample_controls:
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO controls 
            (control_id, framework, domain, title_en, title_ar, description_en, description_ar, priority, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'not_implemented')
        """, control)
    except Exception as e:
        print(f"Error inserting control {control[0]}: {e}")

conn.commit()

# Verify
cursor.execute("SELECT COUNT(*) FROM controls")
count = cursor.fetchone()[0]
print(f"✅ Database initialized with {count} controls")

conn.close()
print("✅ Database ready!")
