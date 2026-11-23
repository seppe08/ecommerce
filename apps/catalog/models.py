from django.conf import settings
from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ("name",)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            "catalog:product_list_by_category", kwargs={"category_slug": self.slug}
        )


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sku = models.CharField(max_length=64, unique=True)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ("-created_at",)
        indexes = (
            models.Index(fields=("slug",)),
            models.Index(fields=("sku",)),
            models.Index(fields=("-created_at",)),
        )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("catalog:product_detail", kwargs={"slug": self.slug})

    @property
    def is_in_stock(self):
        return self.stock > 0

    @property
    def primary_image(self):
        return self.images.filter(is_primary=True).first() or self.images.first()

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if not reviews.exists():
            return 0.0
        return round(sum(r.rating for r in reviews) / reviews.count(), 1)

    @property
    def review_count(self):
        return self.reviews.count()

    def get_rating_distribution(self):
        """Return percentage and count for each rating 1-5."""
        total = self.review_count
        if total == 0:
            return {star: {"count": 0, "pct": 0} for star in range(5, 0, -1)}
        dist = {}
        for star in range(5, 0, -1):
            count = self.reviews.filter(rating=star).count()
            dist[star] = {
                "count": count,
                "pct": round((count / total) * 100),
            }
        return dist


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to="products/")
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"
        ordering = ("-is_primary", "id")

    def __str__(self):
        primary_label = "Primary" if self.is_primary else "Gallery"
        return f"Image for {self.product.name} ({primary_label})"


class Review(models.Model):
    """
    Customer product review with 1-5 star ratings, headline, feedback text,
    and verified buyer validation.
    """

    RATING_CHOICES = (
        (5, "5 Stars — Excellent"),
        (4, "4 Stars — Good"),
        (3, "3 Stars — Average"),
        (2, "2 Stars — Poor"),
        (1, "1 Star — Terrible"),
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        default=5,
    )
    title = models.CharField(max_length=200)
    comment = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product Review"
        verbose_name_plural = "Product Reviews"
        ordering = ("-created_at",)
        unique_together = ("product", "user")

    def __str__(self):
        return f"{self.rating}★ by {self.user.username} on {self.product.name}"


class Wishlist(models.Model):
    """
    Customer saved items / wishlist record linked one-to-one with CustomUser.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist",
    )
    products = models.ManyToManyField(
        Product,
        related_name="wishlists",
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Wishlist"
        verbose_name_plural = "Wishlists"

    def __str__(self):
        return f"{self.user.username}'s Wishlist"
