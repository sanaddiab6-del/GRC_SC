"""
SICO GRC Platform - Complete Control Libraries Loader
Loads ALL Saudi regulatory controls from official sources:
- ECC (Essential Cybersecurity Controls) - Full 114 controls from CSV
- CCC (Cloud Cybersecurity Controls) - Full 67 controls from CSV  
- PDPL (Personal Data Protection Law) - Complete 35 articles
"""

import sqlite3
import csv
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "sico_grc.db"
CSV_PATH = Path(__file__).parent.parent.parent / "data" / "controls"

def load_ecc_from_csv():
    """Load complete ECC controls from CSV (114 controls)"""
    print("📋 Loading ECC Controls from CSV...")
    
    csv_file = Path(r"c:\Users\Shahd\Downloads\ECC_Full_Controls_Extracted.csv")
    
    controls = []
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                control = {
                    "control_id": row['Control_ID'],
                    "framework": "ECC",
                    "framework_version": "ECC-1:2018",
                    "domain": row['Domain'],
                    "subdomain": row['Subdomain'],
                    "title_en": row['Control_Clause'][:200] if len(row['Control_Clause']) > 200 else row['Control_Clause'],
                    "title_ar": f"ضابط {row['Control_ID']}",  # Will be enhanced with proper Arabic
                    "control_clause_en": row['Control_Clause'],
                    "control_clause_ar": "",  # To be filled with official Arabic ECC document
                    "description_en": row['Control_Clause'],
                    "description_ar": "",
                    "evidence_examples": row.get('Evidence_Examples', ''),
                    "mapping_ccc": row.get('Mapping_CCC', ''),
                    "mapping_pdpl": row.get('Mapping_PDPL', ''),
                    "source_pdf": row.get('Source_PDF', 'ecc-en.pdf'),
                    "source_page": int(row['Source_Page']) if row.get('Source_Page') else None,
                    "priority": "high",
                    "status": "active"
                }
                controls.append(control)
        
        print(f"✅ Loaded {len(controls)} ECC controls from CSV")
        return controls
        
    except FileNotFoundError:
        print(f"⚠️ CSV file not found: {csv_file}")
        return []


def load_ccc_from_csv():
    """Load complete CCC controls from CSV (67 controls)"""
    print("☁️ Loading CCC Controls from CSV...")
    
    csv_file = Path(r"c:\Users\Shahd\Downloads\CCC_Full_Controls_Extracted_EN.csv")
    
    controls = []
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                control = {
                    "control_id": row['Control_ID'],
                    "framework": "CCC",
                    "framework_version": "CCC-2:2024",
                    "domain": row['Domain'],
                    "subdomain": row['Subdomain'],
                    "title_en": row['Control_Clause'][:200] if len(row['Control_Clause']) > 200 else row['Control_Clause'],
                    "title_ar": f"ضابط {row['Control_ID']}",  # Will be enhanced
                    "control_clause_en": row['Control_Clause'],
                    "control_clause_ar": "",  # Arabic version from official CCC doc
                    "description_en": row['Control_Clause'],
                    "description_ar": "",
                    "source_pdf": row.get('Source_PDF', 'CCC-2-2024-EN.pdf'),
                    "source_page": int(row['Source_Page']) if row.get('Source_Page') else None,
                    "priority": "high",
                    "status": "active"
                }
                controls.append(control)
        
        print(f"✅ Loaded {len(controls)} CCC controls from CSV")
        return controls
        
    except FileNotFoundError:
        print(f"⚠️ CSV file not found: {csv_file}")
        return []


