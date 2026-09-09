"""Deprecated compatibility entry point for the Rivne catalog loader."""

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Deprecated alias for the non-destructive validated Rivne catalog loader."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate and simulate the catalog import without committing changes.",
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.WARNING(
                "seed_db is deprecated; delegating to load_rivne_catalog."
            )
        )
        call_command(
            "load_rivne_catalog",
            dry_run=options["dry_run"],
            stdout=self.stdout,
        )