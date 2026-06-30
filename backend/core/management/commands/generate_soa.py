"""
Management command: generate_soa

Generates (or refreshes) a Statement of Applicability from a ComplianceAssessment.
All assessable RequirementAssessments are turned into SoAEntry rows.
Entries inherit the applicability from the requirement result:
  - result == not_applicable  -> applicability = not_applicable
  - everything else           -> applicability = applicable
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


class Command(BaseCommand):
    help = "Generate a Statement of Applicability from a ComplianceAssessment"

    def add_arguments(self, parser):
        parser.add_argument(
            "--compliance-assessment-id",
            type=str,
            required=True,
            help="UUID of the ComplianceAssessment to generate the SoA from",
        )
        parser.add_argument(
            "--name",
            type=str,
            default="Statement of Applicability",
            help="Name for the SoA document (default: 'Statement of Applicability')",
        )
        parser.add_argument(
            "--soa-version",
            dest="version",
            type=str,
            default="1.0",
            help="Version string for the SoA document (default: '1.0')",
        )

    def handle(self, *args, **options):
        # Deferred import so the command is safe during makemigrations
        from core.models import (
            ComplianceAssessment,
            RequirementAssessment,
            StatementOfApplicability,
            SoAEntry,
        )

        ca_id = options["compliance_assessment_id"]

        try:
            ca = ComplianceAssessment.objects.get(id=ca_id)
        except ComplianceAssessment.DoesNotExist:
            raise CommandError(f"ComplianceAssessment '{ca_id}' not found.")

        with transaction.atomic():
            soa, created = StatementOfApplicability.objects.get_or_create(
                compliance_assessment=ca,
                defaults={
                    "name": options["name"],
                    "version": options["version"],
                    "folder": ca.folder,
                },
            )
            if not created:
                self.stdout.write(
                    self.style.WARNING(
                        f"SoA already exists for '{ca.name}'. Updating entries."
                    )
                )

            # Process all assessable requirement assessments
            ras = RequirementAssessment.objects.filter(
                compliance_assessment=ca,
                requirement__assessable=True,
            ).select_related("requirement")

            count = 0
            for ra in ras:
                applicability = (
                    SoAEntry.Applicability.NOT_APPLICABLE
                    if ra.result == RequirementAssessment.Result.NOT_APPLICABLE
                    else SoAEntry.Applicability.APPLICABLE
                )
                SoAEntry.objects.update_or_create(
                    statement=soa,
                    requirement_assessment=ra,
                    defaults={
                        "applicability": applicability,
                        "folder": ca.folder,
                    },
                )
                count += 1

        verb = "Created" if created else "Updated"
        self.stdout.write(
            self.style.SUCCESS(
                f"{verb} SoA '{soa.name}' v{soa.version} "
                f"with {count} entries for assessment '{ca.name}'."
            )
        )
