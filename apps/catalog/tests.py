import tempfile
from decimal import Decimal

from django.contrib.admin.sites import AdminSite
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from PIL import Image

from apps.catalog.admin import (
    CategoryAdmin,
    ProductAdmin,
    ProductImageAdmin,
    ProductImageInline,
)
from apps.catalog.models import Category, Product, ProductImage


def create_test_image():
    """Generate a valid 1x1 test image in memory."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        img = Image.new("RGB", (10, 10), color="blue")
        img.save(f, format="PNG")
        f.seek(0)
        return SimpleUploadedFile(
            name="test_img.png",
            content=f.read(),
            content_type="image/png",
        )


class CategoryModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Electronics",
            slug="electronics",
            description="Gadgets and devices",
            is_active=True,
        )

    def test_category_creation_and_str(self):
        self.assertEqual(str(self.category), "Electronics")
        self.assertTrue(self.category.is_active)
        self.assertEqual(self.category.slug, "electronics")

    def test_category_absolute_url(self):
        expected_url = reverse(
            "catalog:product_list_by_category", kwargs={"category_slug": "electronics"}
        )
        self.assertEqual(self.category.get_absolute_url(), expected_url)

    def test_category_slug_and_name_uniqueness(self):
        with transaction.atomic(), self.assertRaises(IntegrityError):
            Category.objects.create(name="Electronics", slug="electronics-2")
        with transaction.atomic(), self.assertRaises(IntegrityError):
            Category.objects.create(name="Other", slug="electronics")


class ProductModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Audio",
            slug="audio",
            description="Headphones and speakers",
        )
        self.product = Product.objects.create(
            category=self.category,
            name="Wireless Headphones",
            slug="wireless-headphones",
            description="Premium noise-cancelling headphones",
            price=Decimal("199.99"),
            sku="AURA-AUDIO-001",
            stock=15,
            is_active=True,
            featured=True,
        )

    def test_product_creation_and_str(self):
        self.assertEqual(str(self.product), "Wireless Headphones")
        self.assertEqual(self.product.price, Decimal("199.99"))
        self.assertEqual(self.product.sku, "AURA-AUDIO-001")
        self.assertTrue(self.product.is_active)
        self.assertTrue(self.product.featured)
        self.assertIsNotNone(self.product.created_at)
        self.assertIsNotNone(self.product.updated_at)

    def test_product_absolute_url(self):
        expected_url = reverse(
            "catalog:product_detail", kwargs={"slug": "wireless-headphones"}
        )
        self.assertEqual(self.product.get_absolute_url(), expected_url)

    def test_product_is_in_stock_property(self):
        self.assertTrue(self.product.is_in_stock)
        self.product.stock = 0
        self.product.save()
        self.assertFalse(self.product.is_in_stock)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_product_primary_image_property(self):
        # When no images exist
        self.assertIsNone(self.product.primary_image)

        # Add gallery image (is_primary=False)
        img1 = ProductImage.objects.create(
            product=self.product,
            image=create_test_image(),
            alt_text="Gallery view",
            is_primary=False,
        )
        self.assertEqual(self.product.primary_image, img1)

        # Add primary image (is_primary=True)
        img2 = ProductImage.objects.create(
            product=self.product,
            image=create_test_image(),
            alt_text="Front view",
            is_primary=True,
        )
        # Should now return img2
        self.assertEqual(self.product.primary_image, img2)

    def test_product_sku_and_slug_uniqueness(self):
        with transaction.atomic(), self.assertRaises(IntegrityError):
            Product.objects.create(
                category=self.category,
                name="Other Headphones",
                slug="wireless-headphones",
                price=Decimal("49.99"),
                sku="UNIQUE-SKU-001",
            )
        with transaction.atomic(), self.assertRaises(IntegrityError):
            Product.objects.create(
                category=self.category,
                name="Different Product",
                slug="different-product",
                price=Decimal("49.99"),
                sku="AURA-AUDIO-001",
            )


class ProductImageModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Wearables", slug="wearables")
        self.product = Product.objects.create(
            category=self.category,
            name="Smart Watch",
            slug="smart-watch",
            price=Decimal("299.00"),
            sku="AURA-WATCH-001",
        )

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_image_creation_and_str(self):
        img_primary = ProductImage.objects.create(
            product=self.product,
            image=create_test_image(),
            alt_text="Smart watch front",
            is_primary=True,
        )
        img_gallery = ProductImage.objects.create(
            product=self.product,
            image=create_test_image(),
            alt_text="Smart watch angle",
            is_primary=False,
        )

        self.assertIn("Primary", str(img_primary))
        self.assertIn("Gallery", str(img_gallery))
        self.assertEqual(img_primary.alt_text, "Smart watch front")

        # Check ordering: primary should come first
        images = list(self.product.images.all())
        self.assertEqual(images[0], img_primary)
        self.assertEqual(images[1], img_gallery)


class CatalogAdminTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.category_admin = CategoryAdmin(Category, self.site)
        self.product_admin = ProductAdmin(Product, self.site)
        self.image_admin = ProductImageAdmin(ProductImage, self.site)

        self.category = Category.objects.create(name="Computers", slug="computers")
        self.product = Product.objects.create(
            category=self.category,
            name="Laptop Pro",
            slug="laptop-pro",
            price=Decimal("1299.99"),
            sku="AURA-LAPTOP-001",
            stock=8,
        )

    def test_category_admin_configuration(self):
        self.assertIn("name", self.category_admin.list_display)
        self.assertIn("slug", self.category_admin.list_display)
        self.assertIn("is_active", self.category_admin.list_filter)
        self.assertIn("name", self.category_admin.search_fields)

        # Test product_count display method
        request = None
        qs = self.category_admin.get_queryset(request)
        cat_obj = qs.get(pk=self.category.pk)
        self.assertEqual(self.category_admin.product_count(cat_obj), 1)

    def test_product_admin_configuration(self):
        self.assertIn("name", self.product_admin.list_display)
        self.assertIn("sku", self.product_admin.list_display)
        self.assertIn("price", self.product_admin.list_editable)
        self.assertIn("is_active", self.product_admin.list_filter)
        self.assertIn("name", self.product_admin.search_fields)
        self.assertIn(ProductImageInline, self.product_admin.inlines)

    def test_image_admin_configuration(self):
        self.assertIn("product", self.image_admin.list_display)
        self.assertIn("is_primary", self.image_admin.list_filter)


class ProductListViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.cat_electronics = Category.objects.create(
            name="Electronics",
            slug="electronics",
            description="Electronic devices",
        )
        self.cat_books = Category.objects.create(
            name="Books",
            slug="books",
            description="Printed and digital books",
        )

        self.p1 = Product.objects.create(
            category=self.cat_electronics,
            name="Alpha Phone",
            slug="alpha-phone",
            description="High performance flagship smartphone",
            price=Decimal("899.00"),
            sku="SKU-PHONE-01",
            stock=10,
            is_active=True,
            featured=True,
        )
        self.p2 = Product.objects.create(
            category=self.cat_electronics,
            name="Beta Tablet",
            slug="beta-tablet",
            description="Lightweight 10-inch productivity tablet",
            price=Decimal("499.00"),
            sku="SKU-TAB-02",
            stock=5,
            is_active=True,
            featured=False,
        )
        self.p3 = Product.objects.create(
            category=self.cat_books,
            name="Python Mastery Guide",
            slug="python-mastery-guide",
            description="Comprehensive guide to modern Python",
            price=Decimal("49.99"),
            sku="SKU-BOOK-03",
            stock=20,
            is_active=True,
            featured=False,
        )
        self.inactive_product = Product.objects.create(
            category=self.cat_electronics,
            name="Discontinued Drone",
            slug="discontinued-drone",
            description="Old drone model",
            price=Decimal("299.00"),
            sku="SKU-OLD-04",
            stock=0,
            is_active=False,
        )

    def test_product_list_status_and_template(self):
        response = self.client.get(reverse("catalog:product_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/product_list.html")
        products = list(response.context["products"])
        self.assertIn(self.p1, products)
        self.assertIn(self.p2, products)
        self.assertIn(self.p3, products)
        self.assertNotIn(self.inactive_product, products)

    def test_product_list_category_slug_url_filter(self):
        url = reverse(
            "catalog:product_list_by_category", kwargs={"category_slug": "electronics"}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        products = list(response.context["products"])
        self.assertIn(self.p1, products)
        self.assertIn(self.p2, products)
        self.assertNotIn(self.p3, products)
        self.assertEqual(response.context["current_category"], self.cat_electronics)

    def test_product_list_category_get_parameter_filter(self):
        response = self.client.get(
            reverse("catalog:product_list"), {"category": "books"}
        )
        self.assertEqual(response.status_code, 200)
        products = list(response.context["products"])
        self.assertIn(self.p3, products)
        self.assertNotIn(self.p1, products)
        self.assertEqual(response.context["current_category"], self.cat_books)

    def test_product_list_invalid_category_returns_404(self):
        url = reverse(
            "catalog:product_list_by_category",
            kwargs={"category_slug": "non-existent-category"},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_product_list_keyword_search(self):
        # Search by name keyword
        response = self.client.get(reverse("catalog:product_list"), {"q": "Tablet"})
        self.assertEqual(response.status_code, 200)
        products = list(response.context["products"])
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0], self.p2)

        # Search by description keyword
        response = self.client.get(reverse("catalog:product_list"), {"q": "flagship"})
        self.assertEqual(response.status_code, 200)
        products = list(response.context["products"])
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0], self.p1)

        # Search by SKU
        response = self.client.get(
            reverse("catalog:product_list"), {"q": "SKU-BOOK-03"}
        )
        self.assertEqual(response.status_code, 200)
        products = list(response.context["products"])
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0], self.p3)

    def test_product_list_featured_filter(self):
        response = self.client.get(reverse("catalog:product_list"), {"featured": "1"})
        self.assertEqual(response.status_code, 200)
        products = list(response.context["products"])
        self.assertEqual(products, [self.p1])

    def test_product_list_sorting(self):
        # Price ascending
        response = self.client.get(
            reverse("catalog:product_list"), {"sort": "price_asc"}
        )
        products = list(response.context["products"])
        self.assertEqual(products, [self.p3, self.p2, self.p1])

        # Price descending
        response = self.client.get(
            reverse("catalog:product_list"), {"sort": "price_desc"}
        )
        products = list(response.context["products"])
        self.assertEqual(products, [self.p1, self.p2, self.p3])

        # Name alphabetical
        response = self.client.get(reverse("catalog:product_list"), {"sort": "name"})
        products = list(response.context["products"])
        self.assertEqual(products, [self.p1, self.p2, self.p3])

    def test_product_list_pagination(self):
        # Create 15 products to trigger pagination (paginate_by = 12)
        for i in range(15):
            Product.objects.create(
                category=self.cat_books,
                name=f"Extra Book {i}",
                slug=f"extra-book-{i}",
                price=Decimal("19.99"),
                sku=f"SKU-EXTRA-{i}",
                stock=5,
                is_active=True,
            )

        response = self.client.get(reverse("catalog:product_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["products"]), 12)

        # Page 2
        response_page2 = self.client.get(reverse("catalog:product_list"), {"page": 2})
        self.assertEqual(response_page2.status_code, 200)
        # Total active = 3 initial + 15 extra = 18. Page 1: 12, Page 2: 6.
        self.assertEqual(len(response_page2.context["products"]), 6)


class ProductDetailViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="Audio", slug="audio")
        self.product = Product.objects.create(
            category=self.category,
            name="Noise Cancelling Headphones",
            slug="noise-cancelling-headphones",
            description="Deep bass and active noise cancellation",
            price=Decimal("249.99"),
            sku="AURA-NC-001",
            stock=12,
            is_active=True,
        )
        self.related_product = Product.objects.create(
            category=self.category,
            name="In-Ear Earbuds",
            slug="in-ear-earbuds",
            description="Compact wireless earbuds",
            price=Decimal("129.99"),
            sku="AURA-EARBUD-002",
            stock=25,
            is_active=True,
        )
        self.inactive_product = Product.objects.create(
            category=self.category,
            name="Old Speaker",
            slug="old-speaker",
            price=Decimal("50.00"),
            sku="AURA-SPEAKER-OLD",
            is_active=False,
        )

    def test_product_detail_success(self):
        url = reverse(
            "catalog:product_detail", kwargs={"slug": "noise-cancelling-headphones"}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/product_detail.html")
        self.assertEqual(response.context["product"], self.product)
        self.assertIn(self.related_product, response.context["related_products"])
        self.assertNotIn(self.product, response.context["related_products"])

    def test_product_detail_inactive_returns_404(self):
        url = reverse("catalog:product_detail", kwargs={"slug": "old-speaker"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_product_detail_nonexistent_slug_returns_404(self):
        url = reverse("catalog:product_detail", kwargs={"slug": "does-not-exist"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class ReviewAndRatingTestCase(TestCase):
    """
    Tests for Review model, ratings calculation, verification, and submission views.
    """

    def setUp(self):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        self.user1 = User.objects.create_user(
            username="reviewer1",
            email="rev1@example.com",
            password="Password123!",
        )
        self.user2 = User.objects.create_user(
            username="reviewer2",
            email="rev2@example.com",
            password="Password123!",
        )
        self.category = Category.objects.create(name="Watches", slug="watches")
        self.product = Product.objects.create(
            category=self.category,
            name="Chronograph Watch",
            slug="chronograph-watch",
            price=Decimal("350.00"),
            sku="WATCH-001",
            stock=10,
        )

    def test_review_ratings_and_aggregates(self):
        from apps.catalog.models import Review

        self.assertEqual(self.product.average_rating, 0.0)
        self.assertEqual(self.product.review_count, 0)

        Review.objects.create(
            product=self.product,
            user=self.user1,
            rating=5,
            title="Superb craftsmanship",
            comment="Exceeded all my expectations.",
        )
        Review.objects.create(
            product=self.product,
            user=self.user2,
            rating=4,
            title="Very good watch",
            comment="Comfortable strap and accurate timing.",
        )

        self.assertEqual(self.product.review_count, 2)
        self.assertEqual(self.product.average_rating, 4.5)
        dist = self.product.get_rating_distribution()
        self.assertEqual(dist[5]["count"], 1)
        self.assertEqual(dist[4]["count"], 1)
        self.assertEqual(dist[3]["count"], 0)

        with self.assertNumQueries(1):
            dist_optimized = self.product.get_rating_distribution()
        self.assertEqual(dist_optimized[5]["count"], 1)

    def test_add_review_authenticated(self):
        self.client.force_login(self.user1)
        review_data = {
            "rating": "5",
            "title": "Incredible design",
            "comment": "Looks even better in person than the photos.",
        }
        response = self.client.post(
            reverse("catalog:add_review", kwargs={"slug": self.product.slug}),
            review_data,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        from apps.catalog.models import Review

        rev = Review.objects.get(product=self.product, user=self.user1)
        self.assertEqual(rev.rating, 5)
        self.assertEqual(rev.title, "Incredible design")
        self.assertContains(response, "Incredible design")

    def test_add_review_unauthenticated_redirects(self):
        response = self.client.post(
            reverse("catalog:add_review", kwargs={"slug": self.product.slug}),
            {"rating": "5", "title": "Test", "comment": "Test"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)


class WishlistTestCase(TestCase):
    """
    Tests for Wishlist model and customer toggle/listing views.
    """

    def setUp(self):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        self.user = User.objects.create_user(
            username="wishlistuser",
            email="wishlist@example.com",
            password="Password123!",
        )
        self.category = Category.objects.create(name="Living", slug="living")
        self.product = Product.objects.create(
            category=self.category,
            name="Ceramic Vase",
            slug="ceramic-vase",
            price=Decimal("45.00"),
            sku="VASE-001",
            stock=15,
        )

    def test_wishlist_toggle_adds_and_removes(self):
        self.client.force_login(self.user)
        # 1. First toggle: add
        response_add = self.client.post(
            reverse("catalog:wishlist_toggle", kwargs={"product_id": self.product.id}),
            headers={"x-requested-with": "XMLHttpRequest"},
        )
        self.assertEqual(response_add.status_code, 200)
        data_add = response_add.json()
        self.assertTrue(data_add["success"])
        self.assertTrue(data_add["in_wishlist"])
        self.assertEqual(data_add["wishlist_count"], 1)

        from apps.catalog.models import Wishlist

        wishlist = Wishlist.objects.get(user=self.user)
        self.assertIn(self.product, wishlist.products.all())

        # 2. Second toggle: remove
        response_remove = self.client.post(
            reverse("catalog:wishlist_toggle", kwargs={"product_id": self.product.id}),
            headers={"x-requested-with": "XMLHttpRequest"},
        )
        self.assertEqual(response_remove.status_code, 200)
        data_remove = response_remove.json()
        self.assertFalse(data_remove["in_wishlist"])
        self.assertEqual(data_remove["wishlist_count"], 0)
        self.assertNotIn(self.product, wishlist.products.all())

    def test_wishlist_detail_view(self):
        self.client.force_login(self.user)
        from apps.catalog.models import Wishlist

        wishlist = Wishlist.objects.create(user=self.user)
        wishlist.products.add(self.product)

        response = self.client.get(reverse("catalog:wishlist_detail"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ceramic Vase")
        self.assertContains(response, "$45.00")

    def test_wishlist_unauthenticated_redirects(self):
        response = self.client.get(reverse("catalog:wishlist_detail"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)