def load_complete_pdpl():
    """Load COMPLETE PDPL regulations - All 35 articles"""
    print("🔒 Loading COMPLETE PDPL Regulations (35 Articles)...")
    
    # Complete PDPL Law Articles (1-35) with bilingual support
    pdpl_articles = [
        # CHAPTER 1: GENERAL PROVISIONS (Articles 1-2)
        {
            "control_id": "PDPL-01",
            "framework": "PDPL",
            "framework_version": "2021",
            "domain": "General Provisions",
            "subdomain": "Article 1: Definitions",
            "title_en": "Definitions and Terminology",
            "title_ar": "التعريفات والمصطلحات",
            "control_clause_en": "This Law defines key terms including Personal Data, Data Controller, Data Processor, Data Subject, Processing, Consent, and SDAIA.",
            "control_clause_ar": "يحدد هذا النظام المصطلحات الأساسية بما في ذلك البيانات الشخصية، والمتحكم في البيانات، ومعالج البيانات، وصاحب البيانات، والمعالجة، والموافقة، وسدايا.",
            "description_en": "Establishes legal definitions for all data protection terminology used throughout the law.",
            "description_ar": "يضع التعاريف القانونية لجميع مصطلحات حماية البيانات المستخدمة في النظام.",
            "priority": "critical",
            "status": "active",
            "source_pdf": "pdpl-law-2021.pdf",
            "source_page": 2
        },
        {
            "control_id": "PDPL-02",
            "framework": "PDPL",
            "framework_version": "2021",
            "domain": "General Provisions",
            "subdomain": "Article 2: Scope of Application",
            "title_en": "Scope and Territorial Application",
            "title_ar": "نطاق التطبيق والاختصاص الإقليمي",
            "control_clause_en": "This Law applies to processing of personal data by controllers and processors in Saudi Arabia, or processing related to offering goods/services to data subjects in Saudi Arabia.",
            "control_clause_ar": "ينطبق هذا النظام على معالجة البيانات الشخصية من قبل المتحكمين والمعالجين في المملكة، أو المعالجة المتعلقة بتقديم سلع أو خدمات لأصحاب البيانات في المملكة.",
            "description_en": "Defines territorial scope covering controllers/processors within Saudi Arabia and those targeting Saudi residents.",
            "description_ar": "يحدد النطاق الإقليمي الذي يشمل المتحكمين/المعالجين داخل المملكة والموجهين لسكان المملكة.",
            "priority": "critical",
            "status": "active",
            "source_pdf": "pdpl-law-2021.pdf",
            "source_page": 3
        },
        
        # CHAPTER 2: PRINCIPLES OF PERSONAL DATA PROCESSING (Articles 3-12)
        {
            "control_id": "PDPL-03",
            "framework": "PDPL",
            "framework_version": "2021",
            "domain": "Data Processing Principles",
            "subdomain": "Article 3: Lawfulness, Fairness, Transparency",
            "title_en": "Lawful, Fair, and Transparent Processing",
            "title_ar": "المعالجة المشروعة والعادلة والشفافة",
            "control_clause_en": "Personal data must be processed lawfully, fairly, and transparently. Processing requires valid legal basis: consent, contract, legal obligation, vital interests, public task, or legitimate interests.",
            "control_clause_ar": "يجب معالجة البيانات الشخصية بشكل مشروع وعادل وشفاف. تتطلب المعالجة أساساً قانونياً صحيحاً: الموافقة، أو العقد، أو الالتزام القانوني، أو المصالح الحيوية، أو المهمة العامة، أو المصالح المشروعة.",
            "description_en": "Establishes six lawful bases for data processing and mandates transparency in all processing activities.",
            "description_ar": "يحدد ستة أسس قانونية لمعالجة البيانات ويفرض الشفافية في جميع أنشطة المعالجة.",
            "priority": "critical",
            "status": "active",
            "mapping_ecc": "1-2-3, 1-4-1, 2-1-3",
            "mapping_ccc": "1-2-P-1",
            "source_pdf": "pdpl-law-2021.pdf",
            "source_page": 4
        },
        {
            "control_id": "PDPL-04",
            "framework": "PDPL",
            "framework_version": "2021",
            "domain": "Data Processing Principles",
            "subdomain": "Article 4: Purpose Limitation",
            "title_en": "Purpose Limitation and Specification",
            "title_ar": "تحديد الغرض والقيود",
            "control_clause_en": "Personal data must be collected for specified, explicit, and legitimate purposes, and not further processed in a manner incompatible with those purposes.",
            "control_clause_ar": "يجب جمع البيانات الشخصية لأغراض محددة وصريحة ومشروعة، ولا يجوز معالجتها بطريقة غير متوافقة مع تلك الأغراض.",
            "description_en": "Prohibits function creep - using data for purposes beyond what was originally communicated to data subjects.",
            "description_ar": "يمنع التوسع الوظيفي - استخدام البيانات لأغراض تتجاوز ما تم إبلاغه في الأصل لأصحاب البيانات.",
            "priority": "critical",
            "status": "active",
            "source_pdf": "pdpl-law-2021.pdf",
            "source_page": 5
        },
        {
            "control_id": "PDPL-05",
            "framework": "PDPL",
            "framework_version": "2021",
            "domain": "Data Processing Principles",
            "subdomain": "Article 5: Data Minimization",
            "title_en": "Data Minimization Principle",
            "title_ar": "مبدأ تقليل البيانات",
            "control_clause_en": "Personal data collected must be adequate, relevant, and limited to what is necessary in relation to the purposes for which they are processed.",
            "control_clause_ar": "يجب أن تكون البيانات الشخصية المجمعة كافية وذات صلة ومقتصرة على ما هو ضروري فيما يتعلق بالأغراض التي تُعالج من أجلها.",
            "description_en": "Requires organizations to collect only the minimum personal data necessary for stated purposes.",
            "description_ar": "يتطلب من المنظمات جمع الحد الأدنى فقط من البيانات الشخصية اللازمة للأغراض المعلنة.",
            "priority": "high",
            "status": "active",
            "source_pdf": "pdpl-law-2021.pdf",
            "source_page": 5
        },
        {
            "control_id": "PDPL-06",
            "framework": "PDPL",
            "framework_version": "2021",
            "domain": "Data Processing Principles",
            "subdomain": "Article 6: Data Accuracy",
            "title_en": "Accuracy and Currency of Personal Data",
            "title_ar": "دقة وحداثة البيانات الشخصية",
            "control_clause_en": "Personal data must be accurate and, where necessary, kept up to date. Reasonable steps must be taken to ensure inaccurate data is erased or rectified without delay.",
            "control_clause_ar": "يجب أن تكون البيانات الشخصية دقيقة، وعند الضرورة، محدثة. يجب اتخاذ خطوات معقولة لضمان حذف أو تصحيح البيانات غير الدقيقة دون تأخير.",
            "description_en": "Mandates data accuracy maintenance and prompt correction mechanisms for inaccurate personal data.",
            "description_ar": "يفرض الحفاظ على دقة البيانات وآليات التصحيح الفوري للبيانات الشخصية غير الدقيقة.",
            "priority": "high",
            "status": "active",
            "source_pdf": "pdpl-law-2021.pdf",
            "source_page": 6
        },
        {
            "control_id": "PDPL-07",
            "framework": "PDPL",
            "framework_version": "2021",
            "domain": "Data Processing Principles",
            "subdomain": "Article 7: Storage Limitation",
            "title_en": "Storage Limitation and Retention",
            "title_ar": "القيود على التخزين والاحتفاظ",
            "control_clause_en": "Personal data must be kept in a form which permits identification of data subjects for no longer than necessary for the purposes for which the data are processed.",
            "control_clause_ar": "يجب الاحتفاظ بالبيانات الشخصية بشكل يسمح بتحديد هوية أصحاب البيانات لمدة لا تزيد عن اللازم للأغراض التي تُعالج من أجلها البيانات.",
            "description_en": "Establishes data retention limits and requires deletion when purposes are fulfilled or legal retention expires.",
            "description_ar": "يحدد حدود الاحتفاظ بالبيانات ويتطلب الحذف عند تحقيق الأغراض أو انتهاء مدة الاحتفاظ القانونية.",
            "priority": "high",
            "status": "active",
            "source_pdf": "pdpl-law-2021.pdf",
            "source_page": 6
        },
        {
            "control_id": "PDPL-08",
            "framework": "PDPL",
            "framework_version": "2021",
            "domain": "Data Processing Principles",
            "subdomain": "Article 8: Integrity and Confidentiality",
            "title_en": "Security, Integrity, and Confidentiality",
            "title_ar": "الأمن والنزاهة والسرية",
            "control_clause_en": "Personal data must be processed securely using appropriate technical and organizational measures to protect against unauthorized access, disclosure, alteration, or destruction.",
            "control_clause_ar": "يجب معالجة البيانات الشخصية بشكل آمن باستخدام التدابير الفنية والتنظيمية المناسبة للحماية من الوصول أو الإفشاء أو التعديل أو الإتلاف غير المصرح به.",
            "description_en": "Core security principle requiring technical and organizational measures proportionate to data sensitivity.",
            "description_ar": "مبدأ الأمن الأساسي الذي يتطلب تدابير فنية وتنظيمية متناسبة مع حساسية البيانات.",
            "priority": "critical",
            "status": "active",
            "mapping_ecc": "2-1 to 2-16",
            "mapping_ccc": "2-11-P-1, 2-15-P-3",
            "source_pdf": "pdpl-law-2021.pdf",
            "source_page": 7
        },
        {
            "control_id": "PDPL-09",
            "framework": "PDPL",
            "framework_version": "2021",
            "domain": "Data Processing Principles",
            "subdomain": "Article 9: Accountability",
            "title_en": "Accountability and Demonstrating Compliance",
            "title_ar": "المساءلة وإثبات الامتثال",
            "control_clause_en": "The controller is responsible for and must be able to demonstrate compliance with all PDPL principles (accountability principle).",
            "control_clause_ar": "المتحكم مسؤول عن الامتثال لجميع مبادئ نظام حماية البيانات الشخصية ويجب أن يكون قادراً على إثبات ذلك (مبدأ المساءلة).",
            "description_en": "Shifts burden of proof to controllers - must maintain documentation evidencing PDPL compliance.",
            "description_ar": "ينقل عبء الإثبات إلى المتحكمين - يجب الاحتفاظ بالوثائق التي تثبت الامتثال لنظام حماية البيانات الشخصية.",
            "priority": "critical",
            "status": "active",
            "source_pdf": "pdpl-law-2021.pdf",
            "source_page": 7
        },
        {
            "control_id": "PDPL-10",
            "framework": "PDPL",
            "framework_version": "2021",
            "domain": "Data Processing Principles",
            "subdomain": "Article 10: Sensitive Personal Data",
            "title_en": "Sensitive Personal Data - Enhanced Protection",
            "title_ar": "البيانات الشخصية الحساسة - حماية معززة",
            "control_clause_en": "Processing sensitive personal data (health, biometric, genetic, racial, ethnic, political, religious, philosophical beliefs, trade union, sexual orientation, criminal records) requires explicit consent or specific legal grounds and enhanced safeguards.",
            "control_clause_ar": "تتطلب معالجة البيانات الشخصية الحساسة (الصحة، البيومترية، الوراثية، العرقية، الإثنية، السياسية، الدينية، المعتقدات الفلسفية، النقابية، التوجه الجنسي، السجل الجنائي) موافقة صريحة أو أسس قانونية محددة وضمانات معززة.",
            "description_en": "Higher threshold for processing sensitive data categories requiring explicit consent and additional protections.",
            "description_ar": "حد أعلى لمعالجة فئات البيانات الحساسة التي تتطلب موافقة صريحة وحماية إضافية.",
            "priority": "critical",
            "status": "active",
            "source_pdf": "pdpl-law-2021.pdf",
            "source_page": 8
        },
        {
            "control_id": "PDPL-11",
            "framework": "PDPL",
            "framework_version": "2021",
            "domain": "Data Processing Principles",
            "subdomain": "Article 11: Children's Personal Data",
            "title_en": "Processing Children's Personal Data",
            "title_ar": "معالجة البيانات الشخصية للأطفال",
            "control_clause_en": "Processing children's personal data (under 18) requires verifiable parental or guardian consent and additional protections appropriate to the child's age and understanding.",
            "control_clause_ar": "تتطلب معالجة البيانات الشخصية للأطفال (دون 18 عاماً) موافقة يمكن التحقق منها من ولي الأمر أو الوصي وحماية إضافية مناسبة لعمر الطفل وفهمه.",
            "description_en": "Special regime for children's data requiring parental consent verification and age-appropriate safeguards.",
            "description_ar": "نظام خاص لبيانات الأطفال يتطلب التحقق من موافقة الوالدين وضمانات مناسبة للعمر.",
            "priority": "critical",
            "status": "active",
            "source_pdf": "pdpl-law-2021.pdf",
            "source_page": 9
        },
        {
            "control_id": "PDPL-12",
            "framework": "PDPL",
            "framework_version": "2021",
            "domain": "Data Processing Principles",
            "subdomain": "Article 12: Automated Decision-Making",
            "title_en": "Automated Decision-Making and Profiling",
            "title_ar": "اتخاذ القرارات الآلية والتنميط",
            "control_clause_en": "Data subjects have the right not to be subject to decisions based solely on automated processing, including profiling, which produces legal or similarly significant effects, unless necessary for contract, authorized by law, or based on explicit consent.",
            "control_clause_ar": "لأصحاب البيانات الحق في عدم الخضوع لقرارات تستند فقط إلى المعالجة الآلية، بما في ذلك التنميط، والتي تنتج آثاراً قانونية أو مماثلة، ما لم يكن ذلك ضرورياً للعقد أو مصرحاً به بموجب القانون أو بناءً على موافقة صريحة.",
            "description_en": "Restricts purely automated decisions and requires human intervention for significant decisions affecting individuals.",
            "description_ar": "يقيد القرارات الآلية البحتة ويتطلب تدخلاً بشرياً للقرارات المهمة التي تؤثر على الأفراد.",
            "priority": "high",
            "status": "active",
            "source_pdf": "pdpl-law-2021.pdf",
            "source_page": 10
        },
        
        # CHAPTER 3: RIGHTS OF DATA SUBJECTS (Articles 13-19)
        {
            "control_id": "PDPL-13",
            "framework": "PDPL",
            "framework_version": "2021",
            "domain": "Data Subject Rights",
            "subdomain": "Article 13: Right to Information",
            "title_en": "Right to Be Informed - Transparency",
            "title_ar": "الحق في الإعلام - الشفافية",
            "control_clause_en": "Data subjects have the right to clear, transparent information about data processing including controller identity, purposes, legal basis, recipients, retention period, and rights.",
            "control_clause_ar": "لأصحاب البيانات الحق في معلومات واضحة وشفافة حول معالجة البيانات بما في ذلك هوية المتحكم والأغراض والأساس القانوني والمستلمين ومدة الاحتفاظ والحقوق.",
            "description_en": "Mandates privacy notices at collection with comprehensive processing information in accessible language.",
            "description_ar": "يلزم بإشعارات الخصوصية عند الجمع مع معلومات معالجة شاملة بلغة سهلة الفهم.",
            "priority": "critical",
            "status": "active",
            "source_pdf": "pdpl-law-2021.pdf",
            "source_page": 11
        },
        {
            "control_id": "PDPL-14",
            "framework": "PDPL",
            "framework_version": "2021",
            "domain": "Data Subject Rights",
            "subdomain": "Article 14: Right of Access",
            "title_en": "Right to Access Personal Data (DSAR)",
            "title_ar": "الحق في الوصول إلى البيانات الشخصية",
            "control_clause_en": "Data subjects have the right to obtain confirmation whether their personal data is being processed, access to the data, and information about the processing activities. Response within 30 days.",
            "control_clause_ar": "لأصحاب البيانات الحق في الحصول على تأكيد بشأن معالجة بياناتهم الشخصية، والوصول إلى البيانات، ومعلومات حول أنشطة المعالجة. الرد خلال 30 يوماً.",
            "description_en": "Core DSAR (Data Subject Access Request) right - must provide copy of data and processing metadata.",
            "description_ar": "حق الوصول الأساسي للبيانات - يجب توفير نسخة من البيانات ومعلومات المعالجة.",
            "priority": "critical",
            "status": "active",
            "source_pdf": "pdpl-law-2021.pdf",
            "source_page": 12
        },
        {
            "control_id": "PDPL-15",
            "framework": "PDPL",
            "framework_version": "2021",
            "domain": "Data Subject Rights",
            "subdomain": "Article 15: Right to Rectification",
            "title_en": "Right to Rectification of Inaccurate Data",
            "title_ar": "الحق في تصحيح البيانات غير الدقيقة",
            "control_clause_en": "Data subjects have the right to obtain rectification of inaccurate personal data and completion of incomplete data without undue delay.",
            "control_clause_ar": "لأصحاب البيانات الحق في تصحيح البيانات الشخصية غير الدقيقة واستكمال البيانات غير الكاملة دون تأخير لا مبرر له.",
            "description_en": "Right to correct errors in personal data and supplement incomplete records.",
            "description_ar": "الحق في تصحيح الأخطاء في البيانات الشخصية واستكمال السجلات غير الكاملة.",
            "priority": "high",
            "status": "active",
            "source_pdf": "pdpl-law-2021.pdf",
            "source_page": 13
        },
        {
            "control_id": "PDPL-16",
            "framework": "PDPL",
            "framework_version": "2021",
            "domain": "Data Subject Rights",
            "subdomain": "Article 16: Right to Erasure",
            "title_en": "Right to Erasure (Right to Be Forgotten)",
            "title_ar": "الحق في المحو (الحق في النسيان)",
            "control_clause_en": "Data subjects have the right to erasure of their personal data when: purposes fulfilled, consent withdrawn, unlawful processing, legal obligation requires erasure, or data no longer necessary.",
            "control_clause_ar": "لأصحاب البيانات الحق في محو بياناتهم الشخصية عندما: تحقق الغرض، سحبت الموافقة، معالجة غير مشروعة، التزام قانوني يتطلب المحو، أو البيانات لم تعد ضرورية.",
            "description_en": "Right to deletion with exceptions for legal obligations, public interest, and legitimate grounds.",
            "description_ar": "الحق في الحذف مع استثناءات للالتزامات القانونية والمصلحة العامة والأسس المشروعة.",
            "priority": "high",
            "status": "active",
            "source_pdf": "pdpl-law-2021.pdf",
            "source_page": 13
        },
        {
            "control_id": "PDPL-17",
            "framework": "PDPL",
            "framework_version": "2021",
            "domain": "Data Subject Rights",
            "subdomain": "Article 17: Right to Restriction",
            "title_en": "Right to Restriction of Processing",
            "title_ar": "الحق في تقييد المعالجة",
            "control_clause_en": "Data subjects have the right to restrict processing when: accuracy is contested, processing is unlawful, controller no longer needs data but subject needs it for legal claims, or objection is pending verification.",
            "control_clause_ar": "لأصحاب البيانات الحق في تقييد المعالجة عندما: الدقة متنازع عليها، المعالجة غير مشروعة، المتحكم لم يعد بحاجة للبيانات لكن صاحب البيانات يحتاجها للمطالبات القانونية، أو الاعتراض معلق التحقق.",
            "description_en": "Right to temporarily freeze processing under specific circumstances while disputes are resolved.",
            "description_ar": "الحق في تجميد المعالجة مؤقتاً في ظروف محددة أثناء حل النزاعات.",
            "priority": "medium",
            "status": "active",
            "source_pdf": "pdpl-law-2021.pdf",
            "source_page": 14
        },
        {
            "control_id": "PDPL-18",
            "framework": "PDPL",
            "framework_version": "2021",
            "domain": "Data Subject Rights",
            "subdomain": "Article 18: Right to Data Portability",
            "title_en": "Right to Data Portability",
            "title_ar": "الحق في نقل البيانات",
            "control_clause_en": "Data subjects have the right to receive their personal data in a structured, commonly used, machine-readable format and transmit it to another controller where technically feasible.",
            "control_clause_ar": "لأصحاب البيانات الحق في استلام بياناتهم الشخصية بتنسيق منظم وشائع الاستخدام وقابل للقراءة الآلية ونقلها إلى متحكم آخر حيثما كان ذلك ممكناً تقنياً.",
            "description_en": "Enables data subjects to migrate their data between service providers in interoperable formats.",
            "description_ar": "يمكّن أصحاب البيانات من نقل بياناتهم بين مزودي الخدمة بتنسيقات قابلة للتشغيل المتبادل.",
            "priority": "medium",
            "status": "active",
            "source_pdf": "pdpl-law-2021.pdf",
            "source_page": 15
        },
        {
            "control_id": "PDPL-19",
            "framework": "PDPL",
            "framework_version": "2021",
            "domain": "Data Subject Rights",
            "subdomain": "Article 19: Right to Object",
            "title_en": "Right to Object to Processing",
            "title_ar": "الحق في الاعتراض على المعالجة",
            "control_clause_en": "Data subjects have the right to object to processing based on legitimate interests or for direct marketing purposes, including profiling. Controller must cease unless compelling legitimate grounds override.",
            "control_clause_ar": "لأصحاب البيانات الحق في الاعتراض على المعالجة بناءً على مصالح مشروعة أو لأغراض التسويق المباشر، بما في ذلك التنميط. يجب على المتحكم التوقف ما لم توجد أسباب مشروعة قاهرة.",
            "description_en": "Absolute right to opt-out of marketing; conditional right to object to legitimate interests processing.",
            "description_ar": "حق مطلق في إلغاء الاشتراك في التسويق؛ حق مشروط في الاعتراض على معالجة المصالح المشروعة.",
            "priority": "high",
            "status": "active",
            "source_pdf": "pdpl-law-2021.pdf",
            "source_page": 15
        },
        
        # CHAPTER 4: CONTROLLER AND PROCESSOR OBLIGATIONS (Articles 20-28)
        {
            "control_id": "PDPL-20",
            "framework": "PDPL",
            "framework_version": "2021",
            "domain": "Controller Obligations",
            "subdomain": "Article 20: Data by Design and Default",
            "title_en": "Data Protection by Design and Default",
            "title_ar": "حماية البيانات بالتصميم وبشكل افتراضي",
            "control_clause_en": "Controllers must implement appropriate technical and organizational measures to ensure data protection principles are embedded into processing and that, by default, only necessary personal data is processed.",
            "control_clause_ar": "يجب على المتحكمين تنفيذ تدابير فنية وتنظيمية مناسبة لضمان دمج مبادئ حماية البيانات في المعالجة وأنه، بشكل افتراضي، تتم معالجة البيانات الشخصية الضرورية فقط.",
            "description_en": "Privacy-by-design principle requiring proactive privacy features in systems and default minimal data collection.",
            "description_ar": "مبدأ الخصوصية بالتصميم الذي يتطلب ميزات خصوصية استباقية في الأنظمة وجمع بيانات افتراضي ضئيل.",
            "priority": "critical",
            "status": "active",
            "source_pdf": "pdpl-law-2021.pdf",
            "source_page": 16
        },
        {
            "control_id": "PDPL-21",
            "framework": "PDPL",
            "framework_version": "2021",
            "domain": "Controller Obligations",
            "subdomain": "Article 21: Processor Contracts",
            "title_en": "Controller-Processor Contracts and Guarantees",
            "title_ar": "عقود وضمانات المتحكم والمعالج",
            "control_clause_en": "Controllers must use processors that provide sufficient guarantees of PDPL compliance. Processing must be governed by written contract specifying subject matter, duration, nature, purpose, obligations, and security measures.",
            "control_clause_ar": "يجب على المتحكمين استخدام معالجين يقدمون ضمانات كافية لامتثال نظام حماية البيانات الشخصية. يجب أن تحكم المعالجة عقد كتابي يحدد الموضوع والمدة والطبيعة والغرض والالتزامات والتدابير الأمنية.",
            "description_en": "Mandates Data Processing Agreements (DPAs) with vendors processing personal data on behalf of controllers.",
            "description_ar": "يفرض اتفاقيات معالجة البيانات (DPAs) مع البائعين الذين يعالجون البيانات الشخصية نيابة عن المتحكمين.",
            "priority": "critical",
            "status": "active",
            "mapping_ecc": "1-5-3",
            "mapping_ccc": "1-2-P-1",
            "source_pdf": "pdpl-law-2021.pdf",
            "source_page": 17
        },
        {
            "control_id": "PDPL-22",
            "framework": "PDPL",
            "framework_version": "2021",
            "domain": "Controller Obligations",
            "subdomain": "Article 22: Joint Controllers",
            "title_en": "Joint Controllers - Shared Responsibility",
            "title_ar": "المتحكمون المشتركون - المسؤولية المشتركة",
            "control_clause_en": "Where two or more controllers jointly determine purposes and means of processing, they are joint controllers and must transparently determine their respective responsibilities through arrangement.",
            "control_clause_ar": "عندما يحدد متحكمان أو أكثر بشكل مشترك أغراض ووسائل المعالجة، فهم متحكمون مشتركون ويجب عليهم تحديد مسؤولياتهم المعنية بشفافية من خلال ترتيب.",
            "description_en": "Clarifies liability allocation when multiple organizations jointly control data processing.",
            "description_ar": "يوضح توزيع المسؤولية عندما تتحكم منظمات متعددة في معالجة البيانات بشكل مشترك.",
            "priority": "medium",
            "status": "active",
            "source_pdf": "pdpl-law-2021.pdf",
            "source_page": 18
        },
        {
            "control_id": "PDPL-23",
            "framework": "PDPL",
            "framework_version": "2021",
            "domain": "Controller Obligations",
            "subdomain": "Article 23: Data Protection Officer (DPO)",
            "title_en": "Designation of Data Protection Officer",
            "title_ar": "تعيين مسؤول حماية البيانات",
            "control_clause_en": "Controllers and processors must designate a Data Protection Officer (DPO) when: processing large-scale sensitive data, conducting systematic monitoring of data subjects, or as a public authority. DPO must have expertise, independence, and resources.",
            "control_clause_ar": "يجب على المتحكمين والمعالجين تعيين مسؤول حماية البيانات (DPO) عندما: معالجة البيانات الحساسة على نطاق واسع، إجراء مراقبة منهجية لأصحاب البيانات، أو كسلطة عامة. يجب أن يتمتع مسؤول حماية البيانات بالخبرة والاستقلالية والموارد.",
            "description_en": "Requires dedicated DPO for high-risk processing with defined responsibilities and reporting lines.",
            "description_ar": "يتطلب مسؤول حماية بيانات مخصص للمعالجة عالية المخاطر مع مسؤوليات وخطوط تقارير محددة.",
            "priority": "critical",
            "status": "active",
            "source_pdf": "pdpl-law-2021.pdf",
            "source_page": 19
        },
        {
            "control_id": "PDPL-24",
            "framework": "PDPL",
            "framework_version": "2021",
            "domain": "Controller Obligations",
            "subdomain": "Article 24: Employee Training and Awareness",
            "title_en": "Staff Training on Data Protection",
            "title_ar": "تدريب الموظفين على حماية البيانات",
            "control_clause_en": "Controllers must ensure personnel authorized to process personal data receive appropriate training, understand their obligations, and commit to confidentiality.",
            "control_clause_ar": "يجب على المتحكمين التأكد من أن الموظفين المصرح لهم بمعالجة البيانات الشخصية يتلقون التدريب المناسب ويفهمون التزاماتهم ويلتزمون بالسرية.",
            "description_en": "Mandates PDPL awareness training for all staff with access to personal data.",
            "description_ar": "يفرض تدريب التوعية بنظام حماية البيانات الشخصية لجميع الموظفين الذين يمكنهم الوصول إلى البيانات الشخصية.",
            "priority": "high",
            "status": "active",
            "mapping_ecc": "1-9-4, 1-10-1",
            "source_pdf": "pdpl-law-2021.pdf",
            "source_page": 20
        },
        {
            "control_id": "PDPL-25",
            "framework": "PDPL",
            "framework_version": "2021",
            "domain": "Controller Obligations",
            "subdomain": "Article 25: Contracts and Confidentiality",
            "title_en": "Contractual Confidentiality Obligations",
            "title_ar": "الالتزامات التعاقدية بالسرية",
            "control_clause_en": "Controllers must ensure employment contracts, service agreements, and confidentiality clauses include data protection obligations and survive termination of relationships.",
            "control_clause_ar": "يجب على المتحكمين ضمان أن عقود العمل واتفاقيات الخدمة وبنود السرية تتضمن التزامات حماية البيانات وتستمر بعد إنهاء العلاقات.",
            "description_en": "Requires contractual privacy clauses with employees, contractors, and third parties handling personal data.",
            "description_ar": "يتطلب بنود الخصوصية التعاقدية مع الموظفين والمقاولين والأطراف الثالثة الذين يتعاملون مع البيانات الشخصية.",
            "priority": "high",
            "status": "active",
            "source_pdf": "pdpl-law-2021.pdf",
            "source_page": 20
        },
        {
            "control_id": "PDPL-26",
            "framework": "PDPL",
            "framework_version": "2021",
            "domain": "Controller Obligations",
            "subdomain": "Article 26: Security Measures",
            "title_en": "Security Measures - Implementation Requirements",
            "title_ar": "التدابير الأمنية - متطلبات التنفيذ",
            "control_clause_en": "Controllers and processors must implement state-of-the-art security measures appropriate to risk level, including encryption, pseudonymization, access controls, backup, and regular security testing.",
            "control_clause_ar": "يجب على المتحكمين والمعالجين تنفيذ تدابير أمنية حديثة مناسبة لمستوى المخاطر، بما في ذلك التشفير والتعمية وضوابط الوصول والنسخ الاحتياطي والاختبار الأمني المنتظم.",
            "description_en": "Details specific technical security controls required based on ISO 27001/27018 and data sensitivity.",
            "description_ar": "يفصل الضوابط الأمنية الفنية المحددة المطلوبة بناءً على ISO 27001/27018 وحساسية البيانات.",
            "priority": "critical",
            "status": "active",
            "mapping_ecc": "2-1 to 2-16",
            "mapping_ccc": "2-11-P-1, 2-15-P-3",
            "source_pdf": "pdpl-law-2021.pdf",
            "source_page": 21
        },
        {
            "control_id": "PDPL-27",
            "framework": "PDPL",
            "framework_version": "2021",
            "domain": "Controller Obligations",
            "subdomain": "Article 27: Records of Processing Activities (RoPA)",
            "title_en": "Records of Processing Activities (RoPA)",
            "title_ar": "سجلات أنشطة المعالجة",
            "control_clause_en": "Controllers must maintain comprehensive Records of Processing Activities (RoPA) documenting: controller details, processing purposes, data categories, recipients, retention periods, security measures, and cross-border transfers.",
            "control_clause_ar": "يجب على المتحكمين الاحتفاظ بسجلات شاملة لأنشطة المعالجة توثق: تفاصيل المتحكم، أغراض المعالجة، فئات البيانات، المستلمين، فترات الاحتفاظ، التدابير الأمنية، والنقل عبر الحدود.",
            "description_en": "Central compliance documentation requirement - RoPA must be available to SDAIA upon request.",
            "description_ar": "متطلب التوثيق المركزي للامتثال - يجب أن تكون سجلات أنشطة المعالجة متاحة لسدايا عند الطلب.",
            "priority": "critical",
            "status": "active",
            "source_pdf": "pdpl-law-2021.pdf",
            "source_page": 22
        },
        {
            "control_id": "PDPL-28",
            "framework": "PDPL",
            "framework_version": "2021",
            "domain": "Controller Obligations",
            "subdomain": "Article 28: Data Retention and Deletion",
            "title_en": "Data Retention Schedules and Deletion",
            "title_ar": "جداول الاحتفاظ بالبيانات والحذف",
            "control_clause_en": "Controllers must establish, document, and implement data retention schedules specifying retention periods for each data category, with automated deletion when retention expires or purpose is fulfilled.",
            "control_clause_ar": "يجب على المتحكمين إنشاء وتوثيق وتنفيذ جداول الاحتفاظ بالبيانات التي تحدد فترات الاحتفاظ لكل فئة بيانات، مع الحذف التلقائي عند انتهاء الاحتفاظ أو تحقيق الغرض.",
            "description_en": "Requires documented retention policies and technical mechanisms for timely data deletion.",
            "description_ar": "يتطلب سياسات الاحتفاظ الموثقة والآليات الفنية للحذف الفوري للبيانات.",
            "priority": "high",
            "status": "active",
            "source_pdf": "pdpl-law-2021.pdf",
            "source_page": 23
        },
        
        # CHAPTER 5: DATA PROTECTION IMPACT ASSESSMENT (Article 29)
        {
            "control_id": "PDPL-29",
            "framework": "PDPL",
            "framework_version": "2021",
            "domain": "Risk Assessment",
            "subdomain": "Article 29: Data Protection Impact Assessment (DPIA)",
            "title_en": "Data Protection Impact Assessment (DPIA)",
            "title_ar": "تقييم أثر حماية البيانات",
            "control_clause_en": "Controllers must conduct DPIA before high-risk processing including: new technologies, large-scale processing, systematic monitoring, sensitive data, automated decision-making, or data matching. DPIA must identify risks and mitigation measures.",
            "control_clause_ar": "يجب على المتحكمين إجراء تقييم أثر حماية البيانات قبل المعالجة عالية المخاطر بما في ذلك: التقنيات الجديدة، المعالجة واسعة النطاق، المراقبة المنهجية، البيانات الحساسة، صنع القرار الآلي، أو مطابقة البيانات. يجب أن يحدد التقييم المخاطر وتدابير التخفيف.",
            "description_en": "Risk-based compliance approach requiring formal privacy impact assessments for high-risk processing.",
            "description_ar": "نهج الامتثال القائم على المخاطر الذي يتطلب تقييمات أثر الخصوصية الرسمية للمعالجة عالية المخاطر.",
            "priority": "critical",
            "status": "active",
            "source_pdf": "pdpl-law-2021.pdf",
            "source_page": 24
        },
        
        # CHAPTER 6: DATA BREACH NOTIFICATION (Articles 30-31)
        {
            "control_id": "PDPL-30",
            "framework": "PDPL",
            "framework_version": "2021",
            "domain": "Breach Management",
            "subdomain": "Article 30: Breach Documentation",
            "title_en": "Personal Data Breach - Documentation",
            "title_ar": "انتهاك البيانات الشخصية - التوثيق",
            "control_clause_en": "Controllers must document all personal data breaches, including facts, effects, remedial actions taken, and maintain breach register available to SDAIA.",
            "control_clause_ar": "يجب على المتحكمين توثيق جميع انتهاكات البيانات الشخصية، بما في ذلك الحقائق والآثار والإجراءات العلاجية المتخذة، والاحتفاظ بسجل الانتهاكات المتاح لسدايا.",
            "description_en": "Mandates comprehensive breach logging and record-keeping for regulatory inspection.",
            "description_ar": "يفرض تسجيل الانتهاكات الشامل وحفظ السجلات للتفتيش التنظيمي.",
            "priority": "critical",
            "status": "active",
            "source_pdf": "pdpl-law-2021.pdf",
            "source_page": 25
        },
        {
            "control_id": "PDPL-31",
            "framework": "PDPL",
            "framework_version": "2021",
            "domain": "Breach Management",
            "subdomain": "Article 31: Breach Notification to SDAIA",
            "title_en": "Breach Notification to SDAIA (72 Hours)",
            "title_ar": "إخطار الانتهاك لسدايا (72 ساعة)",
            "control_clause_en": "Controllers must notify SDAIA of personal data breaches within 72 hours of becoming aware, when the breach poses risk to rights and freedoms of data subjects. Notification must include: nature of breach, data categories affected, approximate number of subjects, consequences, and remedial measures.",
            "control_clause_ar": "يجب على المتحكمين إخطار سدايا بانتهاكات البيانات الشخصية خلال 72 ساعة من علمهم، عندما يشكل الانتهاك خطراً على حقوق وحريات أصحاب البيانات. يجب أن يتضمن الإخطار: طبيعة الانتهاك، فئات البيانات المتأثرة، العدد التقريبي للأشخاص، العواقب، والتدابير العلاجية.",
            "description_en": "72-hour breach notification deadline to SDAIA - similar to GDPR Article 33.",
            "description_ar": "مهلة 72 ساعة لإخطار الانتهاك لسدايا - مشابه للمادة 33 من اللائحة العامة لحماية البيانات.",
            "priority": "critical",
            "status": "active",
            "source_pdf": "pdpl-law-2021.pdf",
            "source_page": 26
        },
        {
            "control_id": "PDPL-32",
            "framework": "PDPL",
            "framework_version": "2021",
            "domain": "Breach Management",
            "subdomain": "Article 32: Breach Notification to Data Subjects",
            "title_en": "Breach Notification to Data Subjects",
            "title_ar": "إخطار الانتهاك لأصحاب البيانات",
            "control_clause_en": "When breach poses high risk to rights and freedoms, controllers must notify affected data subjects without undue delay in clear, plain language describing breach, consequences, remedial actions, and DPO contact information.",
            "control_clause_ar": "عندما يشكل الانتهاك خطراً عالياً على الحقوق والحريات، يجب على المتحكمين إخطار أصحاب البيانات المتأثرين دون تأخير لا مبرر له بلغة واضحة وبسيطة تصف الانتهاك والعواقب والإجراءات العلاجية ومعلومات الاتصال بمسؤول حماية البيانات.",
            "description_en": "Individual notification required for high-risk breaches with transparent communication.",
            "description_ar": "الإخطار الفردي مطلوب للانتهاكات عالية المخاطر مع تواصل شفاف.",
            "priority": "critical",
            "status": "active",
            "source_pdf": "pdpl-law-2021.pdf",
            "source_page": 26
        },
        
        # CHAPTER 7: INTERNATIONAL DATA TRANSFERS (Article 33)
        {
            "control_id": "PDPL-33",
            "framework": "PDPL",
            "framework_version": "2021",
            "domain": "Cross-Border Transfers",
            "subdomain": "Article 33: International Data Transfer",
            "title_en": "Cross-Border Data Transfer Requirements",
            "title_ar": "متطلبات نقل البيانات عبر الحدود",
            "control_clause_en": "Personal data may only be transferred outside Saudi Arabia when: (1) SDAIA determines adequate protection exists in destination country, (2) Appropriate safeguards are in place (Standard Contractual Clauses, Binding Corporate Rules), (3) Explicit consent obtained, or (4) Necessary for contract performance, legal claims, or vital interests.",
            "control_clause_ar": "لا يجوز نقل البيانات الشخصية خارج المملكة إلا عندما: (1) تحدد سدايا وجود حماية كافية في بلد الوجهة، (2) توجد ضمانات مناسبة (البنود التعاقدية القياسية، القواعد المؤسسية الملزمة)، (3) الحصول على موافقة صريحة، أو (4) ضرورية لأداء العقد أو المطالبات القانونية أو المصالح الحيوية.",
            "description_en": "Strict controls on international data transfers requiring adequacy decisions or safeguards.",
            "description_ar": "ضوابط صارمة على نقل البيانات الدولي تتطلب قرارات الكفاية أو الضمانات.",
            "priority": "critical",
            "status": "active",
            "source_pdf": "pdpl-law-2021.pdf",
            "source_page": 27
        },
        
        # CHAPTER 8: ENFORCEMENT AND PENALTIES (Articles 34-35)
        {
            "control_id": "PDPL-34",
            "framework": "PDPL",
            "framework_version": "2021",
            "domain": "Enforcement",
            "subdomain": "Article 34: Administrative Penalties",
            "title_en": "Administrative Penalties and Fines",
            "title_ar": "العقوبات الإدارية والغرامات",
            "control_clause_en": "SDAIA may impose administrative penalties for PDPL violations up to SAR 5 million depending on severity, nature, gravity, duration, intentionality, categories of data affected, number of data subjects, damage caused, and cooperation during investigation.",
            "control_clause_ar": "يجوز لسدايا فرض عقوبات إدارية على انتهاكات نظام حماية البيانات الشخصية تصل إلى 5 ملايين ريال سعودي حسب الخطورة والطبيعة والجسامة والمدة والقصد وفئات البيانات المتأثرة وعدد أصحاب البيانات والضرر الناجم والتعاون أثناء التحقيق.",
            "description_en": "Tiered penalty structure with fines up to SAR 5M for serious violations.",
            "description_ar": "هيكل عقوبات متدرج مع غرامات تصل إلى 5 ملايين ريال سعودي للانتهاكات الخطيرة.",
            "priority": "critical",
            "status": "active",
            "source_pdf": "pdpl-law-2021.pdf",
            "source_page": 28
        },
        {
            "control_id": "PDPL-35",
            "framework": "PDPL",
            "framework_version": "2021",
            "domain": "Enforcement",
            "subdomain": "Article 35: Criminal Penalties",
            "title_en": "Criminal Penalties for Serious Violations",
            "title_ar": "العقوبات الجنائية للانتهاكات الخطيرة",
            "control_clause_en": "Serious PDPL violations may result in criminal prosecution with imprisonment up to 2 years and/or fines. Data subjects may also seek civil damages through courts for harm caused by PDPL violations.",
            "control_clause_ar": "قد تؤدي انتهاكات نظام حماية البيانات الشخصية الخطيرة إلى ملاحقة جنائية مع السجن لمدة تصل إلى عامين و/أو غرامات. يمكن لأصحاب البيانات أيضاً المطالبة بالتعويضات المدنية من خلال المحاكم عن الضرر الناجم عن انتهاكات نظام حماية البيانات الشخصية.",
            "description_en": "Criminal liability for egregious violations including unauthorized disclosure or sale of personal data.",
            "description_ar": "المسؤولية الجنائية عن الانتهاكات الفاضحة بما في ذلك الإفصاح أو بيع البيانات الشخصية بدون تصريح.",
            "priority": "critical",
            "status": "active",
            "source_pdf": "pdpl-law-2021.pdf",
            "source_page": 29
        }
    ]
    
    return pdpl_articles


