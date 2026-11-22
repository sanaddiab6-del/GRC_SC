"""Creates only SICO engagement metadata and execution ledger tables.

No legacy CISO Assistant tables, roles, or tenant ownership are modified.
"""
import uuid
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name='Engagement',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ('folder_id', models.UUIDField(db_index=True)),
                ('created_by_id', models.CharField(max_length=128, db_index=True)),
                ('title', models.CharField(max_length=200)),
                ('objective', models.TextField(max_length=4000)),
                ('framework_id', models.UUIDField(null=True, blank=True)),
                ('compliance_assessment_id', models.UUIDField(null=True, blank=True)),
                ('risk_assessment_id', models.UUIDField(null=True, blank=True)),
                ('status', models.CharField(max_length=20, default='draft', choices=[('draft', 'Draft'), ('in_progress', 'In progress'), ('needs_review', 'Needs human review'), ('on_hold', 'On hold')])),
                ('plan', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='EngagementExecution',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ('stage', models.CharField(max_length=80)),
                ('batch_key', models.CharField(max_length=80, default='default')),
                ('status', models.CharField(max_length=20, choices=[('prepared','Dry-run prepared'), ('committed', 'Approved operation committed')])),
                ('prepared_digest', models.CharField(max_length=64, blank=True)),
                ('prepared_result', models.JSONField(default=dict)),
                ('committed_digest', models.CharField(max_length=64, blank=True)),
                ('committed_result', models.JSONField(default=dict)),
                ('approved_by_id', models.CharField(max_length=128, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('engagement', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='executions', to='ai_onboarding.engagement')),
            ],
            options={'ordering': ['created_at']},
        ),
        migrations.AddConstraint(
            model_name='engagementexecution',
            constraint=models.UniqueConstraint(fields=('engagement','stage','batch_key'), name='sico_eng_exec_unique_stage_batch'),
        ),
    ]
