import requests
from django.conf import settings
from .models import Product, Category
import time
import random


class FakeStoreAPIClient:
    BASE_URL = "https://fakestoreapi.com"

    # Multiple User-Agent options to rotate
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0",
    ]

    @classmethod
    def _get_headers(cls):
        """Get random headers to avoid detection"""
        return {
            "User-Agent": random.choice(cls.USER_AGENTS),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        }

    @classmethod
    def _make_request_with_retry(cls, url, max_retries=5):
        """Make HTTP request with retry logic and different strategies"""

        for attempt in range(max_retries):
            try:
                print(f"🔄 Attempt {attempt + 1}/{max_retries} for {url}")

                # Wait between attempts with exponential backoff
                if attempt > 0:
                    wait_time = (2**attempt) + random.uniform(0, 1)
                    print(f"⏳ Waiting {wait_time:.1f} seconds...")
                    time.sleep(wait_time)

                # Try different approaches for each attempt
                if attempt == 0:
                    # Standard request
                    response = requests.get(url, headers=cls._get_headers(), timeout=30)
                elif attempt == 1:
                    # With session to maintain cookies
                    session = requests.Session()
                    session.headers.update(cls._get_headers())
                    response = session.get(url, timeout=30)
                elif attempt == 2:
                    # Through different endpoint approach
                    response = requests.get(
                        url,
                        headers=cls._get_headers(),
                        timeout=45,
                        allow_redirects=True,
                    )
                elif attempt == 3:
                    # Try with minimal headers
                    simple_headers = {
                        "User-Agent": random.choice(cls.USER_AGENTS),
                        "Accept": "application/json",
                    }
                    response = requests.get(url, headers=simple_headers, timeout=30)
                else:
                    # Last attempt with different approach
                    response = requests.get(
                        url, headers={"User-Agent": "curl/7.68.0"}, timeout=60
                    )

                print(f"📊 Response Status: {response.status_code}")
                print(f"📋 Response Headers: {dict(response.headers)}")

                if response.status_code == 200:
                    print("✅ Request successful!")
                    return response.json()
                elif response.status_code == 403:
                    print(f"❌ 403 Forbidden on attempt {attempt + 1}")
                    print(f"📝 Response text: {response.text[:200]}...")
                    continue
                elif response.status_code == 429:
                    print(f"⏳ Rate limited (429), waiting longer...")
                    time.sleep(10 + attempt * 5)
                    continue
                else:
                    print(f"⚠️  Unexpected status: {response.status_code}")
                    response.raise_for_status()

            except requests.exceptions.Timeout:
                print(f"⏰ Timeout on attempt {attempt + 1}")
                continue
            except requests.exceptions.ConnectionError:
                print(f"🔌 Connection error on attempt {attempt + 1}")
                continue
            except requests.exceptions.RequestException as e:
                print(f"❌ Request error on attempt {attempt + 1}: {e}")
                continue

        # If all attempts failed
        raise Exception(f"Failed to fetch data from {url} after {max_retries} attempts")

    @classmethod
    def fetch_products(cls):
        """Fetch products from Fake Store API with aggressive retry"""
        url = f"{cls.BASE_URL}/products"
        print("🔄 Fetching products from Fake Store API...")
        print(f"🌐 URL: {url}")

        try:
            data = cls._make_request_with_retry(url)
            print(f"✅ Successfully fetched {len(data)} products")
            return data
        except Exception as e:
            print(f"❌ CRITICAL: Could not fetch products: {e}")
            raise Exception(f"API fetch failed: {e}")

    @classmethod
    def fetch_categories(cls):
        """Fetch categories from Fake Store API with aggressive retry"""
        url = f"{cls.BASE_URL}/products/categories"
        print("🔄 Fetching categories from Fake Store API...")
        print(f"🌐 URL: {url}")

        try:
            data = cls._make_request_with_retry(url)
            print(f"✅ Successfully fetched {len(data)} categories")
            return data
        except Exception as e:
            print(f"❌ CRITICAL: Could not fetch categories: {e}")
            raise Exception(f"API fetch failed: {e}")

    @classmethod
    def sync_data(cls):
        """Sync products and categories - MUST succeed from API"""

        print("🚀 Starting API data synchronization...")

        # Fetch categories first (required)
        categories_data = cls.fetch_categories()
        categories_created = 0

        for cat_name in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_name.title(),
                defaults={"slug": cat_name.lower().replace(" ", "-").replace("'", "")},
            )
            if created:
                categories_created += 1
                print(f"✅ Created category: {category.name}")

        # Fetch products (required)
        products_data = cls.fetch_products()
        products_created = 0
        products_updated = 0

        for product_data in products_data:
            try:
                category, _ = Category.objects.get_or_create(
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
                    products_created += 1
                    print(f"Created: {product.title[:50]}...")
                else:
                    products_updated += 1
                    print(f" Updated: {product.title[:50]}...")

            except Exception as e:
                print(f" Error processing product {product_data.get('id')}: {e}")
                continue

        total_products = Product.objects.filter(is_active=True).count()
        total_categories = Category.objects.count()

        result_msg = f"API SYNC SUCCESS: Created {products_created} products, updated {products_updated} products, {categories_created} new categories. Total: {total_products} products, {total_categories} categories"
        print(result_msg)

        return result_msg
