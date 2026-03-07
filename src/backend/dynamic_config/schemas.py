"""Schemas for dynamic configuration APIs."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CustomFieldBase(BaseModel):
    entity_type: str
    field_key: str
    field_label: str
    field_type: str
    required: bool = False
    options_json: Optional[Dict[str, Any]] = None
    organization_id: Optional[int] = None


class CustomFieldCreate(CustomFieldBase):
    pass


class CustomFieldUpdate(BaseModel):
    field_label: Optional[str] = None
    field_type: Optional[str] = None
    required: Optional[bool] = None
    options_json: Optional[Dict[str, Any]] = None


class CustomFieldResponse(CustomFieldBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CustomFieldValueItem(BaseModel):
    field_id: UUID
    value: Optional[Any] = None


class CustomFieldValueUpsert(BaseModel):
    entity_type: str
    entity_id: str
    values: List[CustomFieldValueItem]


class CustomFieldWithValue(CustomFieldResponse):
    value: Optional[Any] = None


class WorkflowStateBase(BaseModel):
    entity_type: str
    state_key: str
    label: str
    order_index: int = 0
    organization_id: Optional[int] = None


class WorkflowStateCreate(WorkflowStateBase):
    pass


class WorkflowStateUpdate(BaseModel):
    state_key: Optional[str] = None
    label: Optional[str] = None
    order_index: Optional[int] = None
    organization_id: Optional[int] = None


class WorkflowStateResponse(WorkflowStateBase):
    id: Union[UUID, int]  # Support both UUID and INTEGER for legacy schemas

    model_config = ConfigDict(from_attributes=True)


class WorkflowTransitionBase(BaseModel):
    from_state: Union[UUID, int]  # Support both UUID and INTEGER for legacy schemas
    to_state: Union[UUID, int]  # Support both UUID and INTEGER for legacy schemas
    action_label: str
    allowed_roles: Optional[List[str]] = None


class WorkflowTransitionCreate(WorkflowTransitionBase):
    pass


class WorkflowTransitionUpdate(BaseModel):
    from_state: Optional[Union[UUID, int]] = None
    to_state: Optional[Union[UUID, int]] = None
    action_label: Optional[str] = None
    allowed_roles: Optional[List[str]] = None


class WorkflowTransitionResponse(WorkflowTransitionBase):
    id: Union[UUID, int]  # Support both UUID and INTEGER for legacy schemas

    model_config = ConfigDict(from_attributes=True)


class WorkflowConfigResponse(BaseModel):
    states: List[WorkflowStateResponse]
    transitions: List[WorkflowTransitionResponse]


class WorkflowApplyRequest(BaseModel):
    entity_type: str
    entity_id: str
    to_state_key: str


class DashboardWidgetBase(BaseModel):
    widget_key: str
    title: str
    component_type: str
    data_source: Optional[str] = None
    config_json: Optional[Dict[str, Any]] = None


class DashboardWidgetCreate(DashboardWidgetBase):
    pass


class DashboardWidgetUpdate(BaseModel):
    widget_key: Optional[str] = None
    title: Optional[str] = None
    component_type: Optional[str] = None
    data_source: Optional[str] = None
    config_json: Optional[Dict[str, Any]] = None


class DashboardWidgetResponse(DashboardWidgetBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)


class DashboardLayoutBase(BaseModel):
    organization_id: Optional[int] = None
    widget_id: UUID
    position: Optional[Dict[str, Any]] = None
    size: Optional[Dict[str, Any]] = None


class DashboardLayoutCreate(DashboardLayoutBase):
    pass


class DashboardLayoutResponse(DashboardLayoutBase):
    id: UUID
    widget: Optional[DashboardWidgetResponse] = None

    model_config = ConfigDict(from_attributes=True)


class UiPageResponse(BaseModel):
    id: UUID
    page_key: str
    title: str

    model_config = ConfigDict(from_attributes=True)


class UiSectionResponse(BaseModel):
    id: UUID
    section_key: str
    title: str
    order_index: int

    model_config = ConfigDict(from_attributes=True)


class UiFieldPlacementResponse(BaseModel):
    id: UUID
    field_key: str
    order_index: int

    model_config = ConfigDict(from_attributes=True)


class UiPageConfigResponse(BaseModel):
    page: UiPageResponse
    sections: List[UiSectionResponse]
    placements: List[UiFieldPlacementResponse]
