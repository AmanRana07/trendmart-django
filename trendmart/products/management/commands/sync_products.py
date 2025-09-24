from django.core.management.base import BaseCommand
from products.utils import FakeStoreAPIClient  # Use proxy version


class Command(BaseCommand):
    help = "Sync products from external API via proxy"

    def handle(self, *args, **options):
        try:
            result = FakeStoreAPIClient.sync_data()
            self.stdout.write(self.style.SUCCESS(result))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Sync failed: {e}"))
            # Don't exit with error - let deployment continue
            self.stdout.write(self.style.WARNING("Continuing with existing data..."))
