from django.core.management.base import BaseCommand
from django.db.models import Q

from restaurants.models import Restaurant


class Command(BaseCommand):
    help = "Preview or retire legacy placeholder catalog entries without deleting records."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Mark matching records inactive. The default only previews matches.",
        )

    def handle(self, *args, **options):
        queryset = (
            Restaurant.objects.filter(
                Q(image_url__icontains="picsum.photos")
                | Q(menu_items__name__icontains="demo")
            )
            .distinct()
            .order_by("id")
        )
        count = queryset.count()

        for restaurant in queryset:
            self.stdout.write(f"{restaurant.pk}: {restaurant.name}")

        if not options["apply"]:
            self.stdout.write(
                self.style.WARNING(
                    f"Preview complete: {count} matching records. Re-run with --apply to retire them."
                )
            )
            return

        updated = queryset.filter(is_active=True).update(is_active=False)
        self.stdout.write(
            self.style.SUCCESS(
                f"Retired {updated} legacy catalog records; no records were deleted."
            )
        )