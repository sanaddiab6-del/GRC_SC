"""
Script to add Arabic translations to all controls and evidence in the database
"""
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "src" / "backend"
sys.path.insert(0, str(backend_path))

import asyncio
from sqlalchemy import select
from core.database import AsyncSessionLocal
from controls.models import Control, FrameworkType
from evidence.models import Evidence

# Arabic translations for all controls
CONTROL_TRANSLATIONS = {
    "ECC-GV-1": {
        "title_ar": "الحوكمة التنظيمية السيبرانية",
        "description_ar": "يجب على المنظمة إنشاء إطار حوكمة للأمن السيبراني يتماشى مع الأهداف الاستراتيجية والمتطلبات التنظيمية."
    },
    "ECC-RM-1": {
        "title_ar": "عملية إدارة المخاطر السيبرانية",
        "description_ar": "تنفيذ منهجية منظمة لتحديد وتقييم ومعالجة مخاطر الأمن السيبراني بما يتماشى مع قبول المخاطر في المنظمة."
    },
    "ECC-AM-1": {
        "title_ar": "جرد الأصول",
        "description_ar": "الحفاظ على جرد شامل ومحدث لجميع أصول تكنولوجيا المعلومات بما في ذلك الأجهزة والبرامج والبيانات."
    },
    "ECC-AC-1": {
        "title_ar": "التحكم في الوصول",
        "description_ar": "تنفيذ ضوابط وصول قوية لتقييد الوصول إلى الموارد بناءً على مبدأ الامتياز الأدنى والحاجة إلى المعرفة."
    },
    "ECC-BC-1": {
        "title_ar": "استمرارية الأعمال والتعافي من الكوارث",
        "description_ar": "تطوير واختبار خطط استمرارية الأعمال والتعافي من الكوارث لضمان استمرار العمليات الحيوية."
    },
    "ECC-IR-1": {
        "title_ar": "الاستجابة للحوادث",
        "description_ar": "إنشاء قدرة الاستجابة للحوادث مع إجراءات موثقة للكشف والاستجابة والتعافي من حوادث الأمن السيبراني."
    },
    "ECC-NW-1": {
        "title_ar": "أمن الشبكات",
        "description_ar": "تنفيذ ضوابط تجزئة الشبكة والجدران النارية وأنظمة كشف التسلل لحماية البنية التحتية للشبكة."
    },
    "ECC-CR-1": {
        "title_ar": "التشفير وإدارة المفاتيح",
        "description_ar": "استخدام التشفير القوي لحماية البيانات الحساسة أثناء النقل والتخزين مع إدارة سليمة للمفاتيح."
    },
    "ECC-TA-1": {
        "title_ar": "التوعية والتدريب الأمني",
        "description_ar": "توفير برامج توعية وتدريب منتظمة للأمن السيبراني لجميع الموظفين والمقاولين."
    },
    "ECC-SC-1": {
        "title_ar": "أمن سلسلة التوريد",
        "description_ar": "تقييم وإدارة مخاطر الأمن السيبراني في سلسلة التوريد بما في ذلك موردي الطرف الثالث."
    },
    "ECC-VM-1": {
        "title_ar": "إدارة الثغرات الأمنية",
        "description_ar": "إنشاء برنامج لتحديد وتقييم ومعالجة الثغرات الأمنية في الأنظمة والتطبيقات في الوقت المناسب."
    },
    "CCC-GOV-01": {
        "title_ar": "حوكمة السحابة",
        "description_ar": "إنشاء إطار حوكمة شامل لاستخدام الحوسبة السحابية يتماشى مع سياسات المنظمة والمتطلبات التنظيمية."
    },
    "CCC-DATA-01": {
        "title_ar": "أمن البيانات السحابية",
        "description_ar": "تصنيف البيانات السحابية وحمايتها من خلال التشفير والتحكم في الوصول والنسخ الاحتياطي."
    },
    "CCC-IAM-01": {
        "title_ar": "إدارة الهوية والوصول السحابي",
        "description_ar": "تنفيذ ضوابط صارمة لإدارة الهوية والوصول للموارد السحابية مع المصادقة متعددة العوامل."
    },
    "CCC-MON-01": {
        "title_ar": "مراقبة الأمن السحابي",
        "description_ar": "مراقبة مستمرة لبيئات السحابة لاكتشاف والاستجابة للتهديدات الأمنية والشذوذ."
    },
    "CCC-NET-01": {
        "title_ar": "أمن الشبكات السحابية",
        "description_ar": "تنفيذ تجزئة الشبكة السحابية وضوابط حركة المرور والحماية من هجمات DDoS."
    },
    "CCC-BACK-01": {
        "title_ar": "النسخ الاحتياطي والاستعادة السحابية",
        "description_ar": "تنفيذ استراتيجيات النسخ الاحتياطي والاستعادة الشاملة للبيانات والخدمات السحابية."
    },
    "CCC-COM-01": {
        "title_ar": "الامتثال السحابي",
        "description_ar": "ضمان امتثال مزودي الخدمات السحابية للمتطلبات التنظيمية السعودية بما في ذلك PDPL و ECC."
    },
    "PDPL-1": {
        "title_ar": "الموافقة على معالجة البيانات",
        "description_ar": "الحصول على موافقة صريحة من أصحاب البيانات قبل جمع أو معالجة أو نقل البيانات الشخصية."
    },
    "PDPL-5": {
        "title_ar": "حقوق أصحاب البيانات",
        "description_ar": "تمكين أصحاب البيانات من ممارسة حقوقهم في الوصول والتصحيح والحذف ونقل بياناتهم الشخصية."
    },
    "PDPL-10": {
        "title_ar": "الحد الأدنى من جمع البيانات",
        "description_ar": "جمع البيانات الشخصية اللازمة فقط للأغراض المحددة والمشروعة والصريحة."
    },
    "PDPL-15": {
        "title_ar": "الإفصاح عن انتهاك البيانات",
        "description_ar": "الإبلاغ عن انتهاكات البيانات الشخصية إلى هيئة SDAIA وأصحاب البيانات المتضررين خلال 72 ساعة."
    },
    "PDPL-20": {
        "title_ar": "تقييم الأثر على حماية البيانات",
        "description_ar": "إجراء تقييمات أثر حماية البيانات للأنشطة عالية المخاطر التي تنطوي على معالجة بيانات شخصية."
    },
    "PDPL-25": {
        "title_ar": "نقل البيانات عبر الحدود",
        "description_ar": "ضمان حماية كافية عند نقل البيانات الشخصية خارج المملكة العربية السعودية."
    },
    "PDPL-30": {
        "title_ar": "الاحتفاظ بالبيانات وحذفها",
        "description_ar": "تحديد سياسات واضحة للاحتفاظ بالبيانات الشخصية وحذفها عند انتهاء الغرض أو المدة القانونية."
    },
    "PDPL-35": {
        "title_ar": "مسؤول حماية البيانات",
        "description_ar": "تعيين مسؤول حماية بيانات مؤهل لضمان الامتثال لمتطلبات PDPL."
    }
}

