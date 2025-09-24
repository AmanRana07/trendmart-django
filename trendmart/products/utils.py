import requests
from django.conf import settings
from .models import Product, Category


class FakeStoreAPIClient:
    BASE_URL = "https://fakestoreapi.com"

    @classmethod
    def fetch_products(cls):
        """Fetch products from Fake Store API"""
        try:
            response = requests.get(f"{cls.BASE_URL}/products")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching products: {e}")
            return []

    @classmethod
    def fetch_categories(cls):
        """Fetch categories from Fake Store API"""
        try:
            response = requests.get(f"{cls.BASE_URL}/products/categories")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching categories: {e}")
            return []

    @classmethod
    def sync_data(cls):
        """Sync products and categories with local database"""

        # Sync categories first
        categories_data = cls.fetch_categories()
        for cat_name in categories_data:
            Category.objects.get_or_create(
                name=cat_name.title(),
                defaults={"slug": cat_name.lower().replace(" ", "-")},
            )

        # Sync products
        products_data = cls.fetch_products()
        for product_data in products_data:
            category, created = Category.objects.get_or_create(
                name=product_data["category"].title(),
                defaults={"slug": product_data["category"].lower().replace(" ", "-")},
            )

            Product.objects.update_or_create(
                external_id=product_data["id"],
                defaults={
                    "title": product_data["title"],
                    "description": product_data["description"],
                    "price": product_data["price"],
                    "category": category,
                    "image_url": product_data["image"],
                    "rating_rate": product_data["rating"]["rate"],
                    "rating_count": product_data["rating"]["count"],
                    "is_active": True,
                },
            )

        return f"Synced {len(products_data)} products and {len(categories_data)} categories"
