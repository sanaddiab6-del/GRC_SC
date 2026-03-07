"""
Dynamic configuration API router.
Provides Jira-style configurable UI layers (fields, workflows, dashboards, UI pages).
"""

from typing import List, Optional
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from auth.security import get_current_user
from auth.models import User
from dynamic_config.models import (
    CustomField,
    CustomFieldValue,
    WorkflowState,
    WorkflowTransition,
    DashboardWidget,
    DashboardLayout,
    UiPage,
    UiSection,
    UiFieldPlacement,
)
from dynamic_config.schemas import (
    CustomFieldCreate,
    CustomFieldUpdate,
    CustomFieldResponse,
    CustomFieldValueUpsert,
    CustomFieldWithValue,
    WorkflowStateCreate,
    WorkflowStateUpdate,
    WorkflowStateResponse,
    WorkflowTransitionCreate,
    WorkflowTransitionUpdate,
    WorkflowTransitionResponse,
    WorkflowConfigResponse,
    WorkflowApplyRequest,
    DashboardWidgetCreate,
    DashboardWidgetUpdate,
    DashboardWidgetResponse,
    DashboardLayoutCreate,
    DashboardLayoutResponse,
    UiPageConfigResponse,
)

router = APIRouter(prefix="/config", tags=["Configuration"])


