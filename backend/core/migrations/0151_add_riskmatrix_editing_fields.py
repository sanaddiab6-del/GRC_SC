# Generated manually to fix RiskMatrix serializer/model mismatch

from django.db import migrations, models
import django.utils.translation


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0150_soa_models"),
    ]

    operations = [
        migrations.AddField(
            model_name="riskmatrix",
            name="editing_draft",
            field=models.JSONField(blank=True, default=None, null=True, verbose_name=django.utils.translation.gettext_lazy("editing draft")),
        ),
        migrations.AddField(
            model_name="riskmatrix",
            name="editing_history",
            field=models.JSONField(blank=True, default=list, null=True, verbose_name=django.utils.translation.gettext_lazy("editing history")),
        ),
        migrations.AddField(
            model_name="riskmatrix",
            name="editing_version",
            field=models.PositiveIntegerField(default=1, verbose_name=django.utils.translation.gettext_lazy("editing version")),
        ),
    ]
