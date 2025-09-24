from django.urls import path
from . import views

urlpatterns = [
    path("products/", views.ProductListView.as_view(), name="product-list"),
    path(
        "products/<int:pk>/", views.ProductDetailView.as_view(), name="product-detail"
    ),
    path(
        "products/<int:product_id>/click/",
        views.track_product_click,
        name="track-click",
    ),
    path("trending/", views.TrendingProductsView.as_view(), name="trending-products"),
    path("categories/", views.CategoryListView.as_view(), name="category-list"),
    path("analytics/", views.product_analytics, name="analytics"),
]