@router.post("/custom-fields", response_model=CustomFieldResponse)
async def create_custom_field(
    payload: CustomFieldCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    field = CustomField(**payload.model_dump())
    db.add(field)
    await db.commit()
    await db.refresh(field)
    return field


@router.get("/custom-fields", response_model=List[CustomFieldResponse])
async def list_custom_fields(
    entity_type: str = Query(...),
    organization_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(CustomField).where(CustomField.entity_type == entity_type)
    if organization_id is not None:
        query = query.where(
            (CustomField.organization_id == organization_id)
            | (CustomField.organization_id.is_(None))
        )
    else:
        query = query.where(CustomField.organization_id.is_(None))
    result = await db.execute(query.order_by(CustomField.created_at.asc()))
    return result.scalars().all()


@router.patch("/custom-fields/{field_id}", response_model=CustomFieldResponse)
async def update_custom_field(
    field_id: UUID,
    payload: CustomFieldUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(CustomField).where(CustomField.id == field_id))
    field = result.scalar_one_or_none()
    if not field:
        raise HTTPException(status_code=404, detail="Custom field not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(field, key, value)

    await db.commit()
    await db.refresh(field)
    return field


@router.delete("/custom-fields/{field_id}")
async def delete_custom_field(
    field_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(CustomField).where(CustomField.id == field_id))
    field = result.scalar_one_or_none()
    if not field:
        raise HTTPException(status_code=404, detail="Custom field not found")
    await db.delete(field)
    await db.commit()
    return {"status": "deleted"}


@router.get("/custom-fields/values", response_model=List[CustomFieldWithValue])
async def get_custom_field_values(
    entity_type: str = Query(...),
    entity_id: str = Query(...),
    organization_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    fields_query = select(CustomField).where(CustomField.entity_type == entity_type)
    if organization_id is not None:
        fields_query = fields_query.where(
            (CustomField.organization_id == organization_id)
            | (CustomField.organization_id.is_(None))
        )
    else:
        fields_query = fields_query.where(CustomField.organization_id.is_(None))

    fields_result = await db.execute(fields_query)
    fields = fields_result.scalars().all()

    values_result = await db.execute(
        select(CustomFieldValue).where(CustomFieldValue.entity_id == entity_id)
    )
    values = {v.field_id: v.value for v in values_result.scalars().all()}

    return [
        CustomFieldWithValue(
            **CustomFieldResponse.model_validate(field).model_dump(),
            value=values.get(field.id),
        )
        for field in fields
    ]


@router.put("/custom-fields/values")
async def upsert_custom_field_values(
    payload: CustomFieldValueUpsert,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    for item in payload.values:
        result = await db.execute(
            select(CustomFieldValue)
            .where(CustomFieldValue.entity_id == payload.entity_id)
            .where(CustomFieldValue.field_id == item.field_id)
        )
        existing = result.scalar_one_or_none()
        if existing:
            existing.value = item.value
        else:
            db.add(
                CustomFieldValue(
                    entity_id=payload.entity_id,
                    field_id=item.field_id,
                    value=item.value,
                )
            )

    await db.commit()
    return {"status": "ok"}


@router.post("/workflows/states", response_model=WorkflowStateResponse)
async def create_workflow_state(
    payload: WorkflowStateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    state = WorkflowState(**payload.model_dump())
    db.add(state)
    await db.commit()
    await db.refresh(state)
    return state


@router.patch("/workflows/states/{state_id}", response_model=WorkflowStateResponse)
async def update_workflow_state(
    state_id: UUID,
    payload: WorkflowStateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(WorkflowState).where(WorkflowState.id == state_id))
    state = result.scalar_one_or_none()
    if not state:
        raise HTTPException(status_code=404, detail="Workflow state not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(state, key, value)

    await db.commit()
    await db.refresh(state)
    return state


@router.post("/workflows/transitions", response_model=WorkflowTransitionResponse)
async def create_workflow_transition(
    payload: WorkflowTransitionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transition = WorkflowTransition(**payload.model_dump())
    db.add(transition)
    await db.commit()
    await db.refresh(transition)
    return transition


@router.patch("/workflows/transitions/{transition_id}", response_model=WorkflowTransitionResponse)
async def update_workflow_transition(
    transition_id: UUID,
    payload: WorkflowTransitionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(WorkflowTransition).where(WorkflowTransition.id == transition_id))
    transition = result.scalar_one_or_none()
    if not transition:
        raise HTTPException(status_code=404, detail="Workflow transition not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(transition, key, value)

    await db.commit()
    await db.refresh(transition)
    return transition


@router.get("/workflows", response_model=WorkflowConfigResponse)
async def get_workflow_config(
    entity_type: str = Query(...),
    organization_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    states_query = select(WorkflowState).where(WorkflowState.entity_type == entity_type)
    if organization_id is not None:
        states_query = states_query.where(
            (WorkflowState.organization_id == organization_id)
            | (WorkflowState.organization_id.is_(None))
        )
    else:
        states_query = states_query.where(WorkflowState.organization_id.is_(None))

    states_result = await db.execute(states_query.order_by(WorkflowState.order_index.asc()))
    states = states_result.scalars().all()

    transitions_result = await db.execute(
        select(WorkflowTransition)
        .join(WorkflowState, WorkflowState.id == WorkflowTransition.from_state)
        .where(WorkflowState.entity_type == entity_type)
    )
    transitions = transitions_result.scalars().all()

    return WorkflowConfigResponse(
        states=[WorkflowStateResponse.model_validate(state) for state in states],
        transitions=[WorkflowTransitionResponse.model_validate(transition) for transition in transitions],
    )


def _entity_mapping():
    from controls.models import Control
    from evidence.models import Evidence
    from risk.models import Risk
    from assessment.models import AssessmentInstance
    from audit.models import AuditFinding

    return {
        "control": (Control, "control_id", "status", str),
        "evidence": (Evidence, "evidence_id", "status", str),
        "risk": (Risk, "risk_id", "status", UUID),
        "assessment": (AssessmentInstance, "assessment_id", "status", str),
        "finding": (AuditFinding, "finding_id", "status", int),
    }


def _normalize_state(value: object) -> str:
    if value is None:
        return ""
    if hasattr(value, "value"):
        return str(getattr(value, "value"))
    return str(value)


@router.post("/workflows/apply")
async def apply_workflow_transition(
    payload: WorkflowApplyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    mapping = _entity_mapping().get(payload.entity_type)
    if not mapping:
        raise HTTPException(status_code=400, detail="Unsupported entity type")

    model, id_field, status_field, cast_fn = mapping
    try:
        entity_id = cast_fn(payload.entity_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid entity_id format")

    stmt = select(model).where(getattr(model, id_field) == entity_id)
    result = await db.execute(stmt)
    entity = result.scalar_one_or_none()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    current_state = _normalize_state(getattr(entity, status_field))

    state_result = await db.execute(
        select(WorkflowState)
        .where(WorkflowState.entity_type == payload.entity_type)
        .where(WorkflowState.state_key == payload.to_state_key)
    )
    target_state = state_result.scalar_one_or_none()
    if not target_state:
        raise HTTPException(status_code=404, detail="Target workflow state not found")

    transition_result = await db.execute(
        select(WorkflowTransition)
        .where(WorkflowTransition.to_state == target_state.id)
        .join(WorkflowState, WorkflowState.id == WorkflowTransition.from_state)
        .where(WorkflowState.state_key == current_state)
    )
    transition = transition_result.scalar_one_or_none()
    if not transition:
        raise HTTPException(status_code=400, detail="Transition not allowed")

    allowed_roles = transition.allowed_roles or []
    if allowed_roles:
        role_names = [role.role_name for role in getattr(current_user, "roles", [])]
        if not any(role in role_names for role in allowed_roles):
            raise HTTPException(status_code=403, detail="Role not allowed for transition")

    setattr(entity, status_field, payload.to_state_key)
    if hasattr(entity, "lifecycle_updated_at"):
        setattr(entity, "lifecycle_updated_at", datetime.utcnow())

    await db.commit()
    return {"status": "updated", "state": payload.to_state_key}


@router.post("/dashboard/widgets", response_model=DashboardWidgetResponse)
async def create_dashboard_widget(
    payload: DashboardWidgetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    widget = DashboardWidget(**payload.model_dump())
    db.add(widget)
    await db.commit()
    await db.refresh(widget)
    return widget


@router.get("/dashboard/widgets", response_model=List[DashboardWidgetResponse])
async def list_dashboard_widgets(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(DashboardWidget).order_by(DashboardWidget.widget_key.asc()))
    return result.scalars().all()


@router.patch("/dashboard/widgets/{widget_id}", response_model=DashboardWidgetResponse)
async def update_dashboard_widget(
    widget_id: UUID,
    payload: DashboardWidgetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(DashboardWidget).where(DashboardWidget.id == widget_id))
    widget = result.scalar_one_or_none()
    if not widget:
        raise HTTPException(status_code=404, detail="Dashboard widget not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(widget, key, value)

    await db.commit()
    await db.refresh(widget)
    return widget


@router.post("/dashboard/layouts", response_model=DashboardLayoutResponse)
async def create_dashboard_layout(
    payload: DashboardLayoutCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    layout = DashboardLayout(**payload.model_dump())
    db.add(layout)
    await db.commit()
    await db.refresh(layout)
    return DashboardLayoutResponse.model_validate(layout)


@router.get("/dashboard/layouts", response_model=List[DashboardLayoutResponse])
async def get_dashboard_layouts(
    organization_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(DashboardLayout).order_by(DashboardLayout.id.asc())
    if organization_id is not None:
        query = query.where(
            (DashboardLayout.organization_id == organization_id)
            | (DashboardLayout.organization_id.is_(None))
        )
    else:
        query = query.where(DashboardLayout.organization_id.is_(None))

    result = await db.execute(query)
    layouts = result.scalars().all()

    responses = []
    for layout in layouts:
        await db.refresh(layout, attribute_names=["widget"])
        responses.append(DashboardLayoutResponse.model_validate(layout))

    return responses


@router.get("/ui/pages/{page_key}", response_model=UiPageConfigResponse)
async def get_ui_page_config(
    page_key: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    page_result = await db.execute(select(UiPage).where(UiPage.page_key == page_key))
    page = page_result.scalar_one_or_none()
    if not page:
        raise HTTPException(status_code=404, detail="UI page not configured")

    sections_result = await db.execute(
        select(UiSection).where(UiSection.page_id == page.id).order_by(UiSection.order_index.asc())
    )
    sections = sections_result.scalars().all()

    placements_result = await db.execute(
        select(UiFieldPlacement)
        .join(UiSection, UiSection.id == UiFieldPlacement.section_id)
        .where(UiSection.page_id == page.id)
        .order_by(UiFieldPlacement.order_index.asc())
    )
    placements = placements_result.scalars().all()

    return UiPageConfigResponse(
        page=page,
        sections=sections,
        placements=placements,
    )
