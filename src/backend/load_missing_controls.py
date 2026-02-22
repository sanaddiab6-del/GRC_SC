"""
SICO GRC - Load Missing ECC Controls + PDPL Obligations
Fills gaps in ECC framework and adds practical PDPL obligation-based controls
"""

import sqlite3
import csv
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "sico_grc.db"

def load_missing_ecc_controls():
    """Load the 8 missing ECC subdomains that were not in the CSV"""
    print("\n🔧 Loading Missing ECC Controls...")
    print("=" * 60)
    
    # Missing ECC controls based on official NCA ECC-1:2018 document
    missing_ecc = [
        # 1-10: Cybersecurity Awareness and Training Program
        {
            "control_id": "1-10-1",
            "framework": "ECC",
            "domain": "Cybersecurity Governance",
            "title_en": "Cybersecurity Awareness Program",
            "title_ar": "برنامج التوعية بالأمن السيبراني",
            "description_en": "A cybersecurity awareness program must be developed and approved. The program must be conducted periodically through multiple channels to strengthen awareness about cybersecurity, cyber threats and risks.",
            "description_ar": "يجب تطوير واعتماد برنامج التوعية بالأمن السيبراني. يجب تنفيذ البرنامج بشكل دوري من خلال قنوات متعددة لتعزيز الوعي بالأمن السيبراني والتهديدات والمخاطر السيبرانية.",
            "policy_guidance_en": "Subdomain: 1-10 Cybersecurity Awareness and Training Program",
            "priority": "critical"
        },
        {
            "control_id": "1-10-2",
            "framework": "ECC",
            "domain": "Cybersecurity Governance",
            "title_en": "Awareness Program Implementation",
            "title_ar": "تنفيذ برنامج التوعية",
            "description_en": "The cybersecurity awareness program must be implemented across the organization with documented training records.",
            "description_ar": "يجب تنفيذ برنامج التوعية بالأمن السيبراني في جميع أنحاء المنظمة مع توثيق سجلات التدريب.",
            "policy_guidance_en": "Subdomain: 1-10 Cybersecurity Awareness and Training Program",
            "priority": "high"
        },
        {
            "control_id": "1-10-3",
            "framework": "ECC",
            "domain": "Cybersecurity Governance",
            "title_en": "Security Awareness Topics",
            "title_ar": "مواضيع التوعية الأمنية",
            "description_en": "Awareness program must cover: phishing emails, mobile device security, storage media handling, secure Internet browsing, and social media security.",
            "description_ar": "يجب أن يغطي برنامج التوعية: رسائل التصيد الاحتيالي، أمن الأجهزة المحمولة، التعامل مع وسائط التخزين، تصفح الإنترنت الآمن، وأمن وسائل التواصل الاجتماعي.",
            "policy_guidance_en": "Subdomain: 1-10 Cybersecurity Awareness and Training Program",
            "priority": "high"
        },
        {
            "control_id": "1-10-4",
            "framework": "ECC",
            "domain": "Cybersecurity Governance",
            "title_en": "Specialized Security Training",
            "title_ar": "التدريب الأمني المتخصص",
            "description_en": "Specialized training must be provided to cybersecurity function personnel, developers, IT operations, and executive/supervisory positions.",
            "description_ar": "يجب توفير تدريب متخصص لموظفي وظيفة الأمن السيبراني والمطورين وعمليات تكنولوجيا المعلومات والمناصب التنفيذية/الإشرافية.",
            "policy_guidance_en": "Subdomain: 1-10 Cybersecurity Awareness and Training Program",
            "priority": "critical"
        },
        
        # 2-10: Operational Technology Security
        {
            "control_id": "2-10-1",
            "framework": "ECC",
            "domain": "Cybersecurity Defense",
            "title_en": "OT/ICS Security Requirements",
            "title_ar": "متطلبات أمن التكنولوجيا التشغيلية",
            "description_en": "Cybersecurity requirements for Operational Technology (OT), Industrial Control Systems (ICS), and SCADA must be identified, documented, and approved.",
            "description_ar": "يجب تحديد وتوثق واعتماد متطلبات الأمن السيبراني للتكنولوجيا التشغيلية (OT) وأنظمة التحكم الصناعية (ICS) وسكادا.",
            "policy_guidance_en": "Subdomain: 2-10 Operational Technology Security",
            "priority": "critical"
        },
        {
            "control_id": "2-10-2",
            "framework": "ECC",
            "domain": "Cybersecurity Defense",
            "title_en": "OT Network Segmentation",
            "title_ar": "تقسيم شبكة التكنولوجيا التشغيلية",
            "description_en": "OT/ICS networks must be segmented from IT networks with strict access controls and monitoring at demilitarized zones (DMZ).",
            "description_ar": "يجب تقسيم شبكات OT/ICS عن شبكات تكنولوجيا المعلومات مع ضوابط وصول صارمة ومراقبة في المناطق منزوعة السلاح (DMZ).",
            "policy_guidance_en": "Subdomain: 2-10 Operational Technology Security",
            "priority": "critical"
        },
        {
            "control_id": "2-10-3",
            "framework": "ECC",
            "domain": "Cybersecurity Defense",
            "title_en": "OT Asset Inventory",
            "title_ar": "جرد أصول التكنولوجيا التشغيلية",
            "description_en": "Comprehensive inventory of all OT/ICS assets including PLCs, RTUs, HMIs, SCADA servers, and engineering workstations must be maintained.",
            "description_ar": "يجب الاحتفاظ بجرد شامل لجميع أصول OT/ICS بما في ذلك PLCs و RTUs و HMIs وخوادم SCADA ومحطات عمل الهندسة.",
            "policy_guidance_en": "Subdomain: 2-10 Operational Technology Security",
            "priority": "high"
        },
        
        # 2-11: Penetration Testing
        {
            "control_id": "2-11-1",
            "framework": "ECC",
            "domain": "Cybersecurity Defense",
            "title_en": "Penetration Testing Policy",
            "title_ar": "سياسة اختبار الاختراق",
            "description_en": "Penetration testing policy and procedures must be defined, documented, and approved.",
            "description_ar": "يجب تحديد وتوثيق واعتماد سياسة وإجراءات اختبار الاختراق.",
            "policy_guidance_en": "Subdomain: 2-11 Penetration Testing",
            "priority": "critical"
        },
        {
            "control_id": "2-11-2",
            "framework": "ECC",
            "domain": "Cybersecurity Defense",
            "title_en": "Annual Penetration Testing",
            "title_ar": "اختبار الاختراق السنوي",
            "description_en": "Penetration testing must be conducted at least annually by qualified internal or external parties covering network, applications, and social engineering.",
            "description_ar": "يجب إجراء اختبار الاختراق مرة واحدة على الأقل سنوياً من قبل أطراف مؤهلة داخلية أو خارجية تغطي الشبكة والتطبيقات والهندسة الاجتماعية.",
            "policy_guidance_en": "Subdomain: 2-11 Penetration Testing",
            "priority": "critical"
        },
        {
            "control_id": "2-11-3",
            "framework": "ECC",
            "domain": "Cybersecurity Defense",
            "title_en": "Penetration Testing Scope",
            "title_ar": "نطاق اختبار الاختراق",
            "description_en": "Penetration testing scope must cover Internet-facing systems, critical internal systems, wireless networks, and high-risk applications.",
            "description_ar": "يجب أن يغطي نطاق اختبار الاختراق الأنظمة المواجهة للإنترنت والأنظمة الداخلية الحرجة والشبكات اللاسلكية والتطبيقات عالية المخاطر.",
            "policy_guidance_en": "Subdomain: 2-11 Penetration Testing",
            "priority": "high"
        },
        
        # 2-12: Cybersecurity Event Logs and Monitoring
        {
            "control_id": "2-12-1",
            "framework": "ECC",
            "domain": "Cybersecurity Defense",
            "title_en": "Event Logging Requirements",
            "title_ar": "متطلبات تسجيل الأحداث",
            "description_en": "Cybersecurity event logging requirements must be defined, documented, and approved for all critical systems and security devices.",
            "description_ar": "يجب تحديد وتوثيق واعتماد متطلبات تسجيل أحداث الأمن السيبراني لجميع الأنظمة الحرجة وأجهزة الأمان.",
            "policy_guidance_en": "Subdomain: 2-12 Cybersecurity Event Logs and Monitoring Management",
            "priority": "critical"
        },
        {
            "control_id": "2-12-2",
            "framework": "ECC",
            "domain": "Cybersecurity Defense",
            "title_en": "SIEM Implementation",
            "title_ar": "تنفيذ نظام إدارة معلومات الأمن والأحداث",
            "description_en": "Security Information and Event Management (SIEM) system must be implemented for centralized logging and real-time monitoring.",
            "description_ar": "يجب تنفيذ نظام إدارة معلومات الأمن والأحداث (SIEM) للتسجيل المركزي والمراقبة في الوقت الفعلي.",
            "policy_guidance_en": "Subdomain: 2-12 Cybersecurity Event Logs and Monitoring Management",
            "priority": "critical"
        },
        {
            "control_id": "2-12-3",
            "framework": "ECC",
            "domain": "Cybersecurity Defense",
            "title_en": "Log Retention and Protection",
            "title_ar": "الاحتفاظ بالسجلات وحمايتها",
            "description_en": "Security logs must be retained for at least one year and protected from unauthorized modification or deletion.",
            "description_ar": "يجب الاحتفاظ بسجلات الأمان لمدة سنة واحدة على الأقل وحمايتها من التعديل أو الحذف غير المصرح به.",
            "policy_guidance_en": "Subdomain: 2-12 Cybersecurity Event Logs and Monitoring Management",
            "priority": "critical"
        },
        {
            "control_id": "2-12-4",
            "framework": "ECC",
            "domain": "Cybersecurity Defense",
            "title_en": "Security Monitoring and Alerting",
            "title_ar": "المراقبة الأمنية والتنبيه",
            "description_en": "24/7 security monitoring must be implemented with automated alerting for critical security events and anomalies.",
            "description_ar": "يجب تنفيذ المراقبة الأمنية على مدار الساعة طوال أيام الأسبوع مع التنبيه التلقائي للأحداث الأمنية الحرجة والشذوذ.",
            "policy_guidance_en": "Subdomain: 2-12 Cybersecurity Event Logs and Monitoring Management",
            "priority": "critical"
        },
        
        # 2-13: Cybersecurity Incident and Threat Management
        {
            "control_id": "2-13-1",
            "framework": "ECC",
            "domain": "Cybersecurity Defense",
            "title_en": "Incident Response Plan",
            "title_ar": "خطة الاستجابة للحوادث",
            "description_en": "Comprehensive incident response plan must be defined, documented, approved, and tested at least annually.",
            "description_ar": "يجب تحديد وتوثيق واعتماد واختبار خطة الاستجابة للحوادث الشاملة مرة واحدة على الأقل سنوياً.",
            "policy_guidance_en": "Subdomain: 2-13 Cybersecurity Incident and Threat Management",
            "priority": "critical"
        },
        {
            "control_id": "2-13-2",
            "framework": "ECC",
            "domain": "Cybersecurity Defense",
            "title_en": "Incident Response Team",
            "title_ar": "فريق الاستجابة للحوادث",
            "description_en": "Dedicated incident response team (CSIRT) must be established with defined roles, responsibilities, and 24/7 availability.",
            "description_ar": "يجب إنشاء فريق استجابة للحوادث (CSIRT) مخصص مع أدوار ومسؤوليات محددة وتوفر على مدار الساعة طوال أيام الأسبوع.",
            "policy_guidance_en": "Subdomain: 2-13 Cybersecurity Incident and Threat Management",
            "priority": "critical"
        },
        {
            "control_id": "2-13-3",
            "framework": "ECC",
            "domain": "Cybersecurity Defense",
            "title_en": "NCA Incident Reporting",
            "title_ar": "الإبلاغ عن الحوادث للهيئة الوطنية",
            "description_en": "Critical cybersecurity incidents must be reported to NCA within 72 hours through the official incident reporting portal.",
            "description_ar": "يجب الإبلاغ عن حوادث الأمن السيبراني الحرجة للهيئة الوطنية للأمن السيبراني خلال 72 ساعة من خلال البوابة الرسمية للإبلاغ عن الحوادث.",
            "policy_guidance_en": "Subdomain: 2-13 Cybersecurity Incident and Threat Management",
            "priority": "critical"
        },
        {
            "control_id": "2-13-4",
            "framework": "ECC",
            "domain": "Cybersecurity Defense",
            "title_en": "Threat Intelligence",
            "title_ar": "معلومات التهديدات",
            "description_en": "Threat intelligence feeds must be subscribed to and integrated with security monitoring to identify emerging threats.",
            "description_ar": "يجب الاشتراك في موجزات معلومات التهديدات ودمجها مع المراقبة الأمنية لتحديد التهديدات الناشئة.",
            "policy_guidance_en": "Subdomain: 2-13 Cybersecurity Incident and Threat Management",
            "priority": "high"
        },
        
        # 2-14: Physical Security
        {
            "control_id": "2-14-1",
            "framework": "ECC",
            "domain": "Cybersecurity Defense",
            "title_en": "Physical Security Policy",
            "title_ar": "سياسة الأمن المادي",
            "description_en": "Physical security policy and procedures must be defined, documented, and approved for data centers and critical IT facilities.",
            "description_ar": "يجب تحديد وتوثيق واعتماد سياسة وإجراءات الأمن المادي لمراكز البيانات ومنشآت تكنولوجيا المعلومات الحرجة.",
            "policy_guidance_en": "Subdomain: 2-14 Physical Security",
            "priority": "critical"
        },
        {
            "control_id": "2-14-2",
            "framework": "ECC",
            "domain": "Cybersecurity Defense",
            "title_en": "Physical Access Controls",
            "title_ar": "ضوابط الوصول المادي",
            "description_en": "Physical access to data centers and server rooms must be controlled using badge readers, biometric systems, or equivalent mechanisms.",
            "description_ar": "يجب التحكم في الوصول المادي إلى مراكز البيانات وغرف الخوادم باستخدام قارئات البطاقات أو الأنظمة البيومترية أو آليات مماثلة.",
            "policy_guidance_en": "Subdomain: 2-14 Physical Security",
            "priority": "critical"
        },
        {
            "control_id": "2-14-3",
            "framework": "ECC",
            "domain": "Cybersecurity Defense",
            "title_en": "Environmental Controls",
            "title_ar": "الضوابط البيئية",
            "description_en": "Environmental controls must be implemented including fire suppression, temperature/humidity monitoring, and power backup (UPS).",
            "description_ar": "يجب تنفيذ الضوابط البيئية بما في ذلك نظام إطفاء الحريق ومراقبة درجة الحرارة/الرطوبة والنسخ الاحتياطي للطاقة (UPS).",
            "policy_guidance_en": "Subdomain: 2-14 Physical Security",
            "priority": "high"
        },
        
        # 2-15: Web Application Security
        {
            "control_id": "2-15-1",
            "framework": "ECC",
            "domain": "Cybersecurity Defense",
            "title_en": "Secure Software Development",
            "title_ar": "تطوير البرمجيات الآمن",
            "description_en": "Secure software development lifecycle (SSDLC) must be implemented following OWASP or equivalent secure coding standards.",
            "description_ar": "يجب تنفيذ دورة حياة تطوير البرمجيات الآمنة (SSDLC) وفقاً لمعايير OWASP أو معايير البرمجة الآمنة المعادلة.",
            "policy_guidance_en": "Subdomain: 2-15 Web Application Security",
            "priority": "critical"
        },
        {
            "control_id": "2-15-2",
            "framework": "ECC",
            "domain": "Cybersecurity Defense",
            "title_en": "Web Application Firewall",
            "title_ar": "جدار حماية تطبيقات الويب",
            "description_en": "Web Application Firewall (WAF) must be deployed for all Internet-facing web applications to protect against OWASP Top 10 vulnerabilities.",
            "description_ar": "يجب نشر جدار حماية تطبيقات الويب (WAF) لجميع تطبيقات الويب المواجهة للإنترنت للحماية من أهم 10 ثغرات أمنية في OWASP.",
            "policy_guidance_en": "Subdomain: 2-15 Web Application Security",
            "priority": "critical"
        },
        {
            "control_id": "2-15-3",
            "framework": "ECC",
            "domain": "Cybersecurity Defense",
            "title_en": "Application Security Testing",
            "title_ar": "اختبار أمان التطبيقات",
            "description_en": "Static (SAST) and Dynamic (DAST) application security testing must be conducted before production deployment.",
            "description_ar": "يجب إجراء اختبار أمان التطبيقات الثابت (SAST) والديناميكي (DAST) قبل النشر في الإنتاج.",
            "policy_guidance_en": "Subdomain: 2-15 Web Application Security",
            "priority": "high"
        },
        
        # 2-16: Business Continuity and Disaster Recovery
        {
            "control_id": "2-16-1",
            "framework": "ECC",
            "domain": "Cybersecurity Defense",
            "title_en": "Business Continuity Plan",
            "title_ar": "خطة استمرارية الأعمال",
            "description_en": "Business Continuity Plan (BCP) must be developed, documented, approved, and tested at least annually.",
            "description_ar": "يجب تطوير وتوثيق واعتماد واختبار خطة استمرارية الأعمال (BCP) مرة واحدة على الأقل سنوياً.",
            "policy_guidance_en": "Subdomain: 2-16 Business Continuity and Disaster Recovery",
            "priority": "critical"
        },
        {
            "control_id": "2-16-2",
            "framework": "ECC",
            "domain": "Cybersecurity Defense",
            "title_en": "Disaster Recovery Plan",
            "title_ar": "خطة التعافي من الكوارث",
            "description_en": "Disaster Recovery Plan (DRP) must be established with defined Recovery Time Objectives (RTO) and Recovery Point Objectives (RPO).",
            "description_ar": "يجب إنشاء خطة التعافي من الكوارث (DRP) مع أهداف وقت التعافي (RTO) وأهداف نقطة التعافي (RPO) المحددة.",
            "policy_guidance_en": "Subdomain: 2-16 Business Continuity and Disaster Recovery",
            "priority": "critical"
        },
        {
            "control_id": "2-16-3",
            "framework": "ECC",
            "domain": "Cybersecurity Defense",
            "title_en": "Data Backup Strategy",
            "title_ar": "استراتيجية النسخ الاحتياطي للبيانات",
            "description_en": "Regular data backups must be performed following the 3-2-1 rule with off-site or cloud storage and encrypted backups.",
            "description_ar": "يجب إجراء نسخ احتياطي منتظم للبيانات وفقاً لقاعدة 3-2-1 مع التخزين خارج الموقع أو السحابي والنسخ الاحتياطية المشفرة.",
            "policy_guidance_en": "Subdomain: 2-16 Business Continuity and Disaster Recovery",
            "priority": "critical"
        },
        {
            "control_id": "2-16-4",
            "framework": "ECC",
            "domain": "Cybersecurity Defense",
            "title_en": "BCP/DR Testing",
            "title_ar": "اختبار خطط استمرارية الأعمال والتعافي",
            "description_en": "BCP and DRP must be tested at least annually through tabletop exercises or full failover tests with documented results.",
            "description_ar": "يجب اختبار خطط استمرارية الأعمال والتعافي من الكوارث مرة واحدة على الأقل سنوياً من خلال تمارين سطح المكتب أو اختبارات التبديل الكاملة مع نتائج موثقة.",
            "policy_guidance_en": "Subdomain: 2-16 Business Continuity and Disaster Recovery",
            "priority": "critical"
        }
    ]
    
    return missing_ecc


