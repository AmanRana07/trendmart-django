from django import forms
from products.models import Product, Category


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "title",
            "description",
            "price",
            "category",
            "image_url",
            "rating_rate",
            "rating_count",
            "is_active",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                    "placeholder": "Enter product title",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                    "rows": 4,
                    "placeholder": "Enter product description",
                }
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                    "step": "0.01",
                    "placeholder": "0.00",
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                }
            ),
            "image_url": forms.URLInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                    "placeholder": "https://example.com/image.jpg",
                }
            ),
            "rating_rate": forms.NumberInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                    "step": "0.1",
                    "min": "0",
                    "max": "5",
                    "placeholder": "4.5",
                }
            ),
            "rating_count": forms.NumberInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                    "min": "0",
                    "placeholder": "100",
                }
            ),
            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "w-6 h-6 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                }
            ),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "slug"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                    "placeholder": "Enter category name",
                }
            ),
            "slug": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                    "placeholder": "category-slug",
                }
            ),
        }
