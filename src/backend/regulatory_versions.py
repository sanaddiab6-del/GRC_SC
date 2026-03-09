"""
Regulatory Version Register
Tracks versions of compliance frameworks (ECC, CCC, PDPL)
"""

from datetime import datetime, date
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, Date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from core.database import Base, get_db

router = APIRouter()


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------

class FrameworkVersion(Base):
    """Tracks the published versions of each regulatory framework."""
    __tablename__ = "framework_versions"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    framework = Column(String(20), nullable=False, index=True)  # ECC, CCC, PDPL
    version_number = Column(String(50), nullable=False)  # e.g. "2.0", "1.1"
    effective_date = Column(Date, nullable=False)
    is_current = Column(Boolean, default=False, index=True)

    # Bilingual description
    description_en = Column(Text)
    description_ar = Column(Text)

    # Key changes in this version
    changes_summary_en = Column(Text)
    changes_summary_ar = Column(Text)

    # Source reference
    source_url = Column(String(500))

    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<FrameworkVersion {self.framework} v{self.version_number}>"


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class FrameworkVersionCreate(BaseModel):
    framework: str = Field(json_schema_extra={"example": "ECC"})
    version_number: str = Field(json_schema_extra={"example": "2.0"})
    effective_date: date
    is_current: bool = False
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    changes_summary_en: Optional[str] = None
    changes_summary_ar: Optional[str] = None
    source_url: Optional[str] = None


class FrameworkVersionResponse(FrameworkVersionCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/framework-versions", response_model=List[FrameworkVersionResponse])
async def list_framework_versions(
    framework: Optional[str] = None,
    current_only: bool = False,
    db: AsyncSession = Depends(get_db),
):
    """
    List all registered framework versions.
    Optionally filter by framework name or show only current versions.
    """
    query = select(FrameworkVersion).order_by(
        FrameworkVersion.framework,
        FrameworkVersion.effective_date.desc(),
    )
    if framework:
        query = query.where(FrameworkVersion.framework == framework.upper())
    if current_only:
        query = query.where(FrameworkVersion.is_current == True)  # noqa: E712

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/framework-versions/{framework}/current", response_model=FrameworkVersionResponse)
async def get_current_version(
    framework: str,
    db: AsyncSession = Depends(get_db),
):
    """Get the currently active version for a given framework."""
    query = (
        select(FrameworkVersion)
        .where(
            FrameworkVersion.framework == framework.upper(),
            FrameworkVersion.is_current == True,  # noqa: E712
        )
    )
    result = await db.execute(query)
    version = result.scalar_one_or_none()
    if not version:
        raise HTTPException(
            status_code=404,
            detail={
                "message_en": f"No current version registered for framework '{framework}'",
                "message_ar": f"لا توجد نسخة حالية مسجلة للإطار '{framework}'",
            },
        )
    return version


@router.post("/framework-versions", response_model=FrameworkVersionResponse, status_code=201)
async def register_framework_version(
    version_data: FrameworkVersionCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new framework version.
    If is_current=True, any existing current version for the same framework
    is automatically demoted.
    """
    framework = version_data.framework.upper()

    # If marking this as current, unset existing current version
    if version_data.is_current:
        existing_query = select(FrameworkVersion).where(
            FrameworkVersion.framework == framework,
            FrameworkVersion.is_current == True,  # noqa: E712
        )
        existing_result = await db.execute(existing_query)
        existing_current = existing_result.scalars().all()
        for ev in existing_current:
            ev.is_current = False

    new_version = FrameworkVersion(
        framework=framework,
        version_number=version_data.version_number,
        effective_date=version_data.effective_date,
        is_current=version_data.is_current,
        description_en=version_data.description_en,
        description_ar=version_data.description_ar,
        changes_summary_en=version_data.changes_summary_en,
        changes_summary_ar=version_data.changes_summary_ar,
        source_url=version_data.source_url,
    )
    db.add(new_version)
    await db.commit()
    await db.refresh(new_version)
    return new_version
