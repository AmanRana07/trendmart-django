from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Product, Category


def home(request):
    """Landing page with trending products"""
    trending_products = Product.get_trending(limit=6)
    recent_products = Product.objects.filter(is_active=True)[:8]
    categories = Category.objects.all()

    context = {
        "trending_products": trending_products,
        "recent_products": recent_products,
        "categories": categories,
    }
    return render(request, "products/home.html", context)


def product_detail(request, product_id):
    """Product detail page"""
    product = get_object_or_404(Product, id=product_id, is_active=True)

    # Track click
    product.click()

    related_products = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=product.id)[:4]

    context = {"product": product, "related_products": related_products}
    return render(request, "products/detail.html", context)


def products_list(request):
    """Products listing with pagination"""
    category = request.GET.get("category")
    products = Product.objects.filter(is_active=True)

    if category:
        products = products.filter(category__slug=category)

    context = {
        "products": products,
        "categories": Category.objects.all(),
        "selected_category": category,
    }
    return render(request, "products/list.html", context)
