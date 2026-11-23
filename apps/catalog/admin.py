from typing import ClassVar

from django.contrib import admin
from django.db.models import Count

from .models import Category, Product, ProductImage, Review, Wishlist


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "alt_text", "is_primary")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "product_count", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "slug", "description")
    prepopulated_fields: ClassVar[dict[str, tuple[str, ...]]] = {"slug": ("name",)}

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(_product_count=Count("products"))

    @admin.display(description="Products", ordering="_product_count")
    def product_count(self, obj):
        return getattr(obj, "_product_count", 0)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "sku",
        "category",
        "price",
        "stock",
        "is_active",
        "featured",
        "created_at",
    )
    list_filter = ("is_active", "featured", "category", "created_at")
    search_fields = ("name", "sku", "description")
    prepopulated_fields: ClassVar[dict[str, tuple[str, ...]]] = {"slug": ("name",)}
    list_editable = ("price", "stock", "is_active", "featured")
    inlines = (ProductImageInline,)
    date_hierarchy = "created_at"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "user",
        "rating",
        "title",
        "is_verified_purchase",
        "created_at",
    )
    list_filter = ("rating", "is_verified_purchase", "created_at")
    search_fields = ("product__name", "user__username", "title", "comment")


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("user", "product_count", "created_at")
    search_fields = ("user__username",)

    def product_count(self, obj):
        return obj.products.count()

    product_count.short_description = "Saved Products"


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "alt_text", "is_primary", "created_at")
    list_filter = ("is_primary", "created_at")
    search_fields = ("product__name", "product__sku", "alt_text")
