from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Category, ProductClick


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "product_count", "created_at"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]

    def product_count(self, obj):
        return obj.product_set.count()

    product_count.short_description = "Products"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "category",
        "price",
        "rating_display",
        "click_count",
        "trending_badge",
        "is_active",
    ]
    list_filter = ["category", "is_active", "created_at"]
    search_fields = ["title", "description"]
    list_editable = ["is_active"]
    ordering = ["-click_count", "-created_at"]

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("title", "description", "price", "category", "is_active")},
        ),
        (
            "External Data",
            {
                "fields": ("external_id", "image_url", "rating_rate", "rating_count"),
                "classes": ["collapse"],
            },
        ),
        (
            "Analytics",
            {"fields": ("click_count", "last_clicked"), "classes": ["collapse"]},
        ),
    )

    readonly_fields = ["click_count", "last_clicked"]

    def rating_display(self, obj):
        return format_html(
            '<span style="color: #f59e0b;">★ {}</span> ({})',
            obj.rating_rate,
            obj.rating_count,
        )

    rating_display.short_description = "Rating"

    def trending_badge(self, obj):
        if obj.click_count > 10:
            return format_html(
                '<span style="background: #ef4444; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px;">🔥 TRENDING</span>'
            )
        elif obj.click_count > 5:
            return format_html(
                '<span style="background: #f59e0b; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px;">📈 POPULAR</span>'
            )
        else:
            return format_html(
                '<span style="background: #6b7280; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px;">🆕 NEW</span>'
            )

    trending_badge.short_description = "Status"


@admin.register(ProductClick)
class ProductClickAdmin(admin.ModelAdmin):
    list_display = ["product", "ip_address", "clicked_at"]
    list_filter = ["clicked_at", "product__category"]
    search_fields = ["product__title", "ip_address"]
    date_hierarchy = "clicked_at"

    def has_add_permission(self, request):
        return False  # Disable manual addition

    def has_change_permission(self, request, obj=None):
        return False  # Disable editing


# Customize admin interface
admin.site.site_header = "TrendMart Admin"
admin.site.site_title = "TrendMart"
admin.site.index_title = "Welcome to TrendMart Administration"