# Evidence translations
EVIDENCE_TRANSLATIONS = {
    "Cybersecurity Governance Charter": {
        "title_ar": "ميثاق الحوكمة السيبرانية",
        "description_ar": "وثيقة تحدد إطار الحوكمة السيبرانية والأدوار والمسؤوليات"
    },
    "Risk Assessment Report Q1 2026": {
        "title_ar": "تقرير تقييم المخاطر Q1 2026",
        "description_ar": "تقرير شامل لتحديد وتقييم المخاطر السيبرانية للربع الأول"
    },
    "Asset Inventory Database": {
        "title_ar": "قاعدة بيانات جرد الأصول",
        "description_ar": "سجل محدث لجميع أصول تكنولوجيا المعلومات في المنظمة"
    },
    "Access Control Policy v2.0": {
        "title_ar": "سياسة التحكم في الوصول v2.0",
        "description_ar": "سياسة شاملة للتحكم في الوصول إلى موارد تكنولوجيا المعلومات"
    },
    "Business Continuity Plan 2026": {
        "title_ar": "خطة استمرارية الأعمال 2026",
        "description_ar": "خطة موثقة لضمان استمرار العمليات الحيوية أثناء الحوادث"
    },
    "Incident Response Playbook": {
        "title_ar": "دليل الاستجابة للحوادث",
        "description_ar": "إجراءات محددة للاستجابة لحوادث الأمن السيبراني"
    },
    "Network Security Architecture": {
        "title_ar": "بنية أمن الشبكات",
        "description_ar": "مخططات ووثائق بنية الشبكة الآمنة"
    },
    "Encryption Standards Document": {
        "title_ar": "وثيقة معايير التشفير",
        "description_ar": "معايير التشفير وإدارة المفاتيح المعتمدة"
    },
    "Security Training Records 2026": {
        "title_ar": "سجلات التدريب الأمني 2026",
        "description_ar": "سجلات حضور وإتمام برامج التوعية الأمنية"
    },
    "Supplier Security Assessment": {
        "title_ar": "تقييم أمن الموردين",
        "description_ar": "تقييم أمني لموردي الطرف الثالث"
    },
    "Vulnerability Scan Report Jan 2026": {
        "title_ar": "تقرير فحص الثغرات يناير 2026",
        "description_ar": "نتائج فحص الثغرات الأمنية الشهري"
    },
    "Cloud Governance Framework": {
        "title_ar": "إطار حوكمة السحابة",
        "description_ar": "إطار شامل لإدارة وحوكمة الخدمات السحابية"
    },
    "Cloud Data Classification Matrix": {
        "title_ar": "مصفوفة تصنيف البيانات السحابية",
        "description_ar": "مصفوفة لتصنيف وحماية البيانات في البيئة السحابية"
    },
    "Cloud IAM Configuration": {
        "title_ar": "تكوين إدارة الهوية والوصول السحابي",
        "description_ar": "إعدادات وسياسات إدارة الهوية والوصول للموارد السحابية"
    },
    "SIEM Dashboard Configuration": {
        "title_ar": "تكوين لوحة SIEM",
        "description_ar": "إعدادات نظام معلومات الأمن وإدارة الأحداث"
    },
    "Data Consent Forms": {
        "title_ar": "نماذج موافقة البيانات",
        "description_ar": "نماذج موافقة موحدة لجمع ومعالجة البيانات الشخصية"
    },
    "Data Subject Rights Procedure": {
        "title_ar": "إجراءات حقوق أصحاب البيانات",
        "description_ar": "إجراءات للاستجابة لطلبات أصحاب البيانات"
    },
    "DPIA Template": {
        "title_ar": "نموذج تقييم أثر حماية البيانات",
        "description_ar": "نموذج موحد لإجراء تقييمات أثر حماية البيانات"
    },
    "Data Transfer Agreement": {
        "title_ar": "اتفاقية نقل البيانات",
        "description_ar": "اتفاقية قانونية لنقل البيانات الشخصية عبر الحدود"
    }
}


