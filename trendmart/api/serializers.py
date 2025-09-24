from rest_framework import serializers
from products.models import Product, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "description",
            "price",
            "category",
            "category_name",
            "image_url",
            "rating_rate",
            "rating_count",
            "click_count",
            "is_active",
            "created_at",
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = "__all__"


class TrendingProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "price",
            "image_url",
            "rating_rate",
            "click_count",
            "category_name",
        ]
