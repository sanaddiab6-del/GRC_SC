"""
Add Arabic translations to all frameworks, requirement nodes, and reference controls.
This script translates the name and description fields.
"""
import json

# Arabic translations for common security/compliance terms
TERM_TRANSLATIONS = {
    # Framework-level terms
    "Information security": "أمن المعلومات",
    "Cybersecurity": "الأمن السيبراني",
    "Risk management": "إدارة المخاطر",
    "Risk assessment": "تقييم المخاطر",
    "Access control": "التحكم في الوصول",
    "Audit": "التدقيق",
    "Compliance": "الامتثال",
    "Policy": "السياسة",
    "Policies": "السياسات",
    "Procedure": "الإجراء",
    "Procedures": "الإجراءات",
    "Control": "الضابط",
    "Controls": "الضوابط",
    "Framework": "إطار العمل",
    "Standard": "المعيار",
    "Requirement": "المتطلب",
    "Requirements": "المتطلبات",
    "Security": "الأمن",
    "Privacy": "الخصوصية",
    "Data protection": "حماية البيانات",
    "Incident": "الحادث",
    "Incident management": "إدارة الحوادث",
    "Business continuity": "استمرارية الأعمال",
    "Disaster recovery": "التعافي من الكوارث",
    "Vulnerability": "الثغرة",
    "Threat": "التهديد",
    "Asset": "الأصل",
    "Asset management": "إدارة الأصول",
    "Configuration": "التكوين",
    "Encryption": "التشفير",
    "Authentication": "المصادقة",
    "Authorization": "التفويض",
    "Network": "الشبكة",
    "Network security": "أمن الشبكات",
    "Physical security": "الأمن المادي",
    "Personnel": "الموظفون",
    "Human resources": "الموارد البشرية",
    "Awareness": "التوعية",
    "Training": "التدريب",
    "Monitoring": "المراقبة",
    "Logging": "التسجيل",
    "Backup": "النسخ الاحتياطي",
    "Recovery": "الاستعادة",
    "Governance": "الحوكمة",
    "Organization": "المنظمة",
    "Management": "الإدارة",
    "Operations": "العمليات",
    "Maintenance": "الصيانة",
    "Documentation": "التوثيق",
    "Review": "المراجعة",
    "Assessment": "التقييم",
    "Evaluation": "التقييم",
    "Implementation": "التطبيق",
    "Planning": "التخطيط",
    "Improvement": "التحسين",
    "Communication": "الاتصال",
    "Supplier": "المورد",
    "Third party": "الطرف الثالث",
    "Cloud": "السحابة",
    "Application": "التطبيق",
    "Software": "البرمجيات",
    "Hardware": "الأجهزة",
    "Infrastructure": "البنية التحتية",
    "Change management": "إدارة التغيير",
    "Capacity": "القدرة",
    "Availability": "التوفر",
    "Integrity": "النزاهة",
    "Confidentiality": "السرية",
    "Resilience": "المرونة",
    "Continuity": "الاستمرارية",
    "Testing": "الاختبار",
    "Maturity": "النضج",
}

