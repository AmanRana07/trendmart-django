from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from products.models import Product, Category, ProductClick
from .serializers import (
    ProductSerializer,
    ProductDetailSerializer,
    TrendingProductSerializer,
    CategorySerializer,
)


class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        category = self.request.query_params.get("category", None)

        if category is not None:
            queryset = queryset.filter(category__slug=category)

        return queryset.order_by("-created_at")


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductDetailSerializer


class TrendingProductsView(generics.ListAPIView):
    serializer_class = TrendingProductSerializer

    def get_queryset(self):
        return Product.get_trending(limit=6)


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


@api_view(["POST"])
def track_product_click(request, product_id):
    """Track product click for trending algorithm"""
    product = get_object_or_404(Product, id=product_id, is_active=True)

    # Update product click count
    product.click()

    # Detailed tracking
    ProductClick.objects.create(
        product=product,
        ip_address=request.META.get("REMOTE_ADDR", ""),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
    )

    return Response(
        {"message": "Click tracked successfully", "click_count": product.click_count},
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
def product_analytics(request):
    """Get product analytics data for dashboard"""
    total_products = Product.objects.filter(is_active=True).count()
    total_clicks = sum(Product.objects.values_list("click_count", flat=True))
    trending_products = Product.get_trending(limit=6)

    analytics_data = {
        "total_products": total_products,
        "total_clicks": total_clicks,
        "trending_products": TrendingProductSerializer(
            trending_products, many=True
        ).data,
        "categories": CategorySerializer(Category.objects.all(), many=True).data,
    }

    return Response(analytics_data)
