"""
Initialize Demo Database with Official NCA Controls
Creates tables and loads ECC, CCC, and PDPL controls for demonstration
"""
import asyncio
import sys
import os
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from sqlalchemy import create_engine
from core.database import Base
from controls.models import Control, FrameworkType, ControlStatus
from auth.models import User, Role
import csv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_tables():
    """Create all database tables.

    For SQLite (local development): uses Base.metadata.create_all() for
    convenience — no Alembic required.

    For PostgreSQL (staging / production): schema creation is managed
    exclusively by Alembic migrations.  create_all() is intentionally
    skipped so that Alembic remains the single source of truth and
    incremental migrations are not bypassed.
    """
    database_url = os.getenv("DATABASE_URL", "sqlite:///./sico_grc.db")
    # Use sync engine (strip async driver prefix)
    sync_url = database_url.replace("+aiosqlite", "").replace("+asyncpg", "")
    engine = create_engine(sync_url, echo=False)

    is_sqlite = sync_url.startswith("sqlite")

    if is_sqlite:
        logger.info("Creating database tables via create_all (SQLite dev mode)...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
    else:
        # PostgreSQL: Alembic manages the schema — do NOT call create_all().
        # Run:  alembic upgrade head
        logger.info(
            "PostgreSQL detected — skipping create_all(). "
            "Run 'alembic upgrade head' to apply migrations."
        )

    return engine


def load_controls_from_csv(engine):
    """Load official NCA controls from CSV files"""
    from sqlalchemy.orm import Session
    
    controls_loaded = 0
    
    with Session(engine) as session:
        # Clear existing controls
        session.query(Control).delete()
        session.commit()
        
        # Load ECC controls
        ecc_csv = Path(__file__).parent.parent.parent / "data" / "controls" / "ecc_controls.csv"
        if ecc_csv.exists():
            logger.info(f"Loading ECC controls from {ecc_csv}...")
            with open(ecc_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Safely parse source  page
                    try:
                        source_page = int(row.get('Source_Page', 0)) if row.get('Source_Page') and row.get('Source_Page').isdigit() else None
                    except (ValueError, AttributeError):
                        source_page = None
                    
                    control = Control(
                        control_id=row['Control_ID'],
                        framework=FrameworkType.ECC,
                        domain=row.get('Domain', ''),
                        subdomain=row.get('Subdomain', ''),
                        title_en=row.get('Control_ID', ''),
                        title_ar=row.get('Control_ID', ''),
                        control_clause_en=row.get('Control_Clause', ''),
                        control_clause_ar=row.get('Control_Clause_AR', row.get('Control_Clause', '')),
                        description_en=row.get('Control_Clause', ''),
                        description_ar=row.get('Control_Clause_AR', row.get('Control_Clause', '')),
                        policy_guidance_en=row.get('Evidence_Examples', ''),
                        policy_guidance_ar='',
                        evidence_examples=row.get('Evidence_Examples', ''),
                        source_pdf=row.get('Source_PDF', 'ECC-1-2018-EN.pdf'),
                        source_page=source_page,
                        mapping_ccc=row.get('Mapping_CCC', ''),
                        mapping_pdpl=row.get('Mapping_PDPL', ''),
                        status=ControlStatus.NOT_STARTED,
                        priority='HIGH'
                    )
                    session.add(control)
                    controls_loaded += 1
            logger.info(f"✅ Loaded {controls_loaded} ECC controls")
        
        # Load CCC controls
        ccc_csv = Path(__file__).parent.parent.parent / "data" / "controls" / "ccc_controls.csv"
        if ccc_csv.exists():
            logger.info(f"Loading CCC controls from {ccc_csv}...")
            ccc_count = 0
            with open(ccc_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Safely parse source page
                    try:
                        source_page = int(row.get('Source_Page', 0)) if row.get('Source_Page') and row.get('Source_Page').isdigit() else None
                    except (ValueError, AttributeError):
                        source_page = None
                    
                    control = Control(
                        control_id=row['Control_ID'],
                        framework=FrameworkType.CCC,
                        domain=row.get('Domain', 'Cloud Controls'),
                        subdomain=row.get('Subdomain', ''),
                        title_en=row.get('Control_ID', ''),
                        title_ar=row.get('Control_ID', ''),
                        control_clause_en=row.get('Control_Clause', ''),
                        control_clause_ar=row.get('Control_Clause_AR', row.get('Control_Clause', '')),
                        description_en=row.get('Control_Clause', ''),
                        description_ar=row.get('Control_Clause_AR', row.get('Control_Clause', '')),
                        evidence_examples=row.get('Evidence_Examples', ''),
                        source_pdf=row.get('Source_PDF', 'CCC-2-2024-EN.pdf'),
                        source_page=source_page,
                        mapping_ecc=row.get('Mapping_ECC', ''),
                        status=ControlStatus.NOT_STARTED,
                        priority='HIGH'
                    )
                    session.add(control)
                    ccc_count += 1
            controls_loaded += ccc_count
            logger.info(f"✅ Loaded {ccc_count} CCC controls")
        
        # Load PDPL controls
        pdpl_csv = Path(__file__).parent.parent.parent / "data" / "controls" / "pdpl_controls.csv"
        if pdpl_csv.exists():
            logger.info(f"Loading PDPL controls from {pdpl_csv}...")
            pdpl_count = 0
            with open(pdpl_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    control = Control(
                        control_id=row['Control_ID'],
                        framework=FrameworkType.PDPL,
                        domain='Data Protection',
                        subdomain=row.get('Subdomain', ''),
                        title_en=row.get('Control_ID', ''),
                        title_ar=row.get('Control_ID', ''),
                        control_clause_en=row.get('Control_Clause', ''),
                        control_clause_ar=row.get('Control_Clause_AR', row.get('Control_Clause', '')),
                        description_en=row.get('Control_Clause', ''),
                        description_ar=row.get('Control_Clause_AR', row.get('Control_Clause', '')),
                        evidence_examples=row.get('Evidence_Examples', ''),
                        source_pdf='PDPL-2021-EN.pdf',
                        mapping_ecc=row.get('Related_ECC', ''),
                        mapping_ccc=row.get('Related_CCC', ''),
                        status=ControlStatus.NOT_STARTED,
                        priority='CRITICAL'
                    )
                    session.add(control)
                    pdpl_count += 1
            controls_loaded += pdpl_count
            logger.info(f"✅ Loaded {pdpl_count} PDPL controls")
        
        session.commit()
        logger.info(f"🎉 Successfully loaded {controls_loaded} total official NCA controls")


def main():
    """Initialize demo database"""
    logger.info("🚀 Initializing SICO GRC Demo Database...")
    logger.info("=" * 60)
    
    engine = create_tables()
    load_controls_from_csv(engine)
    
    logger.info("=" * 60)
    logger.info("✅ Demo database initialized successfully!")
    logger.info("📊 Database ready with official NCA controls (ECC, CCC, PDPL)")
    logger.info("🚀 You can now start the backend server")


if __name__ == "__main__":
    main()