# Full framework name translations
FRAMEWORK_NAME_TRANSLATIONS = {
    "iso27001-2022": "المعيار الدولي ISO/IEC 27001:2022 - نظام إدارة أمن المعلومات",
    "iso27001-2013": "المعيار الدولي ISO/IEC 27001:2013 - نظام إدارة أمن المعلومات",
    "iso22301-2019": "المعيار الدولي ISO 22301:2019 - إدارة استمرارية الأعمال",
    "iso42001-2023": "المعيار الدولي ISO/IEC 42001:2023 - نظام إدارة الذكاء الاصطناعي",
    "nist-csf-2.0": "إطار الأمن السيبراني NIST الإصدار 2.0",
    "nist-csf-1.1": "إطار الأمن السيبراني NIST الإصدار 1.1",
    "nist-sp-800-53-rev5": "NIST SP 800-53 المراجعة 5 - ضوابط الأمان والخصوصية",
    "nist-sp-800-171-rev2": "NIST SP 800-171 المراجعة 2 - حماية المعلومات غير المصنفة الخاضعة للرقابة",
    "gdpr": "اللائحة العامة لحماية البيانات (GDPR)",
    "gdpr-checklist": "قائمة التحقق من اللائحة العامة لحماية البيانات",
    "dora": "قانون المرونة التشغيلية الرقمية (DORA)",
    "soc2-2017": "SOC 2 - معايير خدمات الثقة 2017",
    "soc2-2017-rev-2022": "SOC 2 - معايير خدمات الثقة (مراجعة 2022)",
    "pci-dss-4.0": "معيار أمن بيانات صناعة بطاقات الدفع PCI DSS 4.0",
    "cmmc-2.0": "نموذج شهادة نضج الأمن السيبراني CMMC 2.0",
    "sama-csf-1.0": "إطار الأمن السيبراني لمؤسسة النقد العربي السعودي (ساما)",
    "ecc-1": "الضوابط الأساسية للأمن السيبراني (ECC-1) - الهيئة الوطنية للأمن السيبراني",
    "nca-cscc-1": "ضوابط الأمن السيبراني للحوسبة السحابية - الهيئة الوطنية للأمن السيبراني",
    "nca-dcc-1": "ضوابط الأمن السيبراني للبيانات - الهيئة الوطنية للأمن السيبراني",
    "nca-tcc-1": "ضوابط الأمن السيبراني للاتصالات - الهيئة الوطنية للأمن السيبراني",
    "ai-act": "قانون الذكاء الاصطناعي للاتحاد الأوروبي",
    "essential-eight": "الثمانية الأساسية - استراتيجيات التخفيف",
    "hipaa-security-rule-2003": "قاعدة أمان HIPAA",
    "fedramp-rev5": "FedRAMP المراجعة 5",
    "cis-controls-v8": "ضوابط CIS الإصدار 8",
    "cis-controls-v8.1": "ضوابط CIS الإصدار 8.1",
    "ccpa_act": "قانون خصوصية المستهلك في كاليفورنيا (CCPA)",
    "rnsi-algerie-2020": "المرجعية الوطنية لأمن نظم المعلومات - الجزائر 2020",
    "referentiel-audit-ssi-ancs-tunisie": "مرجعية تدقيق أمن نظم المعلومات - تونس",
    "tiber-eu-2018": "إطار TIBER-EU للاختبار القائم على التهديدات",
    "tisax-v6.0.2": "TISAX الإصدار 6.0.2 - أمن المعلومات في صناعة السيارات",
    "tisax-v5.1": "TISAX الإصدار 5.1 - أمن المعلومات في صناعة السيارات",
}

# Description translations for key frameworks
FRAMEWORK_DESC_TRANSLATIONS = {
    "iso27001-2022": "يحدد المعيار ISO/IEC 27001:2022 متطلبات إنشاء وتنفيذ وصيانة وتحسين نظام إدارة أمن المعلومات بشكل مستمر",
    "nist-csf-2.0": "يوفر إطار الأمن السيبراني NIST إرشادات للمنظمات لإدارة مخاطر الأمن السيبراني وتقليلها",
    "gdpr": "اللائحة العامة لحماية البيانات هي لائحة في قانون الاتحاد الأوروبي بشأن حماية البيانات والخصوصية",
    "dora": "قانون المرونة التشغيلية الرقمية يهدف إلى ضمان قدرة القطاع المالي على الصمود في وجه الاضطرابات التشغيلية الشديدة",
    "sama-csf-1.0": "إطار الأمن السيبراني الصادر عن البنك المركزي السعودي لتعزيز الأمن السيبراني في القطاع المالي",
    "ecc-1": "الضوابط الأساسية للأمن السيبراني الصادرة عن الهيئة الوطنية للأمن السيبراني في المملكة العربية السعودية",
}

def translate_text(text):
    """Simple translation using term dictionary - replaces known terms."""
    if not text:
        return text
    result = text
    # Sort by length (longest first) to avoid partial replacements
    sorted_terms = sorted(TERM_TRANSLATIONS.items(), key=lambda x: len(x[0]), reverse=True)
    for en, ar in sorted_terms:
        # Case-insensitive replacement
        import re
        result = re.sub(re.escape(en), ar, result, flags=re.IGNORECASE)
    return result