async def add_arabic_translations():
    """Add Arabic translations to all controls and evidence"""
    async with AsyncSessionLocal() as session:
        try:
            # Update controls
            result = await session.execute(select(Control))
            controls = result.scalars().all()
            
            updated_controls = 0
            for control in controls:
                control_id = str(control.control_id)
                if control_id in CONTROL_TRANSLATIONS:
                    translation = CONTROL_TRANSLATIONS[control_id]
                    setattr(control, 'title_ar', translation["title_ar"])
                    setattr(control, 'description_ar', translation["description_ar"])
                    updated_controls += 1
                    print(f"✅ Updated Arabic translation for {control_id}")
            
            await session.commit()
            print(f"\n✅ Updated {updated_controls} controls with Arabic translations")
            
            # Update evidence
            result = await session.execute(select(Evidence))
            evidences = result.scalars().all()
            
            updated_evidence = 0
            for evidence in evidences:
                title_en = str(evidence.title_en) if evidence.title_en is not None else ""
                if title_en in EVIDENCE_TRANSLATIONS:
                    translation = EVIDENCE_TRANSLATIONS[title_en]
                    setattr(evidence, 'title_ar', translation["title_ar"])
                    setattr(evidence, 'description_ar', translation["description_ar"])
                    updated_evidence += 1
                    print(f"✅ Updated Arabic translation for evidence: {title_en}")
            
            await session.commit()
            print(f"\n✅ Updated {updated_evidence} evidence records with Arabic translations")
            print(f"\n🎉 Arabic translation complete!")
            print(f"   Controls: {updated_controls}")
            print(f"   Evidence: {updated_evidence}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(add_arabic_translations())
