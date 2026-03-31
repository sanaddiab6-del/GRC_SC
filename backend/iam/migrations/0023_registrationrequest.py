"""
Migration 0023 – Add RegistrationRequest model for self-service user onboarding.

Stores registration requests with a pending/approved/rejected workflow.
Admin approval is required before a user account is created.
"""

import uuid
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("iam", "0022_add_role_tier"),
    ]

    operations = [
        migrations.CreateModel(
            name="RegistrationRequest",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "email",
                    models.EmailField(max_length=100),
                ),
                ("first_name", models.CharField(max_length=150)),
                ("last_name", models.CharField(max_length=150)),
                (
                    "company",
                    models.CharField(
                        max_length=200,
                        verbose_name="Company / Organization",
                    ),
                ),
                (
                    "job_title",
                    models.CharField(max_length=150, verbose_name="Job title"),
                ),
                (
                    "phone",
                    models.CharField(
                        blank=True, max_length=30, verbose_name="Phone number"
                    ),
                ),
                (
                    "department",
                    models.CharField(
                        blank=True,
                        max_length=150,
                        verbose_name="Department / Domain",
                    ),
                ),
                (
                    "reason",
                    models.TextField(verbose_name="Reason for requesting access"),
                ),
                ("password_hash", models.CharField(max_length=256)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("approved", "Approved"),
                            ("rejected", "Rejected"),
                        ],
                        db_index=True,
                        default="pending",
                        max_length=10,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("review_notes", models.TextField(blank=True)),
                (
                    "reviewed_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="reviewed_registrations",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "assigned_user_groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="User groups to assign upon approval.",
                        to="iam.usergroup",
                    ),
                ),
                (
                    "assigned_folder",
                    models.ForeignKey(
                        blank=True,
                        help_text="Domain folder to assign upon approval.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="iam.folder",
                    ),
                ),
            ],
            options={
                "verbose_name": "registration request",
                "verbose_name_plural": "registration requests",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="registrationrequest",
            constraint=models.UniqueConstraint(
                condition=models.Q(("status", "pending")),
                fields=("email",),
                name="unique_pending_email",
            ),
        ),
    ]
