"""
Add Arabic translations to requirement nodes in batches.
"""
import re

TERM_TRANSLATIONS = {
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
    "Encryption": "التشفير",
    "Authentication": "المصادقة",
    "Authorization": "التفويض",
    "Network security": "أمن الشبكات",
    "Physical security": "الأمن المادي",
    "Awareness": "التوعية",
    "Training": "التدريب",
    "Monitoring": "المراقبة",
    "Logging": "التسجيل",
    "Backup": "النسخ الاحتياطي",
    "Recovery": "الاستعادة",
    "Governance": "الحوكمة",
    "Management": "الإدارة",
    "Operations": "العمليات",
    "Maintenance": "الصيانة",
    "Documentation": "التوثيق",
    "Assessment": "التقييم",
    "Implementation": "التطبيق",
    "Planning": "التخطيط",
    "Improvement": "التحسين",
    "Communication": "الاتصال",
    "Supplier": "المورد",
    "Third party": "الطرف الثالث",
    "Cloud": "السحابة",
    "Software": "البرمجيات",
    "Hardware": "الأجهزة",
    "Infrastructure": "البنية التحتية",
    "Change management": "إدارة التغيير",
    "Availability": "التوفر",
    "Integrity": "النزاهة",
    "Confidentiality": "السرية",
    "Resilience": "المرونة",
    "Continuity": "الاستمرارية",
    "Testing": "الاختبار",
}

sorted_terms = sorted(TERM_TRANSLATIONS.items(), key=lambda x: len(x[0]), reverse=True)

def translate_text(text):
    if not text:
        return text
    result = text
    for en, ar in sorted_terms:
        result = re.sub(re.escape(en), ar, result, flags=re.IGNORECASE)
    return result

from core.models import RequirementNode, ReferenceControl, Threat
from django.db import connection

# Batch update using raw SQL for performance
print("Translating requirement nodes in bulk...")
nodes = RequirementNode.objects.filter(translations={}).count()
nodes2 = RequirementNode.objects.exclude(translations__has_key='ar').count()
print(f"  Nodes without any translations: {nodes}")
print(f"  Nodes without Arabic: {nodes2}")

batch_size = 200
updated = 0
offset = 0

while True:
    batch = list(RequirementNode.objects.exclude(translations__has_key='ar').only('id', 'name', 'description', 'translations')[:batch_size])
    if not batch:
        break
    
    for node in batch:
        translations = node.translations or {}
        ar_trans = {}
        if node.name:
            ar_trans['name'] = translate_text(node.name)
        if node.description:
            ar_trans['description'] = translate_text(node.description)
        if ar_trans:
            translations['ar'] = ar_trans
            node.translations = translations
    
    RequirementNode.objects.bulk_update(batch, ['translations'], batch_size=100)
    updated += len(batch)
    print(f"  Updated {updated} nodes...")

print(f"  Total requirement nodes updated: {updated}")

# Reference Controls
print("Translating reference controls...")
ctrl_updated = 0
while True:
    batch = list(ReferenceControl.objects.exclude(translations__has_key='ar').only('id', 'name', 'description', 'translations')[:batch_size])
    if not batch:
        break
    
    for ctrl in batch:
        translations = ctrl.translations or {}
        ar_trans = {}
        if ctrl.name:
            ar_trans['name'] = translate_text(ctrl.name)
        if ctrl.description:
            ar_trans['description'] = translate_text(ctrl.description)
        if ar_trans:
            translations['ar'] = ar_trans
            ctrl.translations = translations
    
    ReferenceControl.objects.bulk_update(batch, ['translations'], batch_size=100)
    ctrl_updated += len(batch)
    print(f"  Updated {ctrl_updated} controls...")

print(f"  Total reference controls updated: {ctrl_updated}")

# Threats
print("Translating threats...")
threat_updated = 0
while True:
    batch = list(Threat.objects.exclude(translations__has_key='ar').only('id', 'name', 'description', 'translations')[:batch_size])
    if not batch:
        break
    
    for t in batch:
        translations = t.translations or {}
        ar_trans = {}
        if t.name:
            ar_trans['name'] = translate_text(t.name)
        if t.description:
            ar_trans['description'] = translate_text(t.description)
        if ar_trans:
            translations['ar'] = ar_trans
            t.translations = translations
    
    Threat.objects.bulk_update(batch, ['translations'], batch_size=100)
    threat_updated += len(batch)
    print(f"  Updated {threat_updated} threats...")

print(f"  Total threats updated: {threat_updated}")
print("\n=== COMPLETE ===")
