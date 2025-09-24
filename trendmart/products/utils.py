import requests
from django.conf import settings
from .models import Product, Category
import time
import random


class FakeStoreAPIClient:
    BASE_URL = "https://fakestoreapi.com"

    # Comprehensive headers to avoid 403 blocks
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Referer": "https://fakestoreapi.com/",
        "Origin": "https://fakestoreapi.com",
    }

    @classmethod
    def _make_request(cls, url, retries=3):
        """Make HTTP request with retry logic and proper error handling"""
        for attempt in range(retries):
            try:
                print(f"🔄 Attempt {attempt + 1}/{retries} - Fetching: {url}")

                # Add random delay to avoid rate limiting
                if attempt > 0:
                    delay = random.uniform(1, 3)
                    print(f"⏱️  Waiting {delay:.1f}s before retry...")
                    time.sleep(delay)

                # Create session with connection pooling
                session = requests.Session()
                session.headers.update(cls.HEADERS)

                response = session.get(
                    url,
                    timeout=60,  # Increased timeout
                    allow_redirects=True,
                    verify=True,  # Verify SSL certificates
                )

                print(f"📊 Response Status: {response.status_code}")
                print(f"📡 Response Headers: {dict(response.headers)}")

                if response.status_code == 200:
                    print(f"✅ Success! Content length: {len(response.content)} bytes")
                    return response.json()

                elif response.status_code == 403:
                    print(f"❌ 403 Forbidden - Attempt {attempt + 1}")
                    print(f"🔍 Response content: {response.text[:500]}")

                    if attempt == retries - 1:
                        print("❌ All attempts failed with 403")
                        raise requests.exceptions.HTTPError(
                            f"403 Forbidden after {retries} attempts"
                        )

                elif response.status_code == 429:
                    print(f"⏳ Rate limited - waiting longer...")
                    time.sleep(5)  # Wait longer for rate limits

                else:
                    response.raise_for_status()

            except requests.exceptions.Timeout:
                print(f"⏱️  Timeout on attempt {attempt + 1}")
                if attempt == retries - 1:
                    raise

            except requests.exceptions.ConnectionError:
                print(f"🔌 Connection error on attempt {attempt + 1}")
                if attempt == retries - 1:
                    raise

            except Exception as e:
                print(f"❌ Error on attempt {attempt + 1}: {str(e)}")
                if attempt == retries - 1:
                    raise

        raise requests.exceptions.RequestException("All retry attempts failed")

    @classmethod
    def fetch_products(cls):
        """Fetch products from Fake Store API with enhanced error handling"""
        try:
            print("🔄 Starting product fetch from Fake Store API...")
            data = cls._make_request(f"{cls.BASE_URL}/products")
            print(f"✅ Successfully fetched {len(data)} products")
            return data
        except Exception as e:
            print(f"❌ Failed to fetch products: {e}")
            raise  # Re-raise to see the actual error

    @classmethod
    def fetch_categories(cls):
        """Fetch categories from Fake Store API with enhanced error handling"""
        try:
            print("🔄 Starting category fetch from Fake Store API...")
            data = cls._make_request(f"{cls.BASE_URL}/products/categories")
            print(f"✅ Successfully fetched {len(data)} categories")
            return data
        except Exception as e:
            print(f"❌ Failed to fetch categories: {e}")
            raise  # Re-raise to see the actual error

    @classmethod
    def sync_data(cls):
        """Sync products and categories with local database"""
        print("🚀 Starting API data sync...")

        try:
            # Sync categories first
            print("📋 Fetching categories...")
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
            print("📦 Fetching products...")
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

            result = f"✅ SUCCESS! Synced {synced_count} new products and {len(categories_data)} categories. Database now has {total_products} total products across {total_categories} categories."
            print(result)
            return result

        except Exception as e:
            error_msg = f"❌ API sync completely failed: {str(e)}"
            print(error_msg)
            raise Exception(error_msg)  # Fail the build if API doesn't work
