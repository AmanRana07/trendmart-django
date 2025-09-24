from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path("login/", views.admin_login, name="admin_login"),
    path("logout/", views.admin_logout, name="admin_logout"),
    path("", views.admin_dashboard, name="admin_dashboard"),
    path("products/", views.products_management, name="admin_products"),
    path("products/add/", views.add_product, name="admin_add_product"),
    path(
        "products/<int:product_id>/edit/", views.edit_product, name="admin_edit_product"
    ),
    path(
        "products/<int:product_id>/delete/",
        views.delete_product,
        name="admin_delete_product",
    ),
    path(
        "products/<int:product_id>/toggle/",
        views.toggle_product_status,
        name="admin_toggle_product",
    ),
    path("categories/", views.categories_management, name="admin_categories"),
    path(
        "categories/<int:category_id>/delete/",
        views.delete_category,
        name="admin_delete_category",
    ),
    path("analytics-data/", views.analytics_data, name="admin_analytics_data"),
]
