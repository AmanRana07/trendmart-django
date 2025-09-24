import requests
from django.conf import settings
from .models import Product, Category
import json


class FakeStoreAPIClient:
    BASE_URL = "https://fakestoreapi.com"

    # Use free proxy services that work with APIs
    PROXIES = [
        "https://api.codetabs.com/v1/proxy/?quest=",  # Free proxy API
        "https://api.allorigins.win/get?url=",  # Another free proxy
        "https://corsproxy.io/?",  # CORS proxy
    ]

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json",
        "Referer": "https://github.com/",  # Make it look like GitHub request
    }

    @classmethod
    def _fetch_via_proxy(cls, url):
        """Fetch URL using proxy services"""
        for proxy_base in cls.PROXIES:
            try:
                proxy_url = f"{proxy_base}{url}"
                print(f"🔄 Trying proxy: {proxy_base}")

                response = requests.get(proxy_url, headers=cls.HEADERS, timeout=30)

                print(f"📊 Proxy response: {response.status_code}")

                if response.status_code == 200:
                    # Handle different proxy response formats
                    if "codetabs.com" in proxy_base:
                        return response.json()
                    elif "allorigins.win" in proxy_base:
                        data = response.json()
                        return json.loads(data["contents"])
                    else:
                        return response.json()

            except Exception as e:
                print(f"❌ Proxy {proxy_base} failed: {e}")
                continue

        raise Exception("All proxy services failed")

    @classmethod
    def fetch_products(cls):
        """Fetch products via proxy services"""
        try:
            print("🔄 Fetching products via proxy...")
            url = f"{cls.BASE_URL}/products"
            data = cls._fetch_via_proxy(url)
            print(f"✅ Successfully fetched {len(data)} products via proxy")
            return data
        except Exception as e:
            print(f"❌ Proxy fetch failed: {e}")
            raise

    @classmethod
    def fetch_categories(cls):
        """Fetch categories via proxy services"""
        try:
            print("🔄 Fetching categories via proxy...")
            url = f"{cls.BASE_URL}/products/categories"
            data = cls._fetch_via_proxy(url)
            print(f"✅ Successfully fetched {len(data)} categories via proxy")
            return data
        except Exception as e:
            print(f"❌ Proxy fetch failed: {e}")
            raise

    @classmethod
    def sync_data(cls):
        """Sync products and categories with local database"""
        print("🚀 Starting proxy-based API sync...")

        try:
            # Sync categories first
            categories_data = cls.fetch_categories()
            print(f"📋 Processing {len(categories_data)} categories...")

            for cat_name in categories_data:
                category, created = Category.objects.get_or_create(
                    name=cat_name.title(),
                    defaults={
                        "slug": cat_name.lower().replace(" ", "-").replace("'", "")
                    },
                )
                if created:
                    print(f"✅ Created category: {category.name}")

            # Sync products
            products_data = cls.fetch_products()
            print(f"📦 Processing {len(products_data)} products...")

            synced_count = 0
            for product_data in products_data:
                try:
                    category, created = Category.objects.get_or_create(
                        name=product_data["category"].title(),
                        defaults={
                            "slug": product_data["category"]
                            .lower()
                            .replace(" ", "-")
                            .replace("'", "")
                        },
                    )

                    product, created = Product.objects.update_or_create(
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

                    if created:
                        synced_count += 1
                        print(f"✅ Created: {product.title[:50]}...")
                    else:
                        print(f"🔄 Updated: {product.title[:50]}...")

                except Exception as e:
                    print(f"❌ Error syncing product {product_data.get('id')}: {e}")
                    continue

            total_products = Product.objects.filter(is_active=True).count()
            total_categories = Category.objects.count()

            result = f"✅ SUCCESS! Synced {synced_count} new products and {len(categories_data)} categories via proxy. Database: {total_products} products, {total_categories} categories."
            print(result)
            return result

        except Exception as e:
            error_msg = f"❌ Proxy API sync failed: {str(e)}"
            print(error_msg)
            raise Exception(error_msg)