def load_pdpl_obligations():
    """Load PDPL obligation-based controls from CSV"""
    print("\n🔒 Loading PDPL Obligation-Based Controls...")
    print("=" * 60)
    
    csv_file = Path(r"c:\Users\Shahd\Downloads\PDPL_Obligation_Based_Control_Library_GRC_Ready.csv")
    
    obligations = []
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader, 1):
                obligation = {
                    "control_id": f"PDPL-OBL-{idx:02d}",
                    "framework": "PDPL",
                    "domain": row['Aligned Domain'],
                    "title_en": row['PDPL Control (Obligation)'],
                    "title_ar": f"التزام PDPL {idx}",  # Will be enhanced with proper Arabic
                    "description_en": f"{row['PDPL Control (Obligation)']} (Reference: {row['PDPL Reference']})",
                    "description_ar": row['PDPL Control (Obligation)'],  # Can be translated
                    "policy_guidance_en": f"Subdomain: {row['Subdomain']}",
                    "policy_guidance_ar": row['Subdomain'],
                    "procedure_guidance_en": f"PDPL Reference: {row['PDPL Reference']}",
                    "priority": "critical" if "breach" in row['PDPL Control (Obligation)'].lower() or "consent" in row['PDPL Control (Obligation)'].lower() else "high",
                    "status": "active"
                }
                obligations.append(obligation)
        
        print(f"✅ Loaded {len(obligations)} PDPL obligation-based controls")
        return obligations
        
    except FileNotFoundError:
        print(f"⚠️ CSV file not found: {csv_file}")
        return []


