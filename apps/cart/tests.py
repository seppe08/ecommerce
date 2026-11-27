from decimal import Decimal
from importlib import import_module

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import RequestFactory, TestCase
from django.urls import reverse

from apps.cart.cart import CART_SESSION_ID, Cart
from apps.cart.context_processors import cart as cart_context_processor
from apps.catalog.models import Category, Product

User = get_user_model()


class CartEngineTestCase(TestCase):
    """
    Unit tests for the session-backed Cart engine.
    """

    def setUp(self):
        self.category = Category.objects.create(name="Electronics", slug="electronics")
        self.product1 = Product.objects.create(
            category=self.category,
            name="Smartphone Pro",
            slug="smartphone-pro",
            price=Decimal("799.99"),
            sku="PHONE-001",
            stock=10,
        )
        self.product2 = Product.objects.create(
            category=self.category,
            name="Wireless Earbuds",
            slug="wireless-earbuds",
            price=Decimal("149.50"),
            sku="EAR-001",
            stock=5,
        )
        self.factory = RequestFactory()

    def _get_cart(self, session_data=None):
        request = self.factory.get("/")
        engine = import_module(settings.SESSION_ENGINE)
        session = engine.SessionStore()
        if session_data:
            session.update(session_data)
        request.session = session
        return Cart(request), request

    def test_cart_initialization_empty(self):
        cart, request = self._get_cart()
        self.assertEqual(len(cart), 0)
        self.assertEqual(cart.get_item_count(), 0)
        self.assertEqual(cart.get_total_price(), Decimal(0))
        self.assertIn(CART_SESSION_ID, request.session)

    def test_cart_add_new_product(self):
        cart, _request = self._get_cart()
        cart.add(self.product1, quantity=2)

        self.assertEqual(len(cart), 2)
        self.assertEqual(cart.get_item_count(), 2)
        self.assertEqual(cart.get_total_price(), Decimal("1599.98"))

    def test_cart_add_increment(self):
        cart, _request = self._get_cart()
        cart.add(self.product1, quantity=1)
        cart.add(self.product1, quantity=3)

        self.assertEqual(cart.get_item_count(), 4)
        self.assertEqual(cart.cart[str(self.product1.id)]["quantity"], 4)

    def test_cart_add_override_quantity(self):
        cart, _request = self._get_cart()
        cart.add(self.product1, quantity=5)
        cart.add(self.product1, quantity=2, override_quantity=True)

        self.assertEqual(cart.get_item_count(), 2)
        self.assertEqual(cart.cart[str(self.product1.id)]["quantity"], 2)

    def test_cart_remove_product(self):
        cart, _request = self._get_cart()
        cart.add(self.product1, quantity=2)
        cart.add(self.product2, quantity=1)

        self.assertEqual(cart.get_item_count(), 3)
        cart.remove(self.product1)

        self.assertEqual(cart.get_item_count(), 1)
        self.assertNotIn(str(self.product1.id), cart.cart)
        self.assertIn(str(self.product2.id), cart.cart)

    def test_cart_iteration_yields_item_data(self):
        cart, _request = self._get_cart()
        cart.add(self.product1, quantity=2)
        cart.add(self.product2, quantity=1)

        items = list(iter(cart))
        self.assertEqual(len(items), 2)

        p1_item = next(i for i in items if i["product"] == self.product1)
        self.assertEqual(p1_item["quantity"], 2)
        self.assertEqual(p1_item["price"], Decimal("799.99"))
        self.assertEqual(p1_item["total_price"], Decimal("1599.98"))

    def test_cart_iteration_removes_stale_deleted_products(self):
        cart, _request = self._get_cart()
        cart.add(self.product1, quantity=1)
        # Delete product from DB
        self.product1.delete()

        items = list(iter(cart))
        self.assertEqual(len(items), 0)
        self.assertEqual(len(cart.cart), 0)

    def test_cart_clear(self):
        cart, request = self._get_cart()
        cart.add(self.product1, quantity=2)
        self.assertEqual(cart.get_item_count(), 2)

        cart.clear()
        self.assertEqual(cart.get_item_count(), 0)
        self.assertNotIn(CART_SESSION_ID, request.session)

    def test_cart_context_processor(self):
        request = self.factory.get("/")
        engine = import_module(settings.SESSION_ENGINE)
        request.session = engine.SessionStore()
        ctx = cart_context_processor(request)
        self.assertIn("cart", ctx)
        self.assertIsInstance(ctx["cart"], Cart)