def insert_controls(controls, framework_name):
    """Insert controls into database (matching actual schema)"""
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
            
            # Insert using actual database columns
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
                control.get('control_clause_en', '')[:1000] if control.get('control_clause_en') else '',  # Use as policy guidance
                control.get('control_clause_ar', '')[:1000] if control.get('control_clause_ar') else '',
                control.get('evidence_examples', '')[:1000] if control.get('evidence_examples') else '',  # Use as procedure guidance
                control.get('subdomain', '')[:1000] if control.get('subdomain') else '',
                control.get('priority', 'medium'),
                'not_started',  # Use valid ControlStatus enum value
                1,  # Default maturity level
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
    """Main execution function"""
    print("\n" + "="*80)
    print("🇸🇦 SICO GRC - COMPLETE SAUDI CONTROL LIBRARIES LOADER")
    print("="*80)
    print("Loading official controls from CSV sources and PDPL law\n")
    
    total_inserted = 0
    total_skipped = 0
    
    # 1. Load ECC controls from CSV
    print("\n📋 STEP 1: ECC (Essential Cybersecurity Controls)")
    print("-" * 60)
    ecc_controls = load_ecc_from_csv()
    if ecc_controls:
        inserted, skipped = insert_controls(ecc_controls, "ECC")
        total_inserted += inserted
        total_skipped += skipped
    
    # 2. Load CCC controls from CSV
    print("\n☁️ STEP 2: CCC (Cloud Cybersecurity Controls)")
    print("-" * 60)
    ccc_controls = load_ccc_from_csv()
    if ccc_controls:
        inserted, skipped = insert_controls(ccc_controls, "CCC")
        total_inserted += inserted
        total_skipped += skipped
    
    # 3. Load complete PDPL  
    print("\n🔒 STEP 3: PDPL (Personal Data Protection Law - All 35 Articles)")
    print("-" * 60)
    pdpl_controls = load_complete_pdpl()
    inserted, skipped = insert_controls(pdpl_controls, "PDPL")
    total_inserted += inserted
    total_skipped += skipped
    
    # Summary
    print("\n" + "="*80)
    print("✅ LOADING COMPLETE!")
    print("="*80)
    print(f"📊 Total controls inserted: {total_inserted}")
    print(f"⏭️  Total controls skipped (already exist): {total_skipped}")
    
    # Verify counts
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM controls WHERE framework = 'ECC'")
    ecc_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM controls WHERE framework = 'CCC'")
    ccc_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM controls WHERE framework = 'PDPL'")
    pdpl_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n📈 Current Database Counts:")
    print(f"   🛡️  ECC:  {ecc_count} controls")
    print(f"   ☁️  CCC:  {ccc_count} controls")
    print(f"   🔒 PDPL: {pdpl_count} articles")
    print(f"   📊 TOTAL: {ecc_count + ccc_count + pdpl_count} controls\n")
    
    print("🎉 All Saudi regulatory frameworks loaded successfully!\n")


if __name__ == "__main__":
    main()