def insert_controls(controls, label):
    """Insert controls into database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    inserted = 0
    skipped = 0
    
    for control in controls:
        try:
            # Check if control already exists
            cursor.execute("SELECT id FROM controls WHERE control_id = ?", (control['control_id'],))
            if cursor.fetchone():
                skipped += 1
                continue
            
            cursor.execute("""
                INSERT INTO controls (
                    control_id, framework, domain, title_en, title_ar,
                    description_en, description_ar, policy_guidance_en, policy_guidance_ar,
                    procedure_guidance_en, procedure_guidance_ar, priority, status,
                    maturity_level, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                control['control_id'],
                control['framework'],
                control['domain'],
                control['title_en'],
                control['title_ar'],
                control.get('description_en', ''),
                control.get('description_ar', ''),
                control.get('policy_guidance_en', ''),
                control.get('policy_guidance_ar', ''),
                control.get('procedure_guidance_en', ''),
                control.get('procedure_guidance_ar', ''),
                control.get('priority', 'medium'),
                control.get('status', 'active'),
                1,
                datetime.now(),
                datetime.now()
            ))
            inserted += 1
            
        except Exception as e:
            print(f"   ⚠️ Error inserting {control['control_id']}: {str(e)}")
            continue
    
    conn.commit()
    conn.close()
    
    print(f"   ✅ {inserted} new controls inserted")
    print(f"   ⏭️ {skipped} controls already exist")
    
    return inserted, skipped


