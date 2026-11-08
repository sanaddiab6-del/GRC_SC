"""Independent SICO engagement ledger; does NOT alter legacy CISO Assistant tables.

IDs to GRC records are intentional UUID references, not database foreign keys:
this new migration has no dependency on the historical core/iam migration graph.
References must ALWAYS be resolved with exact folder + RBAC checks at use time.
"""
from __future__ import annotations

import uuid
from django.db import models


class Engagement(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        IN_PROGRESS = 'in_progress', 'In progress'
        NEEDS_REVIEW = 'needs_review', 'Needs human review'
        ON_HOLD = 'on_hold', 'On hold'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    folder_id = models.UUIDField(db_index=True)
    created_by_id = models.CharField(max_length=128, db_index=True)
    title = models.CharField(max_length=200)
    objective = models.TextField(max_length=4000)
    framework_id = models.UUIDField(null=True, blank=True)
    compliance_assessment_id = models.UUIDField(null=True, blank=True)
    risk_assessment_id = models.UUIDField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    plan = models.JSONField(default=dict)  # advisory workflow; never a compliance verdict
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']


class EngagementExecution(models.Model):
    class Status(models.TextChoices):
        PREPARED = 'prepared', 'Dry-run prepared'
        COMMITTED = 'committed', 'Approved operation committed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    engagement = models.ForeignKey(Engagement, on_delete=models.PROTECT, related_name='executions')
    stage = models.CharField(max_length=80)
    batch_key = models.CharField(max_length=80, default='default')
    status = models.CharField(max_length=20, choices=Status.choices)
    prepared_digest = models.CharField(max_length=64, blank=True)
    prepared_result = models.JSONField(default=dict)
    committed_digest = models.CharField(max_length=64, blank=True)
    committed_result = models.JSONField(default=dict)
    approved_by_id = models.CharField(max_length=128, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['engagement', 'stage', 'batch_key'],
                name='sico_eng_exec_unique_stage_batch',
            ),
        ]
        ordering = ['created_at']
