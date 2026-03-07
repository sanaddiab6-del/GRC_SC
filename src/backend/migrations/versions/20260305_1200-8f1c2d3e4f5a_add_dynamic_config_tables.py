"""Add dynamic configuration tables for Jira-style UI

Revision ID: 8f1c2d3e4f5a
Revises: b7c8d9e0f1a2
Create Date: 2026-03-05 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers
revision = "8f1c2d3e4f5a"
down_revision = "b7c8d9e0f1a2"
branch_labels = None
depends_on = None


class GUID(sa.TypeDecorator):
    """Platform-independent GUID type."""
    impl = sa.CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(postgresql.UUID())
        return dialect.type_descriptor(sa.CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == "postgresql":
            return str(value)
        if isinstance(value, uuid.UUID):
            return "%.32x" % value.int
        return "%.32x" % uuid.UUID(value).int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(value)
        return value


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    def _table_exists(name: str) -> bool:
        return name in inspector.get_table_names()

    def _index_exists(table: str, index_name: str) -> bool:
        indexes = inspector.get_indexes(table)
        return any(idx.get("name") == index_name for idx in indexes)

    def _unique_exists(table: str, constraint_name: str) -> bool:
        uniques = inspector.get_unique_constraints(table)
        return any(uc.get("name") == constraint_name for uc in uniques)

    def _column_exists(table: str, column_name: str) -> bool:
        columns = inspector.get_columns(table)
        return any(col.get("name") == column_name for col in columns)

    def _fk_exists(table: str, fk_name: str) -> bool:
        fks = inspector.get_foreign_keys(table)
        return any(fk.get("name") == fk_name for fk in fks)

    def _is_table_empty(name: str) -> bool:
        result = bind.execute(sa.text(f"SELECT 1 FROM {name} LIMIT 1"))
        return result.first() is None

    def _ensure_jsonb(table: str, column: str) -> None:
        columns = inspector.get_columns(table)
        for col in columns:
            if col.get("name") == column:
                col_type = col.get("type")
                if not isinstance(col_type, postgresql.JSONB):
                    op.execute(
                        sa.text(
                            f"ALTER TABLE {table} ALTER COLUMN {column} TYPE JSONB USING {column}::jsonb"
                        )
                    )
                break

    # Custom fields
    if not _table_exists("custom_fields"):
        op.create_table(
            "custom_fields",
            sa.Column("id", GUID(), primary_key=True, default=uuid.uuid4),
            sa.Column("entity_type", sa.String(50), nullable=False, index=True),
            sa.Column("field_key", sa.String(100), nullable=False),
            sa.Column("field_label", sa.String(255), nullable=False),
            sa.Column("field_type", sa.String(50), nullable=False),
            sa.Column("required", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column("options_json", postgresql.JSONB(), nullable=True),
            sa.Column("organization_id", sa.Integer(), sa.ForeignKey("organizations.id"), nullable=True, index=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.UniqueConstraint("entity_type", "field_key", "organization_id", name="uq_custom_field_key"),
        )
    else:
        _ensure_jsonb("custom_fields", "options_json")
        if not _unique_exists("custom_fields", "uq_custom_field_key"):
            op.create_unique_constraint("uq_custom_field_key", "custom_fields", ["entity_type", "field_key", "organization_id"])
    if not _index_exists("custom_fields", "ix_custom_fields_entity_org"):
        op.create_index("ix_custom_fields_entity_org", "custom_fields", ["entity_type", "organization_id"], unique=False)

    if not _table_exists("custom_field_values"):
        op.create_table(
            "custom_field_values",
            sa.Column("id", GUID(), primary_key=True, default=uuid.uuid4),
            sa.Column("entity_id", sa.String(100), nullable=False, index=True),
            sa.Column("field_id", GUID(), sa.ForeignKey("custom_fields.id", ondelete="CASCADE"), nullable=False),
            sa.Column("value", postgresql.JSONB(), nullable=True),
            sa.UniqueConstraint("entity_id", "field_id", name="uq_custom_field_value"),
        )
    else:
        _ensure_jsonb("custom_field_values", "value")
        if not _unique_exists("custom_field_values", "uq_custom_field_value"):
            op.create_unique_constraint("uq_custom_field_value", "custom_field_values", ["entity_id", "field_id"])
    if not _index_exists("custom_field_values", "ix_custom_field_values_entity"):
        op.create_index("ix_custom_field_values_entity", "custom_field_values", ["entity_id"], unique=False)

    # Workflow definitions
    if not _table_exists("workflow_definitions"):
        op.create_table(
            "workflow_definitions",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("entity_type", sa.String(50), nullable=False, unique=True, index=True),
            sa.Column("name", sa.String(255), nullable=False),
            sa.Column("organization_id", sa.Integer(), sa.ForeignKey("organizations.id"), nullable=True, index=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        )
    else:
        if not _column_exists("workflow_definitions", "organization_id"):
            op.add_column("workflow_definitions", sa.Column("organization_id", sa.Integer(), nullable=True))
        if not _column_exists("workflow_definitions", "created_at"):
            op.add_column("workflow_definitions", sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")))
        
        if _column_exists("workflow_definitions", "organization_id") and not _fk_exists("workflow_definitions", "fk_workflow_definitions_org"):
            op.create_foreign_key(
                "fk_workflow_definitions_org",
                "workflow_definitions",
                "organizations",
                ["organization_id"],
                ["id"],
            )

    # Workflow configuration
    if not _table_exists("workflow_states"):
        op.create_table(
            "workflow_states",
            sa.Column("id", GUID(), primary_key=True, default=uuid.uuid4),
            sa.Column("definition_id", sa.Integer(), sa.ForeignKey("workflow_definitions.id", ondelete="SET NULL"), nullable=True, index=True),
            sa.Column("entity_type", sa.String(50), nullable=False, index=True),
            sa.Column("state_key", sa.String(100), nullable=False),
            sa.Column("label", sa.String(255), nullable=False),
            sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("organization_id", sa.Integer(), sa.ForeignKey("organizations.id"), nullable=True, index=True),
            sa.UniqueConstraint("entity_type", "state_key", "organization_id", name="uq_workflow_state_key"),
        )
    else:
        if not _column_exists("workflow_states", "definition_id"):
            op.add_column("workflow_states", sa.Column("definition_id", sa.Integer(), nullable=True))
        if not _column_exists("workflow_states", "entity_type"):
            op.add_column("workflow_states", sa.Column("entity_type", sa.String(50), nullable=True))
        if not _column_exists("workflow_states", "state_key"):
            op.add_column("workflow_states", sa.Column("state_key", sa.String(100), nullable=True))
        if not _column_exists("workflow_states", "organization_id"):
            op.add_column("workflow_states", sa.Column("organization_id", sa.Integer(), nullable=True))

        if _column_exists("workflow_states", "definition_id") and not _fk_exists("workflow_states", "fk_workflow_states_definition"):
            op.create_foreign_key(
                "fk_workflow_states_definition",
                "workflow_states",
                "workflow_definitions",
                ["definition_id"],
                ["id"],
                ondelete="SET NULL",
            )

        if _column_exists("workflow_states", "organization_id") and not _fk_exists("workflow_states", "fk_workflow_states_org"):
            op.create_foreign_key(
                "fk_workflow_states_org",
                "workflow_states",
                "organizations",
                ["organization_id"],
                ["id"],
            )

        if _column_exists("workflow_states", "state_key") and _column_exists("workflow_states", "key"):
            op.execute(
                sa.text(
                    "UPDATE workflow_states SET state_key = key WHERE (state_key IS NULL OR state_key = '')"
                )
            )

        if _column_exists("workflow_states", "entity_type"):
            op.execute(
                sa.text(
                    "UPDATE workflow_states SET entity_type = 'legacy' WHERE entity_type IS NULL OR entity_type = ''"
                )
            )

        if (
            _column_exists("workflow_states", "entity_type")
            and _column_exists("workflow_states", "state_key")
            and _column_exists("workflow_states", "organization_id")
            and not _unique_exists("workflow_states", "uq_workflow_state_key")
        ):
            op.create_unique_constraint(
                "uq_workflow_state_key",
                "workflow_states",
                ["entity_type", "state_key", "organization_id"],
            )

    if (
        _column_exists("workflow_states", "entity_type")
        and _column_exists("workflow_states", "organization_id")
        and not _index_exists("workflow_states", "ix_workflow_states_entity_org")
    ):
        op.create_index("ix_workflow_states_entity_org", "workflow_states", ["entity_type", "organization_id"], unique=False)

    if not _table_exists("workflow_transitions"):
        # Detect if workflow_states uses UUID or INTEGER for id
        ws_id_is_uuid = False
        if _table_exists("workflow_states"):
            for col in inspector.get_columns("workflow_states"):
                if col.get("name") == "id":
                    ws_id_is_uuid = isinstance(col.get("type"), postgresql.UUID)
                    break
        
        # Use matching FK type
        state_id_type = GUID() if ws_id_is_uuid else sa.Integer()
        
        op.create_table(
            "workflow_transitions",
            sa.Column("id", GUID(), primary_key=True, default=uuid.uuid4),
            sa.Column("from_state", state_id_type, sa.ForeignKey("workflow_states.id", ondelete="CASCADE"), nullable=False),
            sa.Column("to_state", state_id_type, sa.ForeignKey("workflow_states.id", ondelete="CASCADE"), nullable=False),
            sa.Column("action_label", sa.String(255), nullable=False),
            sa.Column("allowed_roles", postgresql.JSONB(), nullable=True),
        )
    else:
        if not _column_exists("workflow_transitions", "from_state"):
            # Detect workflow_states id type for FK
            ws_id_is_uuid = False
            if _table_exists("workflow_states"):
                for col in inspector.get_columns("workflow_states"):
                    if col.get("name") == "id":
                        ws_id_is_uuid = isinstance(col.get("type"), postgresql.UUID)
                        break
            state_id_type = GUID() if ws_id_is_uuid else sa.Integer()
            op.add_column("workflow_transitions", sa.Column("from_state", state_id_type, nullable=True))
        
        if not _column_exists("workflow_transitions", "to_state"):
            # Detect workflow_states id type for FK
            ws_id_is_uuid = False
            if _table_exists("workflow_states"):
                for col in inspector.get_columns("workflow_states"):
                    if col.get("name") == "id":
                        ws_id_is_uuid = isinstance(col.get("type"), postgresql.UUID)
                        break
            state_id_type = GUID() if ws_id_is_uuid else sa.Integer()
            op.add_column("workflow_transitions", sa.Column("to_state", state_id_type, nullable=True))
        
        if not _column_exists("workflow_transitions", "action_label"):
            op.add_column("workflow_transitions", sa.Column("action_label", sa.String(255), nullable=True))
        if not _column_exists("workflow_transitions", "allowed_roles"):
            op.add_column("workflow_transitions", sa.Column("allowed_roles", postgresql.JSONB(), nullable=True))
        
        _ensure_jsonb("workflow_transitions", "allowed_roles")
        
        if _column_exists("workflow_transitions", "from_state") and not _fk_exists("workflow_transitions", "fk_workflow_transitions_from_state"):
            op.create_foreign_key(
                "fk_workflow_transitions_from_state",
                "workflow_transitions",
                "workflow_states",
                ["from_state"],
                ["id"],
                ondelete="CASCADE",
            )
        
        if _column_exists("workflow_transitions", "to_state") and not _fk_exists("workflow_transitions", "fk_workflow_transitions_to_state"):
            op.create_foreign_key(
                "fk_workflow_transitions_to_state",
                "workflow_transitions",
                "workflow_states",
                ["to_state"],
                ["id"],
                ondelete="CASCADE",
            )

    # Seed workflow definitions FIRST (required by workflow_states FK)
    if _table_exists("workflow_definitions") and _is_table_empty("workflow_definitions"):
        definitions_table = sa.table(
            "workflow_definitions",
            sa.column("id", sa.Integer),
            sa.column("entity_type", sa.String),
            sa.column("name", sa.String),
            sa.column("organization_id", sa.Integer),
        )

        definitions = [
            {"id": 1, "entity_type": "control", "name": "Control Workflow", "organization_id": None},
            {"id": 2, "entity_type": "risk", "name": "Risk Workflow", "organization_id": None},
            {"id": 3, "entity_type": "evidence", "name": "Evidence Workflow", "organization_id": None},
            {"id": 4, "entity_type": "assessment", "name": "Assessment Workflow", "organization_id": None},
            {"id": 5, "entity_type": "finding", "name": "Finding Workflow", "organization_id": None},
        ]

        op.bulk_insert(definitions_table, definitions)

    # Seed workflow states and transitions
    state_table = sa.table(
        "workflow_states",
        sa.column("id", GUID()),
        sa.column("definition_id", sa.Integer),
        sa.column("key", sa.String),
        sa.column("name", sa.String),
        sa.column("name_ar", sa.String),
        sa.column("entity_type", sa.String),
        sa.column("state_key", sa.String),
        sa.column("label", sa.String),
        sa.column("order_index", sa.Integer),
        sa.column("organization_id", sa.Integer),
    )

    # Detect workflow_states id type for transitions
    ws_id_is_uuid = False
    if _table_exists("workflow_states"):
        for col in inspector.get_columns("workflow_states"):
            if col.get("name") == "id":
                ws_id_is_uuid = isinstance(col.get("type"), postgresql.UUID)
                break
    
    state_fk_type = GUID() if ws_id_is_uuid else sa.Integer()

    transition_table = sa.table(
        "workflow_transitions",
        sa.column("id", GUID()),
        sa.column("definition_id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("from_state_id", state_fk_type),
        sa.column("to_state_id", state_fk_type),
        sa.column("from_state", state_fk_type),
        sa.column("to_state", state_fk_type),
        sa.column("action_label", sa.String),
        sa.column("allowed_roles", sa.JSON),
    )

    state_ids = {}
    def _add_state(entity, key, label, order, definition_id):
        return {
            "definition_id": definition_id,
            "key": key,
            "name": label,
            "name_ar": label,
            "entity_type": entity,
            "state_key": key,
            "label": label,
            "order_index": order,
            "organization_id": None,
        }

    states = []
    # Control workflow
    states += [
        _add_state("control", "not_started", "Not Started", 1, 1),
        _add_state("control", "in_progress", "In Progress", 2, 1),
        _add_state("control", "compliant", "Compliant", 3, 1),
        _add_state("control", "non_compliant", "Non-Compliant", 4, 1),
        _add_state("control", "not_applicable", "Not Applicable", 5, 1),
    ]
    # Risk workflow
    states += [
        _add_state("risk", "identified", "Identified", 1, 2),
        _add_state("risk", "assessed", "Assessed", 2, 2),
        _add_state("risk", "treated", "Treated", 3, 2),
        _add_state("risk", "accepted", "Accepted", 4, 2),
        _add_state("risk", "transferred", "Transferred", 5, 2),
        _add_state("risk", "mitigated", "Mitigated", 6, 2),
        _add_state("risk", "closed", "Closed", 7, 2),
    ]
    # Evidence workflow
    states += [
        _add_state("evidence", "pending", "Pending", 1, 3),
        _add_state("evidence", "collected", "Collected", 2, 3),
        _add_state("evidence", "validated", "Validated", 3, 3),
        _add_state("evidence", "rejected", "Rejected", 4, 3),
        _add_state("evidence", "expired", "Expired", 5, 3),
    ]
    # Assessment workflow
    states += [
        _add_state("assessment", "draft", "Draft", 1, 4),
        _add_state("assessment", "launched", "Launched", 2, 4),
        _add_state("assessment", "in_progress", "In Progress", 3, 4),
        _add_state("assessment", "submitted", "Submitted", 4, 4),
        _add_state("assessment", "reviewed", "Reviewed", 5, 4),
        _add_state("assessment", "approved", "Approved", 6, 4),
        _add_state("assessment", "rejected", "Rejected", 7, 4),
        _add_state("assessment", "closed", "Closed", 8, 4),
    ]
    # Finding workflow
    states += [
        _add_state("finding", "open", "Open", 1, 5),
        _add_state("finding", "in_progress", "In Progress", 2, 5),
        _add_state("finding", "pending_verification", "Pending Verification", 3, 5),
        _add_state("finding", "verified", "Verified", 4, 5),
        _add_state("finding", "risk_accepted", "Risk Accepted", 5, 5),
        _add_state("finding", "closed", "Closed", 6, 5),
    ]

    inserted_states = False
    if _table_exists("workflow_states") and _is_table_empty("workflow_states"):
        id_is_uuid = False
        for col in inspector.get_columns("workflow_states"):
            if col.get("name") == "id":
                id_is_uuid = isinstance(col.get("type"), postgresql.UUID)
                break

        if id_is_uuid:
            states_with_ids = []
            for state in states:
                state_id = uuid.uuid4()
                state_ids[(state["entity_type"], state["state_key"])] = state_id
                states_with_ids.append({**state, "id": state_id})
            op.bulk_insert(state_table, states_with_ids)
        else:
            op.bulk_insert(state_table, states)
            entity_values = list({s["entity_type"] for s in states})
            result = bind.execute(
                sa.text(
                    "SELECT id, entity_type, state_key "
                    "FROM workflow_states "
                    "WHERE entity_type = ANY(:entities)"
                ),
                {"entities": entity_values},
            )
            for row in result:
                state_ids[(row.entity_type, row.state_key)] = row.id

        inserted_states = True

    def _add_transition(entity, from_key, to_key, label):
        return (entity, from_key, to_key, label)

    transitions = []
    # Control transitions
    transitions += [
        _add_transition("control", "not_started", "in_progress", "Start"),
        _add_transition("control", "not_started", "not_applicable", "Mark Not Applicable"),
        _add_transition("control", "in_progress", "compliant", "Mark Compliant"),
        _add_transition("control", "in_progress", "non_compliant", "Mark Non-Compliant"),
        _add_transition("control", "in_progress", "not_applicable", "Mark Not Applicable"),
        _add_transition("control", "non_compliant", "in_progress", "Reopen"),
        _add_transition("control", "non_compliant", "not_applicable", "Mark Not Applicable"),
        _add_transition("control", "compliant", "in_progress", "Reopen"),
        _add_transition("control", "compliant", "non_compliant", "Mark Non-Compliant"),
        _add_transition("control", "compliant", "not_applicable", "Mark Not Applicable"),
        _add_transition("control", "not_applicable", "not_started", "Reset"),
    ]
    # Risk transitions
    transitions += [
        _add_transition("risk", "identified", "assessed", "Assess"),
        _add_transition("risk", "assessed", "treated", "Treat"),
        _add_transition("risk", "assessed", "accepted", "Accept"),
        _add_transition("risk", "assessed", "transferred", "Transfer"),
        _add_transition("risk", "assessed", "mitigated", "Mitigate"),
        _add_transition("risk", "treated", "mitigated", "Mitigate"),
        _add_transition("risk", "treated", "closed", "Close"),
        _add_transition("risk", "accepted", "closed", "Close"),
        _add_transition("risk", "transferred", "closed", "Close"),
        _add_transition("risk", "mitigated", "closed", "Close"),
    ]
    # Evidence transitions
    transitions += [
        _add_transition("evidence", "pending", "collected", "Collect"),
        _add_transition("evidence", "collected", "validated", "Validate"),
        _add_transition("evidence", "collected", "rejected", "Reject"),
        _add_transition("evidence", "rejected", "collected", "Re-collect"),
        _add_transition("evidence", "validated", "expired", "Expire"),
    ]
    # Assessment transitions
    transitions += [
        _add_transition("assessment", "draft", "launched", "Launch"),
        _add_transition("assessment", "launched", "in_progress", "Start"),
        _add_transition("assessment", "launched", "draft", "Revert"),
        _add_transition("assessment", "in_progress", "submitted", "Submit"),
        _add_transition("assessment", "submitted", "reviewed", "Review"),
        _add_transition("assessment", "reviewed", "approved", "Approve"),
        _add_transition("assessment", "reviewed", "rejected", "Reject"),
        _add_transition("assessment", "approved", "closed", "Close"),
        _add_transition("assessment", "rejected", "draft", "Rework"),
    ]
    # Finding transitions
    transitions += [
        _add_transition("finding", "open", "in_progress", "Start"),
        _add_transition("finding", "in_progress", "pending_verification", "Submit for Verification"),
        _add_transition("finding", "pending_verification", "verified", "Verify"),
        _add_transition("finding", "pending_verification", "in_progress", "Reopen"),
        _add_transition("finding", "verified", "closed", "Close"),
        _add_transition("finding", "open", "risk_accepted", "Accept Risk"),
        _add_transition("finding", "risk_accepted", "closed", "Close"),
    ]

    if inserted_states and _table_exists("workflow_transitions") and _is_table_empty("workflow_transitions"):
        # Detect if workflow_transitions.id is UUID or INTEGER
        wt_id_is_uuid = False
        if _table_exists("workflow_transitions"):
            for col in inspector.get_columns("workflow_transitions"):
                if col.get("name") == "id":
                    wt_id_is_uuid = isinstance(col.get("type"), postgresql.UUID)
                    break
        
        # Entity type to definition_id mapping
        entity_to_definition = {
            "control": 1,
            "risk": 2,
            "evidence": 3,
            "assessment": 4,
            "finding": 5,
        }
        
        transition_rows = []
        for entity, from_key, to_key, label in transitions:
            from_id = state_ids.get((entity, from_key))
            to_id = state_ids.get((entity, to_key))
            if not from_id or not to_id:
                continue
            
            row = {
                "action_label": label,
                "allowed_roles": None,
            }
            
            # Support both legacy and new column names
            if _column_exists("workflow_transitions", "from_state_id"):
                row["from_state_id"] = from_id
            if _column_exists("workflow_transitions", "to_state_id"):
                row["to_state_id"] = to_id
            if _column_exists("workflow_transitions", "from_state"):
                row["from_state"] = from_id
            if _column_exists("workflow_transitions", "to_state"):
                row["to_state"] = to_id
            
            # Add definition_id if column exists
            if _column_exists("workflow_transitions", "definition_id"):
                row["definition_id"] = entity_to_definition.get(entity)
            
            # Add name if column exists (use action_label as value)
            if _column_exists("workflow_transitions", "name"):
                row["name"] = label
            
            # Only include id if table uses UUID (otherwise let SERIAL auto-generate)
            if wt_id_is_uuid:
                row["id"] = uuid.uuid4()
            
            transition_rows.append(row)
        
        if transition_rows:
            op.bulk_insert(transition_table, transition_rows)

    # Dashboard configuration
    if not _table_exists("dashboard_widgets"):
        op.create_table(
            "dashboard_widgets",
            sa.Column("id", GUID(), primary_key=True, default=uuid.uuid4),
            sa.Column("widget_key", sa.String(100), nullable=False, unique=True),
            sa.Column("title", sa.String(255), nullable=False),
            sa.Column("component_type", sa.String(100), nullable=False),
            sa.Column("data_source", sa.String(100), nullable=True),
            sa.Column("config_json", postgresql.JSONB(), nullable=True),
        )
    else:
        _ensure_jsonb("dashboard_widgets", "config_json")

    if not _table_exists("dashboard_layouts"):
        op.create_table(
            "dashboard_layouts",
            sa.Column("id", GUID(), primary_key=True, default=uuid.uuid4),
            sa.Column("organization_id", sa.Integer(), sa.ForeignKey("organizations.id"), nullable=True, index=True),
            sa.Column("widget_id", GUID(), sa.ForeignKey("dashboard_widgets.id", ondelete="CASCADE"), nullable=False),
            sa.Column("position", postgresql.JSONB(), nullable=True),
            sa.Column("size", postgresql.JSONB(), nullable=True),
        )
    else:
        _ensure_jsonb("dashboard_layouts", "position")
        _ensure_jsonb("dashboard_layouts", "size")
    if not _index_exists("dashboard_layouts", "ix_dashboard_layouts_org"):
        op.create_index("ix_dashboard_layouts_org", "dashboard_layouts", ["organization_id"], unique=False)

    # UI configuration
    if not _table_exists("ui_pages"):
        op.create_table(
            "ui_pages",
            sa.Column("id", GUID(), primary_key=True, default=uuid.uuid4),
            sa.Column("page_key", sa.String(100), nullable=False, unique=True),
            sa.Column("title", sa.String(255), nullable=False),
        )

    if not _table_exists("ui_sections"):
        op.create_table(
            "ui_sections",
            sa.Column("id", GUID(), primary_key=True, default=uuid.uuid4),
            sa.Column("page_id", GUID(), sa.ForeignKey("ui_pages.id", ondelete="CASCADE"), nullable=False),
            sa.Column("section_key", sa.String(100), nullable=False),
            sa.Column("title", sa.String(255), nullable=False),
            sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
            sa.UniqueConstraint("page_id", "section_key", name="uq_ui_section_key"),
        )
    else:
        if not _unique_exists("ui_sections", "uq_ui_section_key"):
            op.create_unique_constraint("uq_ui_section_key", "ui_sections", ["page_id", "section_key"])
    if not _index_exists("ui_sections", "ix_ui_sections_page"):
        op.create_index("ix_ui_sections_page", "ui_sections", ["page_id"], unique=False)

    if not _table_exists("ui_field_placements"):
        op.create_table(
            "ui_field_placements",
            sa.Column("id", GUID(), primary_key=True, default=uuid.uuid4),
            sa.Column("section_id", GUID(), sa.ForeignKey("ui_sections.id", ondelete="CASCADE"), nullable=False),
            sa.Column("field_key", sa.String(100), nullable=False),
            sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
        )
    if not _index_exists("ui_field_placements", "ix_ui_field_placements_section"):
        op.create_index("ix_ui_field_placements_section", "ui_field_placements", ["section_id"], unique=False)

    # Report templates
    if not _table_exists("report_templates"):
        op.create_table(
            "report_templates",
            sa.Column("id", GUID(), primary_key=True, default=uuid.uuid4),
            sa.Column("template_key", sa.String(100), nullable=False, unique=True, index=True),
            sa.Column("name", sa.String(255), nullable=False),
            sa.Column("entity_type", sa.String(50), nullable=True),
            sa.Column("query_config", postgresql.JSONB(), nullable=True),
            sa.Column("export_format", sa.String(20), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        )
    else:
        _ensure_jsonb("report_templates", "query_config")

    # Seed default dashboard widgets
    widget_table = sa.table(
        "dashboard_widgets",
        sa.column("id", GUID()),
        sa.column("widget_key", sa.String),
        sa.column("title", sa.String),
        sa.column("component_type", sa.String),
        sa.column("data_source", sa.String),
        sa.column("config_json", sa.JSON),
    )

    widget_ids = {
        "risk_heatmap": uuid.uuid4(),
        "compliance_gauge": uuid.uuid4(),
        "compliance_trend": uuid.uuid4(),
        "activity_timeline": uuid.uuid4(),
        "task_widget": uuid.uuid4(),
        "security_incidents": uuid.uuid4(),
    }

    if _table_exists("dashboard_widgets") and _is_table_empty("dashboard_widgets"):
        op.bulk_insert(
            widget_table,
            [
                {
                    "id": widget_ids["risk_heatmap"],
                    "widget_key": "risk_heatmap",
                    "title": "Risk Heat Map",
                    "component_type": "risk_heatmap",
                    "data_source": "risk",
                    "config_json": {"limit": 5},
                },
                {
                    "id": widget_ids["compliance_gauge"],
                    "widget_key": "compliance_gauge",
                    "title": "Compliance Gauge",
                    "component_type": "compliance_gauge",
                    "data_source": "compliance",
                    "config_json": {"framework": "ECC"},
                },
                {
                    "id": widget_ids["compliance_trend"],
                    "widget_key": "compliance_trend",
                    "title": "Compliance Trend",
                    "component_type": "compliance_trend",
                    "data_source": "compliance",
                    "config_json": {"months": 7},
                },
                {
                    "id": widget_ids["activity_timeline"],
                    "widget_key": "activity_timeline",
                    "title": "Activity Timeline",
                    "component_type": "activity_timeline",
                    "data_source": "activity",
                    "config_json": {"limit": 4},
                },
                {
                    "id": widget_ids["task_widget"],
                    "widget_key": "task_widget",
                    "title": "Tasks",
                    "component_type": "task_widget",
                    "data_source": "tasks",
                    "config_json": {"limit": 4},
                },
                {
                    "id": widget_ids["security_incidents"],
                    "widget_key": "security_incidents",
                    "title": "Security Incidents",
                    "component_type": "security_incident_feed",
                    "data_source": "incidents",
                    "config_json": {"limit": 5},
                },
            ],
        )

    layout_table = sa.table(
        "dashboard_layouts",
        sa.column("id", GUID()),
        sa.column("organization_id", sa.Integer),
        sa.column("widget_id", GUID()),
        sa.column("position", sa.JSON),
        sa.column("size", sa.JSON),
    )

    if _table_exists("dashboard_layouts") and _is_table_empty("dashboard_layouts"):
        op.bulk_insert(
            layout_table,
            [
                {
                    "id": uuid.uuid4(),
                    "organization_id": None,
                    "widget_id": widget_ids["compliance_gauge"],
                    "position": {"x": 0, "y": 0},
                    "size": {"w": 6, "h": 4},
                },
                {
                    "id": uuid.uuid4(),
                    "organization_id": None,
                    "widget_id": widget_ids["risk_heatmap"],
                    "position": {"x": 6, "y": 0},
                    "size": {"w": 6, "h": 4},
                },
                {
                    "id": uuid.uuid4(),
                    "organization_id": None,
                    "widget_id": widget_ids["compliance_trend"],
                    "position": {"x": 0, "y": 4},
                    "size": {"w": 12, "h": 4},
                },
                {
                    "id": uuid.uuid4(),
                    "organization_id": None,
                    "widget_id": widget_ids["activity_timeline"],
                    "position": {"x": 0, "y": 8},
                    "size": {"w": 6, "h": 4},
                },
                {
                    "id": uuid.uuid4(),
                    "organization_id": None,
                    "widget_id": widget_ids["task_widget"],
                    "position": {"x": 6, "y": 8},
                    "size": {"w": 6, "h": 4},
                },
                {
                    "id": uuid.uuid4(),
                    "organization_id": None,
                    "widget_id": widget_ids["security_incidents"],
                    "position": {"x": 0, "y": 12},
                    "size": {"w": 12, "h": 4},
                },
            ],
        )

    # UI pages and sections
    page_table = sa.table(
        "ui_pages",
        sa.column("id", GUID()),
        sa.column("page_key", sa.String),
        sa.column("title", sa.String),
    )

    page_ids = {
        "dashboard": uuid.uuid4(),
        "risks": uuid.uuid4(),
        "controls": uuid.uuid4(),
        "evidence": uuid.uuid4(),
        "reports": uuid.uuid4(),
    }

    if _table_exists("ui_pages") and _is_table_empty("ui_pages"):
        op.bulk_insert(
            page_table,
            [
                {"id": page_ids["dashboard"], "page_key": "dashboard", "title": "Dashboard"},
                {"id": page_ids["risks"], "page_key": "risks", "title": "Risks"},
                {"id": page_ids["controls"], "page_key": "controls", "title": "Controls"},
                {"id": page_ids["evidence"], "page_key": "evidence", "title": "Evidence"},
                {"id": page_ids["reports"], "page_key": "reports", "title": "Reports"},
            ],
        )

    section_table = sa.table(
        "ui_sections",
        sa.column("id", GUID()),
        sa.column("page_id", GUID()),
        sa.column("section_key", sa.String),
        sa.column("title", sa.String),
        sa.column("order_index", sa.Integer),
    )

    section_ids = {
        "dashboard_widgets": uuid.uuid4(),
        "risk_custom_fields": uuid.uuid4(),
        "control_custom_fields": uuid.uuid4(),
        "evidence_custom_fields": uuid.uuid4(),
        "report_templates": uuid.uuid4(),
    }

    if _table_exists("ui_sections") and _is_table_empty("ui_sections"):
        op.bulk_insert(
            section_table,
            [
                {
                    "id": section_ids["dashboard_widgets"],
                    "page_id": page_ids["dashboard"],
                    "section_key": "widgets",
                    "title": "Dashboard Widgets",
                    "order_index": 1,
                },
                {
                    "id": section_ids["risk_custom_fields"],
                    "page_id": page_ids["risks"],
                    "section_key": "custom_fields",
                    "title": "Risk Custom Fields",
                    "order_index": 10,
                },
                {
                    "id": section_ids["control_custom_fields"],
                    "page_id": page_ids["controls"],
                    "section_key": "custom_fields",
                    "title": "Control Custom Fields",
                    "order_index": 10,
                },
                {
                    "id": section_ids["evidence_custom_fields"],
                    "page_id": page_ids["evidence"],
                    "section_key": "custom_fields",
                    "title": "Evidence Custom Fields",
                    "order_index": 10,
                },
                {
                    "id": section_ids["report_templates"],
                    "page_id": page_ids["reports"],
                    "section_key": "templates",
                    "title": "Report Templates",
                    "order_index": 1,
                },
            ],
        )

    # Report templates seed
    report_template_table = sa.table(
        "report_templates",
        sa.column("id", GUID()),
        sa.column("template_key", sa.String),
        sa.column("name", sa.String),
        sa.column("entity_type", sa.String),
        sa.column("query_config", sa.JSON),
        sa.column("export_format", sa.String),
    )

    if _table_exists("report_templates") and _is_table_empty("report_templates"):
        op.bulk_insert(
            report_template_table,
            [
                {
                    "id": uuid.uuid4(),
                    "template_key": "compliance_summary",
                    "name": "Compliance Status Report",
                    "entity_type": "control",
                    "query_config": {"report_type": "compliance_summary", "framework_filter": ["ECC", "CCC", "PDPL"]},
                    "export_format": "pdf",
                },
                {
                    "id": uuid.uuid4(),
                    "template_key": "control_posture",
                    "name": "Control Posture Report",
                    "entity_type": "control",
                    "query_config": {"report_type": "control_posture", "framework_filter": ["ECC", "CCC", "PDPL"]},
                    "export_format": "pdf",
                },
                {
                    "id": uuid.uuid4(),
                    "template_key": "evidence_status",
                    "name": "Evidence Coverage Report",
                    "entity_type": "evidence",
                    "query_config": {"report_type": "evidence_status"},
                    "export_format": "pdf",
                },
                {
                    "id": uuid.uuid4(),
                    "template_key": "risk_heatmap",
                    "name": "Risk Heatmap",
                    "entity_type": "risk",
                    "query_config": {"report_type": "risk_heatmap"},
                    "export_format": "pdf",
                },
                {
                    "id": uuid.uuid4(),
                    "template_key": "audit_readiness",
                    "name": "Audit Trail Report",
                    "entity_type": "audit",
                    "query_config": {"report_type": "audit_readiness"},
                    "export_format": "pdf",
                },
                {
                    "id": uuid.uuid4(),
                    "template_key": "executive_dashboard",
                    "name": "Executive Summary",
                    "entity_type": "dashboard",
                    "query_config": {"report_type": "executive_dashboard"},
                    "export_format": "pdf",
                },
            ],
        )


def downgrade() -> None:
    op.drop_table("report_templates")
    op.drop_index("ix_ui_field_placements_section", table_name="ui_field_placements")
    op.drop_table("ui_field_placements")
    op.drop_index("ix_ui_sections_page", table_name="ui_sections")
    op.drop_table("ui_sections")
    op.drop_table("ui_pages")
    op.drop_index("ix_dashboard_layouts_org", table_name="dashboard_layouts")
    op.drop_table("dashboard_layouts")
    op.drop_table("dashboard_widgets")
    op.drop_table("workflow_transitions")
    op.drop_index("ix_workflow_states_entity_org", table_name="workflow_states")
    op.drop_table("workflow_states")
    op.drop_index("ix_custom_field_values_entity", table_name="custom_field_values")
    op.drop_table("custom_field_values")
    op.drop_index("ix_custom_fields_entity_org", table_name="custom_fields")
    op.drop_table("custom_fields")
