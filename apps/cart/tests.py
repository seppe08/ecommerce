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
