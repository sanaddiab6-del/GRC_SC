from django.core.management.base import BaseCommand, CommandError

from ai_onboarding.model_check import OK, check_ai_model


class Command(BaseCommand):
    help = "Check that Ollama serves the team-standard pinned AI model (warnings only)."

    def add_arguments(self, parser):
        parser.add_argument("--strict", action="store_true",
                            help="Exit with an error when any warning is found.")

    def handle(self, *args, **options):
        results = check_ai_model()
        for result in results:
            style = self.style.SUCCESS if result.level == OK else self.style.WARNING
            self.stdout.write(style(f"[AI model check] {result.level}: {result.message}"))
        if options["strict"] and any(r.level != OK for r in results):
            raise CommandError("AI model check found warnings.")
