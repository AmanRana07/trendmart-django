from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    # Core fields
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    # External API fields
    external_id = models.IntegerField(null=True, blank=True)  # For Fake Store API ID
    image_url = models.URLField(max_length=500)
    rating_rate = models.FloatField(default=0.0)
    rating_count = models.IntegerField(default=0)

    # Trending tracking
    click_count = models.IntegerField(default=0)
    last_clicked = models.DateTimeField(null=True, blank=True)

    # Meta
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def click(self):
        """Track product click for trending algorithm"""
        self.click_count += 1
        self.last_clicked = timezone.now()
        self.save()

    @classmethod
    def get_trending(cls, limit=6):
        """Get trending products based on recent clicks"""
        return cls.objects.filter(is_active=True).order_by(
            "-click_count", "-last_clicked"
        )[:limit]


class ProductClick(models.Model):
    """Detailed click tracking for analytics"""

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    clicked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-clicked_at"]
