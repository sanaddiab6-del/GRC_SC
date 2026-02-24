"""
Load ECC, CCC, PDPL controls from official CSV files into the sanadcom SQLite database.
Run from: sanadcom/src/backend/
"""
import asyncio
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DATABASE_URL', 'sqlite+aiosqlite:///./sico_grc.db')
os.environ.setdefault('SECRET_KEY', 'sico-grc-dev-secret-key-32chars-minimum-safe')

from sqlalchemy import select
from core.database import AsyncSessionLocal, init_db
from controls.models import Control, FrameworkType, ControlStatus

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'controls')

# Minimal Arabic translation dictionary for domain names
ARABIC = {
    'Cybersecurity Governance': 'حوكمة الأمن السيبراني',
    'Cybersecurity Defense': 'الدفاع السيبراني',
    'Cybersecurity Resilience': 'مرونة الأمن السيبراني',
    'Third-Party Cybersecurity': 'أمن سيبراني طرف ثالث',
    'Cloud Security Governance': 'حوكمة أمن السحابة',
    'Cloud Security Defense': 'الدفاع الأمني السحابي',
    'Cloud Security Resilience': 'مرونة الأمن السحابي',
    'Personal Data Protection': 'حماية البيانات الشخصية',
}


def ar(text: str) -> str:
    return ARABIC.get(text, text)


async def load():
    await init_db()

    async with AsyncSessionLocal() as db:
        # Count existing
        res = await db.execute(select(Control))
        existing = {c.control_id for c in res.scalars().all()}
        print(f"[CSV Loader] Existing controls: {len(existing)}")

        added = 0

        # --- ECC ---
        ecc_path = os.path.normpath(os.path.join(DATA_DIR, 'ecc_controls.csv'))
        if os.path.exists(ecc_path):
            with open(ecc_path, encoding='utf-8') as f:
                for row in csv.DictReader(f):
                    cid = row.get('Control_ID', '').strip()
                    if not cid or cid in existing:
                        continue
                    domain = row.get('Domain', 'General').strip()
                    clause = row.get('Control_Clause', '').strip()
                    subdomain = row.get('Subdomain', domain).strip()
                    ctrl = Control(
                        control_id=cid,
                        framework=FrameworkType.ECC,
                        domain=domain,
                        title_en=subdomain or domain,
                        title_ar=ar(domain),
                        description_en=clause[:500] if clause else domain,
                        description_ar=ar(domain),
                        priority='high',
                        status=ControlStatus.NOT_STARTED,
                        maturity_level=1,
                        evidence_types=["POLICY", "PROCEDURE"],
                        related_controls={},
                    )
                    db.add(ctrl)
                    existing.add(cid)
                    added += 1
            print(f"[CSV Loader] ECC from CSV: added {added} so far")

        # --- CCC ---
        ccc_before = added
        ccc_path = os.path.normpath(os.path.join(DATA_DIR, 'ccc_controls.csv'))
        if os.path.exists(ccc_path):
            with open(ccc_path, encoding='utf-8') as f:
                for row in csv.DictReader(f):
                    cid = row.get('Control_ID', '').strip()
                    if not cid or cid in existing:
                        continue
                    domain = row.get('Domain', 'Cloud Security').strip()
                    clause = row.get('Control_Clause', '').strip()
                    subdomain = row.get('Subdomain', domain).strip()
                    ctrl = Control(
                        control_id=cid,
                        framework=FrameworkType.CCC,
                        domain=domain,
                        title_en=subdomain or domain,
                        title_ar=ar(domain),
                        description_en=clause[:500] if clause else domain,
                        description_ar=ar(domain),
                        priority='high',
                        status=ControlStatus.NOT_STARTED,
                        maturity_level=1,
                        evidence_types=["POLICY", "CONFIG"],
                        related_controls={},
                    )
                    db.add(ctrl)
                    existing.add(cid)
                    added += 1
            print(f"[CSV Loader] CCC from CSV: added {added - ccc_before}")

        # --- PDPL ---
        pdpl_before = added
        pdpl_path = os.path.normpath(os.path.join(DATA_DIR, 'pdpl_controls.csv'))
        if os.path.exists(pdpl_path):
            with open(pdpl_path, encoding='utf-8') as f:
                for row in csv.DictReader(f):
                    cid = row.get('Control_ID', '').strip()
                    if not cid or cid in existing:
                        continue
                    domain = row.get('Domain', 'Data Protection').strip()
                    clause = row.get('Control_Clause', '').strip()
                    subdomain = row.get('Subdomain', domain).strip()
                    ctrl = Control(
                        control_id=cid,
                        framework=FrameworkType.PDPL,
                        domain=domain,
                        title_en=subdomain or domain,
                        title_ar=ar(domain),
                        description_en=clause[:500] if clause else domain,
                        description_ar=ar(domain),
                        priority='high',
                        status=ControlStatus.NOT_STARTED,
                        maturity_level=1,
                        evidence_types=["POLICY", "RECORD"],
                        related_controls={},
                    )
                    db.add(ctrl)
                    existing.add(cid)
                    added += 1
            print(f"[CSV Loader] PDPL from CSV: added {added - pdpl_before}")

        await db.commit()

        # Final count
        res2 = await db.execute(select(Control))
        total = len(res2.scalars().all())
        print(f"[CSV Loader] Done. Added {added} new controls. Total in DB: {total}")


if __name__ == '__main__':
    asyncio.run(load())
