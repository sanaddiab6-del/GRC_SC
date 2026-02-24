#!/usr/bin/env python3
"""Load all three CSV files (ECC, CCC, PDPL) into the SICO GRC database."""

import asyncio
import csv
import os
import re
import sys
from pathlib import Path

# â”€â”€â”€ path bootstrap â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
BACKEND_DIR = Path(__file__).parent
sys.path.insert(0, str(BACKEND_DIR))

os.environ.setdefault("SECRET_KEY", "sico-grc-dev-secret-key-32chars-minimum-safe")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./sico_grc.db")
os.environ.setdefault("DEBUG", "True")
os.environ.setdefault("TLS_ENABLED", "False")
os.environ.setdefault("RATE_LIMIT_ENABLED", "False")

from sqlalchemy import select, text
from core.database import engine, AsyncSessionLocal
from controls.models import Control, ControlStatus, FrameworkType as Framework

DOWNLOADS = Path("C:/Users/Shahd/Downloads")

# â”€â”€â”€ ECC loader â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
async def load_ecc(session):
    ecc_file = DOWNLOADS / "ECC_Full_Controls_Extracted.csv"
    if not ecc_file.exists():
        print(f"  [SKIP] ECC file not found: {ecc_file}")
        return 0

    # fetch existing control_ids
    existing = set(r[0] for r in (await session.execute(
        select(Control.control_id).where(Control.framework == Framework.ECC)
    )).all())

    rows = []
    with open(ecc_file, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cid = row.get("Control_ID", "").strip()
            if not cid:
                continue
            full_id = f"ECC-{cid}"
            if full_id in existing:
                continue

            domain = row.get("Domain", "").strip()
            subdomain = row.get("Subdomain", "").strip()
            clause = row.get("Control_Clause", "").strip()

            # infer priority from domain prefix number
            top = cid.split("-")[0] if "-" in cid else cid.split(".")[0]
            priority = "CRITICAL" if top in ("1",) else "HIGH"

            c = Control(
                control_id=full_id,
                framework=Framework.ECC,
                domain=domain or "Cybersecurity Governance",
                title_en=subdomain or clause[:120] or full_id,
                title_ar=subdomain or clause[:120] or full_id,
                description_en=clause or subdomain,
                description_ar=clause or subdomain,
                priority=priority,
                status=ControlStatus.NOT_STARTED,
                maturity_level=1,
                evidence_types=[],
                related_controls=[],
            )
            session.add(c)
            rows.append(full_id)

    await session.flush()
    return len(rows)


# â”€â”€â”€ CCC loader â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
async def load_ccc(session):
    ccc_file = DOWNLOADS / "CCC_Full_Controls_Extracted_EN.csv"
    if not ccc_file.exists():
        print(f"  [SKIP] CCC file not found: {ccc_file}")
        return 0

    existing = set(r[0] for r in (await session.execute(
        select(Control.control_id).where(Control.framework == Framework.CCC)
    )).all())

    rows = []
    with open(ccc_file, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cid = row.get("Control_ID", "").strip()
            if not cid:
                continue
            full_id = f"CCC-{cid}"
            if full_id in existing:
                continue

            domain = row.get("Domain", "").strip()
            subdomain = row.get("Subdomain", "").strip()
            clause = row.get("Control_Clause", "").strip()

            # priority based on depth: -P-1-x are sub-controls (HIGH), -P-1 are CRITICAL
            depth = cid.count("-")
            priority = "CRITICAL" if depth <= 2 else "HIGH"

            c = Control(
                control_id=full_id,
                framework=Framework.CCC,
                domain=domain or "Cybersecurity Governance",
                title_en=subdomain or clause[:120] or full_id,
                title_ar=subdomain or clause[:120] or full_id,
                description_en=clause or subdomain,
                description_ar=clause or subdomain,
                priority=priority,
                status=ControlStatus.NOT_STARTED,
                maturity_level=1,
                evidence_types=[],
                related_controls=[],
            )
            session.add(c)
            rows.append(full_id)

    await session.flush()
    return len(rows)


# â”€â”€â”€ PDPL loader â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
async def load_pdpl(session):
    pdpl_file = DOWNLOADS / "PDPL_Obligation_Based_Control_Library_GRC_Ready.csv"
    if not pdpl_file.exists():
        print(f"  [SKIP] PDPL file not found: {pdpl_file}")
        return 0

    existing = set(r[0] for r in (await session.execute(
        select(Control.control_id).where(Control.framework == Framework.PDPL)
    )).all())

    # track counter per PDPL reference to generate unique IDs
    ref_counter: dict[str, int] = {}
    rows = []

    with open(pdpl_file, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pdpl_ref = row.get("PDPL Reference", "").strip()
            domain = row.get("Aligned Domain", "").strip()
            subdomain = row.get("Subdomain", "").strip()
            obligation = row.get("PDPL Control (Obligation)", "").strip()

            if not obligation:
                continue

            # build ID: PDPL-ART2-1, PDPL-ART5-1, etc.
            clean_ref = re.sub(r"[^A-Za-z0-9]", "", pdpl_ref.replace("Art.", "ART").replace(" ", ""))
            ref_counter[clean_ref] = ref_counter.get(clean_ref, 0) + 1
            full_id = f"PDPL-{clean_ref}-{ref_counter[clean_ref]}"

            if full_id in existing:
                continue

            c = Control(
                control_id=full_id,
                framework=Framework.PDPL,
                domain=domain or "Data Protection",
                title_en=subdomain or obligation[:120],
                title_ar=subdomain or obligation[:120],
                description_en=obligation,
                description_ar=obligation,
                priority="HIGH",
                status=ControlStatus.NOT_STARTED,
                maturity_level=1,
                evidence_types=[],
                related_controls=[],
            )
            session.add(c)
            rows.append(full_id)

    await session.flush()
    return len(rows)


# â”€â”€â”€ main â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
async def main():
    from core.database import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        async with session.begin():
            # count before
            total_before = (await session.execute(text("SELECT COUNT(*) FROM controls"))).scalar()
            print(f"Controls before: {total_before}")

            ecc_added = await load_ecc(session)
            print(f"  ECC added: {ecc_added}")

            ccc_added = await load_ccc(session)
            print(f"  CCC added: {ccc_added}")

            pdpl_added = await load_pdpl(session)
            print(f"  PDPL added: {pdpl_added}")

        total_after = (await session.execute(text("SELECT COUNT(*) FROM controls"))).scalar()
        ecc_total = (await session.execute(text("SELECT COUNT(*) FROM controls WHERE framework='ECC'"))).scalar()
        ccc_total = (await session.execute(text("SELECT COUNT(*) FROM controls WHERE framework='CCC'"))).scalar()
        pdpl_total = (await session.execute(text("SELECT COUNT(*) FROM controls WHERE framework='PDPL'"))).scalar()

        print(f"\nControls after: {total_after}")
        print(f"  ECC: {ecc_total}  CCC: {ccc_total}  PDPL: {pdpl_total}")
        print(f"  Net added: {total_after - total_before}")


if __name__ == "__main__":
    asyncio.run(main())