from core.models import Framework, RequirementNode, ReferenceControl, LoadedLibrary, Threat
from django.db import transaction

updated_fw = 0
updated_nodes = 0
updated_controls = 0
updated_libs = 0
updated_threats = 0

with transaction.atomic():
    # 1. Translate Frameworks
    print("Translating frameworks...")
    for fw in Framework.objects.all():
        translations = fw.translations or {}
        if 'ar' not in translations:
            # Extract framework key from URN
            fw_key = fw.urn.split(':')[-1] if fw.urn else ''
            
            ar_trans = {}
            if fw_key in FRAMEWORK_NAME_TRANSLATIONS:
                ar_trans['name'] = FRAMEWORK_NAME_TRANSLATIONS[fw_key]
            else:
                ar_trans['name'] = translate_text(fw.name)
            
            if fw_key in FRAMEWORK_DESC_TRANSLATIONS:
                ar_trans['description'] = FRAMEWORK_DESC_TRANSLATIONS[fw_key]
            elif fw.description:
                ar_trans['description'] = translate_text(fw.description)
            
            translations['ar'] = ar_trans
            fw.translations = translations
            fw.save(update_fields=['translations'])
            updated_fw += 1
    
    print(f"  Updated {updated_fw} frameworks")
    
    # 2. Translate Requirement Nodes
    print("Translating requirement nodes...")
    for node in RequirementNode.objects.all().iterator(chunk_size=500):
        translations = node.translations or {}
        if 'ar' not in translations:
            ar_trans = {}
            if node.name:
                ar_trans['name'] = translate_text(node.name)
            if node.description:
                ar_trans['description'] = translate_text(node.description)
            if ar_trans:
                translations['ar'] = ar_trans
                node.translations = translations
                node.save(update_fields=['translations'])
                updated_nodes += 1
    
    print(f"  Updated {updated_nodes} requirement nodes")
    
    # 3. Translate Reference Controls
    print("Translating reference controls...")
    for ctrl in ReferenceControl.objects.all().iterator(chunk_size=500):
        translations = ctrl.translations or {}
        if 'ar' not in translations:
            ar_trans = {}
            if ctrl.name:
                ar_trans['name'] = translate_text(ctrl.name)
            if ctrl.description:
                ar_trans['description'] = translate_text(ctrl.description)
            if ar_trans:
                translations['ar'] = ar_trans
                ctrl.translations = translations
                ctrl.save(update_fields=['translations'])
                updated_controls += 1
    
    print(f"  Updated {updated_controls} reference controls")
    
    # 4. Translate Loaded Libraries
    print("Translating loaded libraries...")
    for lib in LoadedLibrary.objects.all():
        translations = lib.translations or {}
        if 'ar' not in translations:
            lib_key = lib.urn.split(':')[-1] if lib.urn else ''
            ar_trans = {}
            if lib.name:
                ar_trans['name'] = translate_text(lib.name)
            if lib.description:
                ar_trans['description'] = translate_text(lib.description)
            if ar_trans:
                translations['ar'] = ar_trans
                lib.translations = translations
                lib.save(update_fields=['translations'])
                updated_libs += 1
    
    print(f"  Updated {updated_libs} loaded libraries")
    
    # 5. Translate Threats
    print("Translating threats...")
    for threat in Threat.objects.all():
        translations = threat.translations or {}
        if 'ar' not in translations:
            ar_trans = {}
            if threat.name:
                ar_trans['name'] = translate_text(threat.name)
            if threat.description:
                ar_trans['description'] = translate_text(threat.description)
            if ar_trans:
                translations['ar'] = ar_trans
                threat.translations = translations
                threat.save(update_fields=['translations'])
                updated_threats += 1
    
    print(f"  Updated {updated_threats} threats")

print(f"\n=== COMPLETE ===")
print(f"Frameworks: {updated_fw}")
print(f"Requirement Nodes: {updated_nodes}")
print(f"Reference Controls: {updated_controls}")
print(f"Loaded Libraries: {updated_libs}")
print(f"Threats: {updated_threats}")
