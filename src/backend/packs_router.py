"""
Commercial Packs API Router
Exposes metadata for pre-packaged compliance bundles (ECC, CCC, PDPL)
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


# ---------------------------------------------------------------------------
# Pack catalogue (static metadata - extend or load from DB as needed)
# ---------------------------------------------------------------------------

PACK_CATALOGUE = [
    {
        "pack_id": "ecc-baseline",
        "name_en": "ECC Baseline Pack",
        "name_ar": "حزمة خط الأساس للضوابط الأساسية",
        "framework": "ECC",
        "description_en": (
            "Ready-to-deploy bundle covering all 114 NCA Essential Cybersecurity Controls. "
            "Includes evidence templates, bilingual policies, implementation playbooks, "
            "and an executive reporting kit."
        ),
        "description_ar": (
            "حزمة جاهزة للنشر تغطي جميع ضوابط الأمن السيبراني الأساسية للهيئة الوطنية للأمن السيبراني "
            "وعددها 114 ضابطاً. تتضمن قوالب الأدلة والسياسات ثنائية اللغة وكتيبات التنفيذ وعدة التقارير التنفيذية."
        ),
        "controls_count": 114,
        "evidence_templates": 45,
        "deployment_months": 6,
        "effort_person_days": 180,
        "tier": "standard",
        "features": [
            "114 ECC control library",
            "Bilingual policy templates",
            "Evidence collection checklist",
            "90-day implementation playbook",
            "Executive reporting templates",
            "ISO 27001 cross-mapping",
        ],
    },
    {
        "pack_id": "ccc-cloud",
        "name_en": "CCC Cloud Pack",
        "name_ar": "حزمة ضوابط الأمن السيبراني السحابي",
        "framework": "CCC",
        "description_en": (
            "Cloud-specific compliance bundle covering 107 NCA CCC controls beyond the ECC baseline. "
            "Includes shared responsibility matrices, cloud architecture guidance, and multi-cloud playbooks."
        ),
        "description_ar": (
            "حزمة امتثال سحابية متخصصة تغطي 107 ضابطاً فريداً من ضوابط الأمن السيبراني السحابي "
            "للهيئة الوطنية للأمن السيبراني. تتضمن مصفوفات المسؤولية المشتركة وإرشادات الهندسة السحابية."
        ),
        "controls_count": 107,
        "evidence_templates": 30,
        "deployment_months": 5,
        "effort_person_days": 150,
        "tier": "standard",
        "prerequisites": ["ecc-baseline"],
        "features": [
            "107 CCC delta control library",
            "Shared responsibility matrices",
            "Cloud security architecture guidance",
            "Container & serverless playbooks",
            "Multi-cloud governance templates",
        ],
    },
    {
        "pack_id": "pdpl-privacy",
        "name_en": "PDPL Privacy Pack",
        "name_ar": "حزمة الامتثال لنظام حماية البيانات الشخصية",
        "framework": "PDPL",
        "description_en": (
            "Comprehensive PDPL compliance kit covering 28 operational controls. "
            "Includes 7 privacy registers (RoPA, DSAR log, Breach log, Consent log, etc.), "
            "bilingual privacy policies, and a 72-hour breach notification workflow."
        ),
        "description_ar": (
            "مجموعة شاملة للامتثال لنظام حماية البيانات الشخصية تغطي 28 ضابطاً تشغيلياً. "
            "تتضمن 7 سجلات خصوصية وسياسات خصوصية ثنائية اللغة وسير عمل إشعار الاختراق خلال 72 ساعة."
        ),
        "controls_count": 28,
        "evidence_templates": 20,
        "deployment_months": 3,
        "effort_person_days": 60,
        "tier": "standard",
        "features": [
            "28 PDPL operational controls",
            "7 privacy registers (RoPA, DSAR, Breach, Consent, etc.)",
            "Bilingual privacy policy templates",
            "DSAR response workflow (<30 days)",
            "72-hour breach notification procedure",
            "DPO appointment guidelines",
        ],
    },
]

PACK_INDEX = {p["pack_id"]: p for p in PACK_CATALOGUE}


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class PackSummary(BaseModel):
    pack_id: str
    name_en: str
    name_ar: str
    framework: str
    controls_count: int
    deployment_months: int
    tier: str


class PackDetail(PackSummary):
    description_en: str
    description_ar: str
    evidence_templates: int
    effort_person_days: int
    features: List[str]
    prerequisites: Optional[List[str]] = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/packs", response_model=List[PackSummary])
async def list_packs(framework: Optional[str] = None):
    """
    List available commercial compliance packs.
    Optionally filter by framework (ECC, CCC, PDPL).
    """
    packs = PACK_CATALOGUE
    if framework:
        packs = [p for p in packs if p["framework"].upper() == framework.upper()]
    return packs


@router.get("/packs/{pack_id}", response_model=PackDetail)
async def get_pack(pack_id: str):
    """Get detailed information about a specific compliance pack."""
    pack = PACK_INDEX.get(pack_id)
    if not pack:
        raise HTTPException(
            status_code=404,
            detail={
                "message_en": f"Pack '{pack_id}' not found",
                "message_ar": f"الحزمة '{pack_id}' غير موجودة",
            },
        )
    return pack
