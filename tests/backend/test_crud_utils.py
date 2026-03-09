"""
Tests for core/crud_utils.py — get_by_id, check_exists, update_model, delete_by_id,
create_bilingual_error.
All tests use a mock AsyncSession so no real DB is needed.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, PropertyMock
from fastapi import HTTPException


# ─── get_by_id ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_by_id_found():
    from core.crud_utils import get_by_id

    mock_item = MagicMock()
    mock_item.control_id = "ECC-1"

    session = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = mock_item
    session.execute = AsyncMock(return_value=result)

    # We need a mock model with a real attribute-like field
    model = MagicMock()
    model.control_id = MagicMock()  # column descriptor

    item = await get_by_id(
        db=session,
        model=model,
        id_field_name="control_id",
        id_value="ECC-1",
        error_message_en="Not found",
        error_message_ar="غير موجود",
    )
    assert item is mock_item


@pytest.mark.asyncio
async def test_get_by_id_not_found():
    from core.crud_utils import get_by_id

    session = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    session.execute = AsyncMock(return_value=result)

    model = MagicMock()
    model.control_id = MagicMock()

    with pytest.raises(HTTPException) as exc_info:
        await get_by_id(
            db=session,
            model=model,
            id_field_name="control_id",
            id_value="NOPE",
            error_message_en="Not found",
            error_message_ar="غير موجود",
        )
    assert exc_info.value.status_code == 404


# ─── check_exists ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_check_exists_no_conflict():
    from core.crud_utils import check_exists

    session = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    session.execute = AsyncMock(return_value=result)

    model = MagicMock()
    model.control_id = MagicMock()

    # Should not raise
    await check_exists(
        db=session,
        model=model,
        id_field_name="control_id",
        id_value="NEW-ID",
        error_message_en="Already exists",
        error_message_ar="موجود بالفعل",
    )


@pytest.mark.asyncio
async def test_check_exists_conflict():
    from core.crud_utils import check_exists

    existing = MagicMock()
    session = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = existing
    session.execute = AsyncMock(return_value=result)

    model = MagicMock()
    model.control_id = MagicMock()

    with pytest.raises(HTTPException) as exc_info:
        await check_exists(
            db=session,
            model=model,
            id_field_name="control_id",
            id_value="DUP",
            error_message_en="Already exists",
            error_message_ar="موجود بالفعل",
        )
    assert exc_info.value.status_code == 400


# ─── update_model ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_model():
    from core.crud_utils import update_model
    from pydantic import BaseModel
    from typing import Optional

    class FakeUpdate(BaseModel):
        title_en: Optional[str] = None
        status: Optional[str] = None

    item = MagicMock()
    item.title_en = "Old"
    item.status = "not_started"

    session = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()

    update_data = FakeUpdate(title_en="New Title")
    result = await update_model(item=item, update_data=update_data, db=session)

    # setattr should have been called
    assert result is item
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once()


# ─── delete_by_id ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_delete_by_id_found():
    from core.crud_utils import delete_by_id

    mock_item = MagicMock()
    session = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = mock_item
    session.execute = AsyncMock(return_value=result)
    session.delete = AsyncMock()
    session.commit = AsyncMock()

    model = MagicMock()
    model.control_id = MagicMock()

    await delete_by_id(
        db=session,
        model=model,
        id_field_name="control_id",
        id_value="ECC-1",
        error_message_en="Not found",
        error_message_ar="غير موجود",
    )
    session.delete.assert_awaited_once_with(mock_item)
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_by_id_not_found():
    from core.crud_utils import delete_by_id

    session = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    session.execute = AsyncMock(return_value=result)

    model = MagicMock()
    model.control_id = MagicMock()

    with pytest.raises(HTTPException) as exc_info:
        await delete_by_id(
            db=session,
            model=model,
            id_field_name="control_id",
            id_value="NOPE",
            error_message_en="Not found",
            error_message_ar="غير موجود",
        )
    assert exc_info.value.status_code == 404


# ─── create_bilingual_error ───────────────────────────────────────────────────

def test_create_bilingual_error_not_found():
    from core.crud_utils import create_bilingual_error

    err = create_bilingual_error("Control", "الضابط", "ECC-1", "not_found")
    assert "not found" in err["message_en"]
    assert "ECC-1" in err["message_en"]


def test_create_bilingual_error_already_exists():
    from core.crud_utils import create_bilingual_error

    err = create_bilingual_error("Evidence", "الدليل", "EVD-1", "already_exists")
    assert "already exists" in err["message_en"]


def test_create_bilingual_error_unknown():
    from core.crud_utils import create_bilingual_error

    err = create_bilingual_error("X", "ي", "1", "other")
    assert "Error" in err["message_en"]
