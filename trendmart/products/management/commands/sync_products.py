from django.core.management.base import BaseCommand
from products.utils import FakeStoreAPIClient


class Command(BaseCommand):
    help = "Sync products from Fake Store API"

    def handle(self, *args, **options):
        result = FakeStoreAPIClient.sync_data()
        self.stdout.write(self.style.SUCCESS(result))
