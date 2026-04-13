import uuid
import iam.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0147_repair_requirementnode_questions_column"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="WorkflowCase",
            fields=[
                (
                    "id",
                    models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Created at")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Updated at")),
                ("is_published", models.BooleanField(default=False, verbose_name="published")),
                ("name", models.CharField(max_length=200, verbose_name="Name")),
                (
                    "description",
                    models.TextField(blank=True, null=True, verbose_name="Description"),
                ),
                ("eta", models.DateField(blank=True, null=True, verbose_name="ETA")),
                (
                    "due_date",
                    models.DateField(blank=True, null=True, verbose_name="Due date"),
                ),
                (
                    "ref_id",
                    models.CharField(blank=True, max_length=100, null=True, verbose_name="Reference ID"),
                ),
                (
                    "workflow_type",
                    models.CharField(
                        choices=[
                            ("risk", "Risk"),
                            ("finding", "Finding"),
                            ("exception", "Exception"),
                            ("incident", "Incident"),
                            ("vendor", "Vendor"),
                        ],
                        default="finding",
                        max_length=32,
                    ),
                ),
                (
                    "classification",
                    models.CharField(
                        choices=[
                            ("audit_finding", "Audit finding"),
                            ("compliance_gap", "Compliance gap"),
                            ("control_deficiency", "Control deficiency"),
                            ("risk_observation", "Risk observation"),
                            ("security_exception", "Security exception"),
                            ("incident", "Incident"),
                            ("vendor_issue", "Vendor issue"),
                        ],
                        default="control_deficiency",
                        max_length=32,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("open", "Open"),
                            ("in_progress", "In progress"),
                            ("in_review", "In review"),
                            ("closed", "Closed"),
                            ("closed_with_monitoring", "Closed with monitoring"),
                            ("reopened", "Reopened"),
                        ],
                        default="draft",
                        max_length=32,
                    ),
                ),
                (
                    "treatment_decision",
                    models.CharField(
                        choices=[
                            ("undecided", "Undecided"),
                            ("accept", "Accept"),
                            ("remediate", "Remediate"),
                            ("compensate", "Compensating control"),
                            ("escalate", "Escalate"),
                            ("monitor", "Monitor"),
                        ],
                        default="undecided",
                        max_length=32,
                    ),
                ),
                ("domain", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "severity",
                    models.SmallIntegerField(
                        choices=[(-1, "--"), (0, "Info"), (1, "Low"), (2, "Medium"), (3, "High"), (4, "Critical")],
                        default=-1,
                    ),
                ),
                (
                    "require_evidence_for_closure",
                    models.BooleanField(default=True),
                ),
                (
                    "require_approval_for_closure",
                    models.BooleanField(default=True),
                ),
                (
                    "require_task_completion_for_closure",
                    models.BooleanField(default=True),
                ),
                (
                    "require_recurring_control_for_closure",
                    models.BooleanField(default=False),
                ),
                (
                    "require_residual_risk_reassessment",
                    models.BooleanField(default=False),
                ),
                ("recurring_control_confirmed", models.BooleanField(default=False)),
                ("monitoring_required", models.BooleanField(default=False)),
                (
                    "residual_risk_reassessed_at",
                    models.DateTimeField(blank=True, null=True),
                ),
                (
                    "residual_risk_summary",
                    models.TextField(blank=True, null=True),
                ),
                ("closure_notes", models.TextField(blank=True, null=True)),
                ("closed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "affected_assets",
                    models.ManyToManyField(blank=True, related_name="workflow_cases", to="core.asset"),
                ),
                (
                    "applied_controls",
                    models.ManyToManyField(blank=True, related_name="workflow_cases", to="core.appliedcontrol"),
                ),
                (
                    "evidences",
                    models.ManyToManyField(blank=True, related_name="workflow_cases", to="core.evidence"),
                ),
                (
                    "filtering_labels",
                    models.ManyToManyField(blank=True, to="core.filteringlabel", verbose_name="Labels"),
                ),
                (
                    "findings",
                    models.ManyToManyField(blank=True, related_name="workflow_cases", to="core.finding"),
                ),
                (
                    "findings_assessments",
                    models.ManyToManyField(blank=True, related_name="workflow_cases", to="core.findingsassessment"),
                ),
                (
                    "folder",
                    models.ForeignKey(default=iam.models.Folder.get_root_folder_id, on_delete=django.db.models.deletion.CASCADE, related_name="%(class)s_folder", to="iam.folder"),
                ),
                (
                    "incidents",
                    models.ManyToManyField(blank=True, related_name="workflow_cases", to="core.incident"),
                ),
                (
                    "owners",
                    models.ManyToManyField(blank=True, related_name="workflow_cases", to="core.actor"),
                ),
                (
                    "requirement_assessments",
                    models.ManyToManyField(blank=True, related_name="workflow_cases", to="core.requirementassessment"),
                ),
                (
                    "residual_risk_reassessed_by",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="workflow_cases_reassessed", to=settings.AUTH_USER_MODEL),
                ),
                (
                    "reviewers",
                    models.ManyToManyField(blank=True, related_name="workflow_case_reviews", to="core.actor"),
                ),
                (
                    "risk_scenarios",
                    models.ManyToManyField(blank=True, related_name="workflow_cases", to="core.riskscenario"),
                ),
                (
                    "security_exceptions",
                    models.ManyToManyField(blank=True, related_name="workflow_cases", to="core.securityexception"),
                ),
                (
                    "task_templates",
                    models.ManyToManyField(blank=True, related_name="workflow_cases", to="core.tasktemplate"),
                ),
                (
                    "validation_flows",
                    models.ManyToManyField(blank=True, related_name="workflow_cases", to="core.validationflow"),
                ),
            ],
            options={
                "verbose_name": "Workflow case",
                "verbose_name_plural": "Workflow cases",
            },
        ),
        migrations.CreateModel(
            name="WorkflowCaseEvent",
            fields=[
                (
                    "id",
                    models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Created at")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Updated at")),
                ("is_published", models.BooleanField(default=False, verbose_name="published")),
                ("event_type", models.CharField(max_length=100, verbose_name="Event type")),
                ("event_notes", models.TextField(blank=True, null=True, verbose_name="Notes")),
                (
                    "event_actor",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="workflow_case_events", to=settings.AUTH_USER_MODEL),
                ),
                (
                    "folder",
                    models.ForeignKey(default=iam.models.Folder.get_root_folder_id, on_delete=django.db.models.deletion.CASCADE, related_name="%(class)s_folder", to="iam.folder"),
                ),
                (
                    "workflow_case",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="events", to="core.workflowcase"),
                ),
            ],
            options={
                "verbose_name": "Workflow case event",
                "verbose_name_plural": "Workflow case events",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="WorkflowCaseApprovalStep",
            fields=[
                (
                    "id",
                    models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Created at")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Updated at")),
                ("is_published", models.BooleanField(default=False, verbose_name="published")),
                ("sequence", models.PositiveIntegerField(default=1, verbose_name="Sequence")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("approved", "Approved"),
                            ("rejected", "Rejected"),
                            ("changes_requested", "Changes requested"),
                        ],
                        default="pending",
                        max_length=32,
                    ),
                ),
                ("is_required", models.BooleanField(default=True, verbose_name="Required")),
                ("notes", models.TextField(blank=True, null=True, verbose_name="Notes")),
                ("acted_at", models.DateTimeField(blank=True, null=True, verbose_name="Acted at")),
                (
                    "approver",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="workflow_case_approval_steps", to=settings.AUTH_USER_MODEL),
                ),
                (
                    "folder",
                    models.ForeignKey(default=iam.models.Folder.get_root_folder_id, on_delete=django.db.models.deletion.CASCADE, related_name="%(class)s_folder", to="iam.folder"),
                ),
                (
                    "workflow_case",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="approval_steps", to="core.workflowcase"),
                ),
            ],
            options={
                "verbose_name": "Workflow case approval step",
                "verbose_name_plural": "Workflow case approval steps",
                "ordering": ["sequence", "created_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="workflowcaseapprovalstep",
            constraint=models.UniqueConstraint(fields=("workflow_case", "sequence"), name="unique_workflow_case_approval_sequence"),
        ),
    ]