def main():
    print("\n" + "="*80)
    print("🔧 SICO GRC - MISSING CONTROLS REMEDIATION")
    print("="*80)
    print("Adding missing ECC subdomains + practical PDPL obligations\n")
    
    total_inserted = 0
    total_skipped = 0
    
    # Load missing ECC controls
    missing_ecc = load_missing_ecc_controls()
    inserted, skipped = insert_controls(missing_ecc, "Missing ECC")
    total_inserted += inserted
    total_skipped += skipped
    
    # Load PDPL obligation-based controls
    pdpl_obligations = load_pdpl_obligations()
    if pdpl_obligations:
        inserted, skipped = insert_controls(pdpl_obligations, "PDPL Obligations")
        total_inserted += inserted
        total_skipped += skipped
    
    print("\n" + "="*80)
    print("✅ REMEDIATION COMPLETE!")
    print("="*80)
    print(f"📊 Total new controls: {total_inserted}")
    print(f"⏭️  Skipped (existing): {total_skipped}")
    
    # Verify final counts
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT framework, COUNT(*) FROM controls GROUP BY framework")
    print(f"\n📈 Updated Database Counts:")
    for fw, count in cursor.fetchall():
        print(f"   {fw}: {count} controls")
    
    cursor.execute("SELECT COUNT(*) FROM controls")
    total = cursor.fetchone()[0]
    print(f"   {'─'*50}")
    print(f"   TOTAL: {total} controls\n")
    
    conn.close()


if __name__ == "__main__":
    main()
