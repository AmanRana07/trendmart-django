from django.db.models import Sum, Count, Avg
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from products.models import Product, Category, ProductClick
from .forms import ProductForm, CategoryForm
import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.shortcuts import render, redirect


def admin_login(request):
    """Custom admin login page"""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("admin_dashboard")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_staff:
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.username}!")

                    # Redirect to next page or dashboard
                    next_page = request.GET.get("next")
                    if next_page:
                        return redirect(next_page)
                    return redirect("admin_dashboard")
                else:
                    messages.error(request, "You do not have admin privileges.")
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, "custom_admin/login.html", {"form": form})


def admin_logout(request):
    """Custom admin logout"""
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        messages.success(
            request, f"Goodbye, {username}! You have been logged out successfully."
        )

    return redirect("home")


def is_staff_user(user):
    return user.is_authenticated and user.is_staff


@user_passes_test(is_staff_user)
def admin_dashboard(request):
    """Main admin dashboard with REAL analytics"""
    # Basic counts
    total_products = Product.objects.filter(is_active=True).count()
    total_categories = Category.objects.count()

    # REAL click count calculation
    total_clicks = (
        Product.objects.filter(is_active=True).aggregate(total=Sum("click_count"))[
            "total"
        ]
        or 0
    )

    # Get trending and recent products
    trending_products = Product.objects.filter(is_active=True).order_by("-click_count")[
        :5
    ]
    recent_products = Product.objects.filter(is_active=True).order_by("-created_at")[:5]

    # Calculate average rating
    avg_rating = (
        Product.objects.filter(is_active=True).aggregate(avg=Avg("rating_rate"))["avg"]
        or 0
    )

    # Analytics data for charts
    category_data = []
    for category in Category.objects.all():
        product_count = category.product_set.filter(is_active=True).count()
        category_clicks = (
            category.product_set.filter(is_active=True).aggregate(
                total=Sum("click_count")
            )["total"]
            or 0
        )

        category_data.append(
            {"name": category.name, "count": product_count, "clicks": category_clicks}
        )

    # Recent click activity (last 7 days)
    from datetime import datetime, timedelta

    week_ago = datetime.now() - timedelta(days=7)
    recent_clicks = ProductClick.objects.filter(clicked_at__gte=week_ago).count()

    # Top clicked products for chart
    top_clicked = Product.objects.filter(is_active=True, click_count__gt=0).order_by(
        "-click_count"
    )[:10]

    click_analytics = []
    for product in top_clicked:
        click_analytics.append(
            {
                "title": product.title[:20]
                + ("..." if len(product.title) > 20 else ""),
                "clicks": product.click_count,
            }
        )

    context = {
        "total_products": total_products,
        "total_categories": total_categories,
        "total_clicks": total_clicks,  # REAL click count
        "avg_rating": round(avg_rating, 1),
        "recent_clicks_week": recent_clicks,
        "trending_products": trending_products,
        "recent_products": recent_products,
        "category_data": json.dumps(category_data),
        "click_analytics": json.dumps(click_analytics),
    }
    return render(request, "custom_admin/dashboard.html", context)


@user_passes_test(is_staff_user, login_url='admin_login')
def products_management(request):
    """Products management page with pagination and search"""
    products = Product.objects.all().order_by("-created_at")

    # Search functionality
    search = request.GET.get("search")
    if search:
        products = products.filter(title__icontains=search)

    # Filter by category
    category_filter = request.GET.get("category")
    if category_filter:
        products = products.filter(category_id=category_filter)

    # Pagination
    paginator = Paginator(products, 10)
    page_number = request.GET.get("page")
    products_page = paginator.get_page(page_number)

    categories = Category.objects.all()

    context = {
        "products": products_page,
        "categories": categories,
        "search": search,
        "category_filter": category_filter,
    }
    return render(request, "custom_admin/products_management.html", context)


@user_passes_test(is_staff_user, login_url='admin_login')
def add_product(request):
    """Add new product"""
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.title}" added successfully!')
            return redirect("admin_products")
    else:
        form = ProductForm()

    return render(request, "custom_admin/add_product.html", {"form": form})


@user_passes_test(is_staff_user, login_url='admin_login')
def edit_product(request, product_id):
    """Edit existing product"""
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            product = form.save()
            messages.success(
                request, f'Product "{product.title}" updated successfully!'
            )
            return redirect("admin_products")
    else:
        form = ProductForm(instance=product)

    return render(
        request, "custom_admin/edit_product.html", {"form": form, "product": product}
    )


@user_passes_test(is_staff_user, login_url='admin_login')
def delete_product(request, product_id):
    """Delete product"""
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        product_title = product.title
        product.delete()
        messages.success(request, f'Product "{product_title}" deleted successfully!')
        return redirect("admin_products")

    return render(request, "custom_admin/delete_product.html", {"product": product})


@user_passes_test(is_staff_user, login_url='admin_login')
def categories_management(request):
    """Categories management page"""
    categories = Category.objects.all().order_by("name")

    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" added successfully!')
            return redirect("admin_categories")
    else:
        form = CategoryForm()

    context = {"categories": categories, "form": form}
    return render(request, "custom_admin/categories_management.html", context)


@user_passes_test(is_staff_user, login_url='admin_login')
def delete_category(request, category_id):
    """Delete category"""
    category = get_object_or_404(Category, id=category_id)

    if request.method == "POST":
        category_name = category.name
        category.delete()
        messages.success(request, f'Category "{category_name}" deleted successfully!')
        return redirect("admin_categories")

    return render(request, "custom_admin/delete_category.html", {"category": category})


@user_passes_test(is_staff_user, login_url='admin_login')
def toggle_product_status(request, product_id):
    """Toggle product active status via AJAX"""
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)
        product.is_active = not product.is_active
        product.save()

        return JsonResponse(
            {
                "success": True,
                "is_active": product.is_active,
                "message": f'Product {"activated" if product.is_active else "deactivated"} successfully!',
            }
        )

    return JsonResponse({"success": False})


@user_passes_test(is_staff_user, login_url='admin_login')
def analytics_data(request):
    """Return analytics data as JSON for charts"""
    # Products by category
    category_data = []
    for category in Category.objects.all():
        category_data.append(
            {
                "name": category.name,
                "count": category.product_set.filter(is_active=True).count(),
            }
        )

    # Click analytics
    click_data = Product.objects.filter(is_active=True).order_by("-click_count")[:10]
    click_analytics = [
        {"title": p.title[:20] + "...", "clicks": p.click_count} for p in click_data
    ]

    return JsonResponse(
        {"category_data": category_data, "click_analytics": click_analytics}
    )