class CartViewsTestCase(TestCase):
    """
    Integration tests for Cart views and HTTP / AJAX interactions.
    """

    def setUp(self):
        self.category = Category.objects.create(name="Accessories", slug="accessories")
        self.product = Product.objects.create(
            category=self.category,
            name="Leather Wallet",
            slug="leather-wallet",
            price=Decimal("49.99"),
            sku="WAL-001",
            stock=5,
        )
        self.out_of_stock_product = Product.objects.create(
            category=self.category,
            name="Vintage Watch",
            slug="vintage-watch",
            price=Decimal("199.99"),
            sku="WATCH-001",
            stock=0,
        )

    def test_cart_detail_view_empty(self):
        response = self.client.get(reverse("cart:cart_detail"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your shopping cart is empty")
        self.assertContains(response, "Explore Catalog")

    def test_cart_add_standard_post(self):
        response = self.client.post(
            reverse("cart:cart_add", kwargs={"product_id": self.product.id}),
            {"quantity": 2},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        session = self.client.session
        self.assertIn(CART_SESSION_ID, session)
        self.assertEqual(session[CART_SESSION_ID][str(self.product.id)]["quantity"], 2)
        # Flash message check
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("added to your cart" in m.message for m in messages))

    def test_cart_add_ajax_post(self):
        response = self.client.post(
            reverse("cart:cart_add", kwargs={"product_id": self.product.id}),
            {"quantity": 1},
            headers={"x-requested-with": "XMLHttpRequest"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["cart_count"], 1)
        self.assertEqual(data["cart_total"], "49.99")

    def test_cart_add_out_of_stock_rejected(self):
        response = self.client.post(
            reverse(
                "cart:cart_add", kwargs={"product_id": self.out_of_stock_product.id}
            ),
            {"quantity": 1},
            headers={"x-requested-with": "XMLHttpRequest"},
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("out of stock", data["message"])

    def test_cart_add_exceeding_stock_clamped(self):
        # Product stock is 5
        response = self.client.post(
            reverse("cart:cart_add", kwargs={"product_id": self.product.id}),
            {"quantity": 10},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        session = self.client.session
        # Clamped to max available stock
        self.assertEqual(session[CART_SESSION_ID][str(self.product.id)]["quantity"], 5)

    def test_cart_update_quantity_increase(self):
        self.client.post(
            reverse("cart:cart_add", kwargs={"product_id": self.product.id}),
            {"quantity": 1},
        )
        response = self.client.post(
            reverse(
                "cart:cart_update_quantity", kwargs={"product_id": self.product.id}
            ),
            {"action": "increase"},
            headers={"x-requested-with": "XMLHttpRequest"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["quantity"], 2)
        self.assertEqual(data["cart_count"], 2)

    def test_cart_update_quantity_decrease(self):
        self.client.post(
            reverse("cart:cart_add", kwargs={"product_id": self.product.id}),
            {"quantity": 3},
        )
        response = self.client.post(
            reverse(
                "cart:cart_update_quantity", kwargs={"product_id": self.product.id}
            ),
            {"action": "decrease"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        session = self.client.session
        self.assertEqual(session[CART_SESSION_ID][str(self.product.id)]["quantity"], 2)

    def test_cart_update_quantity_to_zero_removes_item(self):
        self.client.post(
            reverse("cart:cart_add", kwargs={"product_id": self.product.id}),
            {"quantity": 1},
        )
        response = self.client.post(
            reverse(
                "cart:cart_update_quantity", kwargs={"product_id": self.product.id}
            ),
            {"action": "decrease"},
            headers={"x-requested-with": "XMLHttpRequest"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertTrue(data["removed"])
        self.assertEqual(data["cart_count"], 0)

    def test_cart_remove_view(self):
        self.client.post(
            reverse("cart:cart_add", kwargs={"product_id": self.product.id}),
            {"quantity": 2},
        )
        response = self.client.post(
            reverse("cart:cart_remove", kwargs={"product_id": self.product.id}),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        session = self.client.session
        self.assertNotIn(str(self.product.id), session.get(CART_SESSION_ID, {}))


class CouponIntegrationTestCase(TestCase):
    """
    Tests for Coupon model validation, Cart discount application, and Order linkage.
    """

    def setUp(self):
        from django.utils import timezone

        from apps.orders.models import Coupon

        self.category = Category.objects.create(name="Accessories", slug="accessories")
        self.product = Product.objects.create(
            category=self.category,
            name="Leather Belt",
            slug="leather-belt",
            price=Decimal("50.00"),
            sku="BELT-001",
            stock=20,
        )
        self.coupon_percent = Coupon.objects.create(
            code="SAVE20",
            discount_type=Coupon.DISCOUNT_TYPE_PERCENT,
            discount_value=Decimal("20.00"),
            valid_from=timezone.now() - timezone.timedelta(days=1),
            valid_to=timezone.now() + timezone.timedelta(days=10),
            is_active=True,
        )
        self.coupon_fixed = Coupon.objects.create(
            code="FLAT15",
            discount_type=Coupon.DISCOUNT_TYPE_FIXED,
            discount_value=Decimal("15.00"),
            min_purchase_amount=Decimal("40.00"),
            valid_from=timezone.now() - timezone.timedelta(days=1),
            valid_to=timezone.now() + timezone.timedelta(days=10),
            is_active=True,
        )
        self.coupon_expired = Coupon.objects.create(
            code="EXPIRED",
            discount_type=Coupon.DISCOUNT_TYPE_FIXED,
            discount_value=Decimal("10.00"),
            valid_from=timezone.now() - timezone.timedelta(days=20),
            valid_to=timezone.now() - timezone.timedelta(days=1),
            is_active=True,
        )

    def test_coupon_calculations(self):
        # 20% off 50.00 = 10.00
        discount = self.coupon_percent.calculate_discount(Decimal("50.00"))
        self.assertEqual(discount, Decimal("10.00"))

        # Flat 15.00 off 50.00 = 15.00
        discount_fixed = self.coupon_fixed.calculate_discount(Decimal("50.00"))
        self.assertEqual(discount_fixed, Decimal("15.00"))

    def test_coupon_validations(self):
        valid, _ = self.coupon_percent.is_valid(Decimal("50.00"))
        self.assertTrue(valid)

        # Min spend check
        valid_low, err_low = self.coupon_fixed.is_valid(Decimal("30.00"))
        self.assertFalse(valid_low)
        self.assertIn("Minimum cart subtotal", err_low)

        # Expired check
        valid_exp, err_exp = self.coupon_expired.is_valid(Decimal("50.00"))
        self.assertFalse(valid_exp)
        self.assertIn("expired", err_exp)

    def test_coupon_apply_and_remove_view(self):
        # Add item to cart
        self.client.post(
            reverse("cart:cart_add", kwargs={"product_id": self.product.id}),
            {"quantity": 1},
        )
        # Apply coupon
        response = self.client.post(
            reverse("cart:coupon_apply"),
            {"code": "SAVE20"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "SAVE20")
        self.assertContains(response, "-$10.00")
        self.assertContains(response, "$40.00")

        # Remove coupon
        response_remove = self.client.post(
            reverse("cart:coupon_remove"),
            follow=True,
        )
        self.assertEqual(response_remove.status_code, 200)
        self.assertContains(response_remove, "Coupon discount removed.")
        self.assertContains(response_remove, "$50.00")

    def test_order_creation_attaches_coupon_and_increments_usage(self):
        # Add item to cart and apply coupon
        self.client.post(
            reverse("cart:cart_add", kwargs={"product_id": self.product.id}),
            {"quantity": 2},  # Total 100.00
        )
        self.client.post(reverse("cart:coupon_apply"), {"code": "SAVE20"})

        from apps.orders.models import Order

        checkout_data = {
            "first_name": "Coupon",
            "last_name": "User",
            "email": "coupon@example.com",
            "address": "123 Promo St",
            "city": "Discount City",
            "postal_code": "12345",
            "country": "United States",
            "payment_method": "cod",
        }
        response = self.client.post(reverse("orders:order_create"), checkout_data)
        self.assertEqual(response.status_code, 302)

        order = Order.objects.first()
        self.assertIsNotNone(order)
        self.assertEqual(order.coupon, self.coupon_percent)
        self.assertEqual(order.discount, Decimal("20.00"))
        self.assertEqual(order.get_total_cost(), Decimal("80.00"))

        self.coupon_percent.refresh_from_db()
        self.assertEqual(self.coupon_percent.times_used, 1)

    def test_cart_add_invalid_quantity_returns_error(self):
        response = self.client.post(
            reverse("cart:cart_add", kwargs={"product_id": self.product.id}),
            {"quantity": 0},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])
