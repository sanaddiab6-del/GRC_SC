"""
Dynamic configuration models for Jira-style UI customization.
"""

from datetime import datetime
import enum
import uuid

from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Enum as SQLEnum, Index, UniqueConstraint
from sqlalchemy import Uuid
from sqlalchemy.orm import relationship
from sqlalchemy.dialects import postgresql

from core.database import Base


class CustomFieldType(str, enum.Enum):
    """Supported custom field types."""
    TEXT = "text"
    NUMBER = "number"
    SELECT = "select"
    USER = "user"
    DATE = "date"
    BOOLEAN = "boolean"


class CustomField(Base):
    """Custom field definitions for configurable entities."""
    __tablename__ = "custom_fields"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String(50), nullable=False, index=True)
    field_key = Column(String(100), nullable=False)
    field_label = Column(String(255), nullable=False)
    field_type = Column(SQLEnum(CustomFieldType, native_enum=False), nullable=False)
    required = Column(Boolean, default=False)
    options_json = Column(postgresql.JSONB)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    values = relationship("CustomFieldValue", back_populates="field", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("entity_type", "field_key", "organization_id", name="uq_custom_field_key"),
        Index("ix_custom_fields_entity_org", "entity_type", "organization_id"),
    )


class CustomFieldValue(Base):
    """Custom field values for specific entities."""
    __tablename__ = "custom_field_values"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id = Column(String(100), nullable=False, index=True)
    field_id = Column(Uuid(as_uuid=True), ForeignKey("custom_fields.id", ondelete="CASCADE"), nullable=False)
    value = Column(postgresql.JSONB)

    field = relationship("CustomField", back_populates="values")

    __table_args__ = (
        UniqueConstraint("entity_id", "field_id", name="uq_custom_field_value"),
        Index("ix_custom_field_values_entity", "entity_id"),
    )


class WorkflowState(Base):
    """Workflow states per entity type."""
    __tablename__ = "workflow_states"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String(50), nullable=False, index=True)
    state_key = Column(String(100), nullable=False)
    label = Column(String(255), nullable=False)
    order_index = Column(Integer, default=0)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True, index=True)

    outgoing = relationship(
        "WorkflowTransition",
        foreign_keys="WorkflowTransition.from_state",
        back_populates="from_state_ref",
        cascade="all, delete-orphan",
    )
    incoming = relationship(
        "WorkflowTransition",
        foreign_keys="WorkflowTransition.to_state",
        back_populates="to_state_ref",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint("entity_type", "state_key", "organization_id", name="uq_workflow_state_key"),
        Index("ix_workflow_states_entity_org", "entity_type", "organization_id"),
    )


class WorkflowTransition(Base):
    """Workflow transitions between states."""
    __tablename__ = "workflow_transitions"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    from_state = Column(Uuid(as_uuid=True), ForeignKey("workflow_states.id", ondelete="CASCADE"), nullable=False)
    to_state = Column(Uuid(as_uuid=True), ForeignKey("workflow_states.id", ondelete="CASCADE"), nullable=False)
    action_label = Column(String(255), nullable=False)
    allowed_roles = Column(postgresql.JSONB)

    from_state_ref = relationship("WorkflowState", foreign_keys=[from_state], back_populates="outgoing")
    to_state_ref = relationship("WorkflowState", foreign_keys=[to_state], back_populates="incoming")


class DashboardWidget(Base):
    """Configurable dashboard widgets."""
    __tablename__ = "dashboard_widgets"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    widget_key = Column(String(100), nullable=False, unique=True)
    title = Column(String(255), nullable=False)
    component_type = Column(String(100), nullable=False)
    data_source = Column(String(100), nullable=True)
    config_json = Column(postgresql.JSONB)


class DashboardLayout(Base):
    """Dashboard layout per organization."""
    __tablename__ = "dashboard_layouts"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True, index=True)
    widget_id = Column(Uuid(as_uuid=True), ForeignKey("dashboard_widgets.id", ondelete="CASCADE"), nullable=False)
    position = Column(postgresql.JSONB)
    size = Column(postgresql.JSONB)

    widget = relationship("DashboardWidget")

    __table_args__ = (
        Index("ix_dashboard_layouts_org", "organization_id"),
    )


class UiPage(Base):
    """Configurable UI pages."""
    __tablename__ = "ui_pages"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    page_key = Column(String(100), nullable=False, unique=True)
    title = Column(String(255), nullable=False)

    sections = relationship("UiSection", back_populates="page", cascade="all, delete-orphan")


class UiSection(Base):
    """Page sections for UI configuration."""
    __tablename__ = "ui_sections"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    page_id = Column(Uuid(as_uuid=True), ForeignKey("ui_pages.id", ondelete="CASCADE"), nullable=False)
    section_key = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    order_index = Column(Integer, default=0)

    page = relationship("UiPage", back_populates="sections")
    placements = relationship("UiFieldPlacement", back_populates="section", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("page_id", "section_key", name="uq_ui_section_key"),
        Index("ix_ui_sections_page", "page_id"),
    )


class UiFieldPlacement(Base):
    """Field placement within UI sections."""
    __tablename__ = "ui_field_placements"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    section_id = Column(Uuid(as_uuid=True), ForeignKey("ui_sections.id", ondelete="CASCADE"), nullable=False)
    field_key = Column(String(100), nullable=False)
    order_index = Column(Integer, default=0)

    section = relationship("UiSection", back_populates="placements")

    __table_args__ = (
        Index("ix_ui_field_placements_section", "section_id"),
    )
