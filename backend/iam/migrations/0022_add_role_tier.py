"""
Migration 0022 – Add privilege tier to the Role model.

Sets a tier integer on every built-in role so the hierarchy is recorded in
the database and is visible to admin tooling.  Custom (non-builtin) roles
default to tier 5 (Reader) as a conservative starting point.
"""

from django.db import migrations, models

# Tier values mirror ROLE_TIER_MAP in iam/jwt_auth.py
BUILTIN_TIERS: dict[str, int] = {
    "BI-RL-ADM": 1,  # System Administrator
    "BI-RL-DMA": 2,  # Domain Manager
    "BI-RL-ANA": 3,  # Analyst
    "BI-RL-APP": 4,  # Approver
    "BI-RL-AUD": 5,  # Reader
    "BI-RL-ADE": 6,  # Auditee
    "BI-RL-TPR": 7,  # Third-Party Respondent
}


def populate_role_tiers(apps, schema_editor):
    Role = apps.get_model("iam", "Role")
    for role in Role.objects.all():
        role.tier = BUILTIN_TIERS.get(role.name, 5)
        role.save(update_fields=["tier"])


def reverse_populate_role_tiers(apps, schema_editor):
    # No-op: removing the field handles the reverse
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("iam", "0021_fix_auditee_iam_groups"),
    ]

    operations = [
        # 1. Add the column with a sensible default
        migrations.AddField(
            model_name="role",
            name="tier",
            field=models.PositiveSmallIntegerField(
                default=5,
                help_text=(
                    "Privilege tier: 1 = System Administrator (highest), "
                    "7 = Third-Party Respondent (lowest).  "
                    "Lower number → more privileged."
                ),
                verbose_name="privilege tier",
            ),
        ),
        # 2. Back-fill correct tiers for existing rows
        migrations.RunPython(
            populate_role_tiers,
            reverse_code=reverse_populate_role_tiers,
        ),
    ]
