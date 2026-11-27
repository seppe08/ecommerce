from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.cart.cart import CART_SESSION_ID
from apps.catalog.models import Category, Product
from apps.orders.admin import OrderAdmin
from apps.orders.models import Order, OrderItem

User = get_user_model()


class OrdersModelTestCase(TestCase):
    """
    Unit tests for Order and OrderItem models.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="testshopper",
            email="shopper@example.com",
            password="Password123!",
            first_name="Alice",
            last_name="Smith",
        )
        self.category = Category.objects.create(name="Footwear", slug="footwear")
        self.product = Product.objects.create(
            category=self.category,
            name="Running Shoes",
            slug="running-shoes",
            price=Decimal("120.00"),
            sku="SHOE-001",
            stock=15,
        )

    def test_order_creation_and_auto_order_number(self):
        order = Order.objects.create(
            user=self.user,
            first_name="Alice",
            last_name="Smith",
            email="shopper@example.com",
            address="123 Running Lane",
            city="Boston",
            postal_code="02101",
            country="United States",
        )
        self.assertTrue(order.order_number.startswith("ORD-"))
        self.assertEqual(order.status, Order.STATUS_PENDING)
        self.assertFalse(order.paid)
        self.assertEqual(order.full_name, "Alice Smith")
        self.assertEqual(str(order), f"Order #{order.order_number}")

    def test_order_item_cost_and_order_total(self):
        order = Order.objects.create(
            user=self.user,
            first_name="Alice",
            last_name="Smith",
            email="shopper@example.com",
            address="123 Running Lane",
            city="Boston",
            postal_code="02101",
            country="United States",
        )
        item1 = OrderItem.objects.create(
            order=order,
            product=self.product,
            price=Decimal("120.00"),
            quantity=2,
        )
        self.assertEqual(item1.get_cost(), Decimal("240.00"))
        self.assertEqual(order.get_total_cost(), Decimal("240.00"))


class OrdersViewsTestCase(TestCase):
    """
    Integration tests for Checkout, Order Confirmation, Order List, and Invoice views.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="johndoe",
            email="john@example.com",
            password="SecurePassword123!",
            first_name="John",
            last_name="Doe",
            phone="+1 555-123-4567",
        )
        self.other_user = User.objects.create_user(
            username="janedoe",
            email="jane@example.com",
            password="SecurePassword123!",
            first_name="Jane",
            last_name="Doe",
        )
        self.category = Category.objects.create(name="Gadgets", slug="gadgets")
        self.product = Product.objects.create(
            category=self.category,
            name="Noise Cancelling Headphones",
            slug="headphones",
            price=Decimal("250.00"),
            sku="HP-001",
            stock=10,
        )

    def _fill_cart(self, product, quantity=2):
        session = self.client.session
        session[CART_SESSION_ID] = {
            str(product.id): {
                "quantity": quantity,
                "price": str(product.price),
            }
        }
        session.save()

    def test_order_create_empty_cart_redirects(self):
        response = self.client.get(reverse("orders:order_create"))
        self.assertRedirects(response, reverse("cart:cart_detail"))

    def test_order_create_get_prepopulates_user_data(self):
        self._fill_cart(self.product, 1)
        self.client.login(username="johndoe", password="SecurePassword123!")

        response = self.client.get(reverse("orders:order_create"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John")
        self.assertContains(response, "Doe")
        self.assertContains(response, "john@example.com")
        self.assertContains(response, "+1 555-123-4567")

    def test_order_create_success_atomic_stock_decrement(self):
        self._fill_cart(self.product, quantity=3)
        initial_stock = self.product.stock

        form_data = {
            "first_name": "Guest",
            "last_name": "Shopper",
            "email": "guest@example.com",
            "phone": "1234567890",
            "address": "456 Market St",
            "city": "San Francisco",
            "postal_code": "94105",
            "country": "United States",
        }
        response = self.client.post(reverse("orders:order_create"), form_data)

        self.assertEqual(response.status_code, 302)
        order = Order.objects.first()
        self.assertIsNotNone(order)
        self.assertEqual(order.email, "guest@example.com")
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().quantity, 3)

        # Verify product inventory stock was decremented
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, initial_stock - 3)

        # Verify cart was cleared
        session = self.client.session
        self.assertNotIn(CART_SESSION_ID, session)

    def test_order_create_insufficient_stock_atomic_rollback(self):
        # Desired quantity exceeds stock
        self._fill_cart(self.product, quantity=5)
        # Concurrently reduce available stock to 2
        self.product.stock = 2
        self.product.save()

        form_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "address": "123 Main St",
            "city": "Boston",
            "postal_code": "02101",
            "country": "United States",
        }
        response = self.client.post(reverse("orders:order_create"), form_data)

        # Should remain on page and show error message
        self.assertEqual(response.status_code, 200)
        # Transaction rolled back: zero orders created
        self.assertEqual(Order.objects.count(), 0)
        # Stock untouched
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 2)

    def test_order_created_view_access_control(self):
        order = Order.objects.create(
            user=self.user,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            address="123 Main St",
            city="Boston",
            postal_code="02101",
            country="United States",
        )

        # Other user cannot access John's order
        self.client.login(username="janedoe", password="SecurePassword123!")
        response = self.client.get(
            reverse("orders:order_created", kwargs={"order_id": order.id})
        )
        self.assertEqual(response.status_code, 403)

        # Owner can access
        self.client.login(username="johndoe", password="SecurePassword123!")
        response = self.client.get(
            reverse("orders:order_created", kwargs={"order_id": order.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, order.order_number)

    def test_order_list_requires_login(self):
        response = self.client.get(reverse("orders:order_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_order_list_shows_only_user_orders_and_filters(self):
        self.client.login(username="johndoe", password="SecurePassword123!")
        order1 = Order.objects.create(
            user=self.user,
            status=Order.STATUS_PENDING,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            address="123 Main St",
            city="Boston",
            postal_code="02101",
            country="United States",
        )
        order2 = Order.objects.create(
            user=self.user,
            status=Order.STATUS_DELIVERED,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            address="123 Main St",
            city="Boston",
            postal_code="02101",
            country="United States",
        )
        # Order belonging to Jane
        Order.objects.create(
            user=self.other_user,
            status=Order.STATUS_DELIVERED,
            first_name="Jane",
            last_name="Doe",
            email="jane@example.com",
            address="456 Jane St",
            city="Boston",
            postal_code="02101",
            country="United States",
        )

        # All orders for John
        response = self.client.get(reverse("orders:order_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, order1.order_number)
        self.assertContains(response, order2.order_number)
        self.assertEqual(len(response.context["orders"]), 2)

        # Filter by status 'delivered'
        response = self.client.get(reverse("orders:order_list") + "?status=delivered")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, order2.order_number)
        self.assertNotContains(response, order1.order_number)

    def test_order_detail_view_permissions(self):
        order = Order.objects.create(
            user=self.user,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            address="123 Main St",
            city="Boston",
            postal_code="02101",
            country="United States",
        )
        # Unauthorized user
        self.client.login(username="janedoe", password="SecurePassword123!")
        response = self.client.get(
            reverse("orders:order_detail", kwargs={"order_number": order.order_number})
        )
        self.assertEqual(response.status_code, 403)

        # Authorized user
        self.client.login(username="johndoe", password="SecurePassword123!")
        response = self.client.get(
            reverse("orders:order_detail", kwargs={"order_number": order.order_number})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, order.order_number)


class OrderAdminTestCase(TestCase):
    """
    Tests for Django Admin custom actions and displays.
    """

    def setUp(self):
        self.order = Order.objects.create(
            first_name="Admin",
            last_name="Tester",
            email="admin@example.com",
            address="1 Admin Way",
            city="Adminville",
            postal_code="10001",
            country="United States",
        )

    def test_admin_mark_as_paid_and_shipped(self):
        admin = OrderAdmin(Order, None)
        qs = Order.objects.filter(id=self.order.id)

        with patch.object(admin, "message_user"):
            admin.mark_as_paid(None, qs)
            self.order.refresh_from_db()
            self.assertTrue(self.order.paid)
            self.assertEqual(self.order.status, Order.STATUS_PAID)

            admin.mark_as_shipped(None, qs)
            self.order.refresh_from_db()
            self.assertEqual(self.order.status, Order.STATUS_SHIPPED)


class OrderPaymentIntegrationTestCase(TestCase):
    """
    Comprehensive tests for Stripe & Card payment workflows, sandbox processing,
    permission controls, and webhooks.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="shopper1",
            email="shopper1@example.com",
            password="Password123!",
            first_name="Shopper",
            last_name="One",
        )
        self.intruder = User.objects.create_user(
            username="intruder",
            email="intruder@example.com",
            password="Password123!",
        )
        self.category = Category.objects.create(name="Apparel", slug="apparel")
        self.product = Product.objects.create(
            category=self.category,
            name="Classic Hoodie",
            slug="classic-hoodie",
            price=Decimal("65.00"),
            sku="HOOD-001",
            stock=10,
        )
        self.order = Order.objects.create(
            user=self.user,
            first_name="Shopper",
            last_name="One",
            email="shopper1@example.com",
            address="789 Park Ave",
            city="New York",
            postal_code="10021",
            country="United States",
            payment_method="stripe",
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            price=Decimal("65.00"),
            quantity=1,
        )

    def test_order_payment_get_authorized_user(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse(
                "orders:order_payment", kwargs={"order_number": self.order.order_number}
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.order.order_number)
        self.assertContains(response, "Credit / Debit Card Payment")
        self.assertContains(response, "Pay $65.00 Now")

    def test_order_payment_get_unauthorized_user_forbidden(self):
        self.client.force_login(self.intruder)
        response = self.client.get(
            reverse(
                "orders:order_payment", kwargs={"order_number": self.order.order_number}
            )
        )
        self.assertEqual(response.status_code, 403)

    def test_order_payment_successful_card_submission(self):
        self.client.force_login(self.user)
        card_data = {
            "cardholder_name": "Shopper One",
            "card_number": "4242 4242 4242 4242",
            "expiry": "12/28",
            "cvc": "123",
        }
        response = self.client.post(
            reverse(
                "orders:order_payment", kwargs={"order_number": self.order.order_number}
            ),
            card_data,
        )
        self.assertRedirects(
            response,
            reverse("orders:order_created", kwargs={"order_id": self.order.id}),
        )
        self.order.refresh_from_db()
        self.assertTrue(self.order.paid)
        self.assertEqual(self.order.status, Order.STATUS_PAID)
        self.assertTrue(self.order.stripe_payment_intent_id.startswith("pi_mock_"))

    def test_order_payment_declined_card_simulation(self):
        self.client.force_login(self.user)
        declined_card_data = {
            "cardholder_name": "Shopper One",
            "card_number": "4000 0000 0000 0002",
            "expiry": "12/28",
            "cvc": "123",
        }
        response = self.client.post(
            reverse(
                "orders:order_payment", kwargs={"order_number": self.order.order_number}
            ),
            declined_card_data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your card was declined by the issuer")
        self.order.refresh_from_db()
        self.assertFalse(self.order.paid)
        self.assertEqual(self.order.status, Order.STATUS_PENDING)

    def test_order_payment_switch_to_cash_on_delivery(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse(
                "orders:order_payment", kwargs={"order_number": self.order.order_number}
            ),
            {"switch_to_cod": "1"},
        )
        self.assertRedirects(
            response,
            reverse("orders:order_created", kwargs={"order_id": self.order.id}),
        )
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_method, "cod")
        self.assertFalse(self.order.paid)

    def test_order_payment_already_paid_redirects(self):
        self.client.force_login(self.user)
        self.order.mark_as_paid("pi_mock_existing123")
        response = self.client.get(
            reverse(
                "orders:order_payment", kwargs={"order_number": self.order.order_number}
            )
        )
        self.assertRedirects(
            response,
            reverse("orders:order_created", kwargs={"order_id": self.order.id}),
        )

    def test_stripe_webhook_successful_payment_intent(self):
        import json

        from django.core import mail
        from django.test import override_settings

        payload = {
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "id": "pi_webhook_test_999",
                    "metadata": {"order_number": self.order.order_number},
                }
            },
        }
        mail.outbox.clear()
        with (
            override_settings(STRIPE_WEBHOOK_SECRET="whsec_test_secret"),
            patch("stripe.Webhook.construct_event", return_value=payload),
        ):
            response = self.client.post(
                reverse("orders:stripe_webhook"),
                data=json.dumps(payload),
                content_type="application/json",
                HTTP_STRIPE_SIGNATURE="t=1,v1=sig",
            )
            self.assertEqual(response.status_code, 200)
            # Duplicate webhook delivery should be idempotent (no duplicate email)
            response_dup = self.client.post(
                reverse("orders:stripe_webhook"),
                data=json.dumps(payload),
                content_type="application/json",
                HTTP_STRIPE_SIGNATURE="t=1,v1=sig",
            )
            self.assertEqual(response_dup.status_code, 200)

        self.order.refresh_from_db()
        self.assertTrue(self.order.paid)
        self.assertEqual(self.order.status, Order.STATUS_PAID)
        self.assertEqual(self.order.stripe_payment_intent_id, "pi_webhook_test_999")
        self.assertEqual(len(mail.outbox), 1)

    def test_stripe_webhook_rejects_missing_secret(self):
        import json

        from django.test import override_settings

        payload = {
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "id": "pi_forged",
                    "metadata": {"order_number": self.order.order_number},
                }
            },
        }
        with override_settings(STRIPE_WEBHOOK_SECRET=""):
            response = self.client.post(
                reverse("orders:stripe_webhook"),
                data=json.dumps(payload),
                content_type="application/json",
            )
        self.assertEqual(response.status_code, 400)
        self.order.refresh_from_db()
        self.assertFalse(self.order.paid)

    def test_card_payment_form_rejects_invalid_or_expired_expiry(self):
        from .forms import CardPaymentForm

        bad_form = CardPaymentForm(
            data={
                "cardholder_name": "Shopper One",
                "card_number": "4242424242424242",
                "expiry": "not-a-date",
                "cvc": "123",
            }
        )
        self.assertFalse(bad_form.is_valid())
        self.assertIn("expiry", bad_form.errors)

        expired_form = CardPaymentForm(
            data={
                "cardholder_name": "Shopper One",
                "card_number": "4242424242424242",
                "expiry": "01/20",
                "cvc": "123",
            }
        )
        self.assertFalse(expired_form.is_valid())
        self.assertIn("expiry", expired_form.errors)


class OrderFulfillmentAndAddressTestCase(TestCase):
    """
    Tests for order cancellation with inventory replenishment, transactional confirmation
    emails, and customer saved address auto-creation.
    """

    def setUp(self):
        from apps.catalog.models import Category, Product

        self.user = User.objects.create_user(
            username="buyer1",
            email="buyer1@example.com",
            password="Password123!",
            first_name="Buyer",
            last_name="One",
        )
        self.intruder = User.objects.create_user(
            username="intruder2",
            email="intruder2@example.com",
            password="Password123!",
        )
        self.category = Category.objects.create(name="Shoes", slug="shoes")
        self.product = Product.objects.create(
            category=self.category,
            name="Trail Runners",
            slug="trail-runners",
            price=Decimal("110.00"),
            sku="RUN-001",
            stock=8,
        )
        self.order = Order.objects.create(
            user=self.user,
            first_name="Buyer",
            last_name="One",
            email="buyer1@example.com",
            address="100 Trail Way",
            city="Denver",
            postal_code="80201",
            country="United States",
            status=Order.STATUS_PENDING,
            payment_method="cod",
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            price=Decimal("110.00"),
            quantity=2,
        )

    def test_order_cancel_restores_inventory_stock(self):
        self.client.force_login(self.user)
        initial_stock = self.product.stock  # 8

        response = self.client.post(
            reverse(
                "orders:order_cancel", kwargs={"order_number": self.order.order_number}
            ),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.STATUS_CANCELLED)

        # Inventory replenished by 2
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, initial_stock + 2)

    def test_order_cancel_rejected_if_not_pending(self):
        self.client.force_login(self.user)
        self.order.status = Order.STATUS_SHIPPED
        self.order.save()

        response = self.client.post(
            reverse(
                "orders:order_cancel", kwargs={"order_number": self.order.order_number}
            ),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.STATUS_SHIPPED)

    def test_order_cancel_unauthorized_forbidden(self):
        self.client.force_login(self.intruder)
        response = self.client.post(
            reverse(
                "orders:order_cancel", kwargs={"order_number": self.order.order_number}
            ),
        )
        self.assertEqual(response.status_code, 403)

    def test_order_confirmation_email_sent_on_checkout(self):
        from django.core import mail

        from apps.cart.cart import CART_SESSION_ID

        # Put item in cart
        session = self.client.session
        session[CART_SESSION_ID] = {
            str(self.product.id): {"quantity": 1, "price": "110.00"}
        }
        session.save()

        mail.outbox.clear()
        form_data = {
            "first_name": "Buyer",
            "last_name": "One",
            "email": "buyer1@example.com",
            "address": "100 Trail Way",
            "city": "Denver",
            "postal_code": "80201",
            "country": "United States",
            "payment_method": "cod",
        }
        response = self.client.post(reverse("orders:order_create"), form_data)
        self.assertEqual(response.status_code, 302)

        # Mail was dispatched
        self.assertEqual(len(mail.outbox), 1)
        sent_email = mail.outbox[0]
        self.assertIn("Order Confirmation", sent_email.subject)
        self.assertIn("buyer1@example.com", sent_email.to)
        self.assertIn("Trail Runners", sent_email.body)

    def test_checkout_save_address(self):
        from apps.accounts.models import Address
        from apps.cart.cart import CART_SESSION_ID

        self.client.force_login(self.user)
        session = self.client.session
        session[CART_SESSION_ID] = {
            str(self.product.id): {"quantity": 1, "price": "110.00"}
        }
        session.save()

        form_data = {
            "first_name": "Buyer",
            "last_name": "One",
            "email": "buyer1@example.com",
            "address": "500 Mountain Rd",
            "city": "Boulder",
            "postal_code": "80301",
            "country": "United States",
            "payment_method": "cod",
            "save_address": "1",
        }
        response = self.client.post(reverse("orders:order_create"), form_data)
        self.assertEqual(response.status_code, 302)

        addr = Address.objects.filter(user=self.user, address="500 Mountain Rd").first()
        self.assertIsNotNone(addr)
        self.assertEqual(addr.city, "Boulder")

    def test_order_cancel_restores_coupon_usage(self):
        from datetime import timedelta

        from django.utils import timezone

        from .models import Coupon

        coupon = Coupon.objects.create(
            code="ONCE",
            discount_type=Coupon.DISCOUNT_TYPE_FIXED,
            discount_value=Decimal("10.00"),
            valid_from=timezone.now() - timedelta(days=1),
            valid_to=timezone.now() + timedelta(days=5),
            usage_limit=1,
            times_used=1,
        )
        self.order.coupon = coupon
        self.order.discount = Decimal("10.00")
        self.order.save()

        self.client.force_login(self.user)
        response = self.client.post(
            reverse(
                "orders:order_cancel", kwargs={"order_number": self.order.order_number}
            ),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        coupon.refresh_from_db()
        self.assertEqual(coupon.times_used, 0)

    def test_multiple_guest_orders_remain_accessible_in_session(self):
        from apps.cart.cart import CART_SESSION_ID

        form_data = {
            "first_name": "Guest",
            "last_name": "Shopper",
            "email": "guest@example.com",
            "address": "123 Guest St",
            "city": "Austin",
            "postal_code": "78701",
            "country": "United States",
            "payment_method": "cod",
        }
        orders_placed = []
        for _ in range(2):
            session = self.client.session
            session[CART_SESSION_ID] = {
                str(self.product.id): {"quantity": 1, "price": "110.00"}
            }
            session.save()
            resp = self.client.post(reverse("orders:order_create"), form_data)
            self.assertEqual(resp.status_code, 302)
            orders_placed.append(Order.objects.order_by("-id").first())

        # Both first and second guest orders must remain accessible
        for guest_order in orders_placed:
            detail_resp = self.client.get(
                reverse(
                    "orders:order_detail",
                    kwargs={"order_number": guest_order.order_number},
                )
            )
            self.assertEqual(detail_resp.status_code, 200)

    def test_order_create_rollback_preserves_cart(self):
        from apps.cart.cart import CART_SESSION_ID

        session = self.client.session
        session[CART_SESSION_ID] = {
            str(self.product.id): {"quantity": 99, "price": "110.00"}
        }
        session.save()

        form_data = {
            "first_name": "Buyer",
            "last_name": "One",
            "email": "buyer1@example.com",
            "address": "100 Trail Way",
            "city": "Denver",
            "postal_code": "80201",
            "country": "United States",
            "payment_method": "cod",
        }
        response = self.client.post(reverse("orders:order_create"), form_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(CART_SESSION_ID, self.client.session)
