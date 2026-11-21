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
            username='testshopper',
            email='shopper@example.com',
            password='Password123!',
            first_name='Alice',
            last_name='Smith',
        )
        self.category = Category.objects.create(name='Footwear', slug='footwear')
        self.product = Product.objects.create(
            category=self.category,
            name='Running Shoes',
            slug='running-shoes',
            price=Decimal('120.00'),
            sku='SHOE-001',
            stock=15,
        )

    def test_order_creation_and_auto_order_number(self):
        order = Order.objects.create(
            user=self.user,
            first_name='Alice',
            last_name='Smith',
            email='shopper@example.com',
            address='123 Running Lane',
            city='Boston',
            postal_code='02101',
            country='United States',
        )
        self.assertTrue(order.order_number.startswith('ORD-'))
        self.assertEqual(order.status, Order.STATUS_PENDING)
        self.assertFalse(order.paid)
        self.assertEqual(order.full_name, 'Alice Smith')
        self.assertEqual(str(order), f'Order #{order.order_number}')

    def test_order_item_cost_and_order_total(self):
        order = Order.objects.create(
            user=self.user,
            first_name='Alice',
            last_name='Smith',
            email='shopper@example.com',
            address='123 Running Lane',
            city='Boston',
            postal_code='02101',
            country='United States',
        )
        item1 = OrderItem.objects.create(
            order=order,
            product=self.product,
            price=Decimal('120.00'),
            quantity=2,
        )
        self.assertEqual(item1.get_cost(), Decimal('240.00'))
        self.assertEqual(order.get_total_cost(), Decimal('240.00'))


class OrdersViewsTestCase(TestCase):
    """
    Integration tests for Checkout, Order Confirmation, Order List, and Invoice views.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username='johndoe',
            email='john@example.com',
            password='SecurePassword123!',
            first_name='John',
            last_name='Doe',
            phone='+1 555-123-4567',
        )
        self.other_user = User.objects.create_user(
            username='janedoe',
            email='jane@example.com',
            password='SecurePassword123!',
            first_name='Jane',
            last_name='Doe',
        )
        self.category = Category.objects.create(name='Gadgets', slug='gadgets')
        self.product = Product.objects.create(
            category=self.category,
            name='Noise Cancelling Headphones',
            slug='headphones',
            price=Decimal('250.00'),
            sku='HP-001',
            stock=10,
        )

    def _fill_cart(self, product, quantity=2):
        session = self.client.session
        session[CART_SESSION_ID] = {
            str(product.id): {
                'quantity': quantity,
                'price': str(product.price),
            }
        }
        session.save()

    def test_order_create_empty_cart_redirects(self):
        response = self.client.get(reverse('orders:order_create'))
        self.assertRedirects(response, reverse('cart:cart_detail'))

    def test_order_create_get_prepopulates_user_data(self):
        self._fill_cart(self.product, 1)
        self.client.login(username='johndoe', password='SecurePassword123!')

        response = self.client.get(reverse('orders:order_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John')
        self.assertContains(response, 'Doe')
        self.assertContains(response, 'john@example.com')
        self.assertContains(response, '+1 555-123-4567')

    def test_order_create_success_atomic_stock_decrement(self):
        self._fill_cart(self.product, quantity=3)
        initial_stock = self.product.stock

        form_data = {
            'first_name': 'Guest',
            'last_name': 'Shopper',
            'email': 'guest@example.com',
            'phone': '1234567890',
            'address': '456 Market St',
            'city': 'San Francisco',
            'postal_code': '94105',
            'country': 'United States',
        }
        response = self.client.post(reverse('orders:order_create'), form_data)

        self.assertEqual(response.status_code, 302)
        order = Order.objects.first()
        self.assertIsNotNone(order)
        self.assertEqual(order.email, 'guest@example.com')
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
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'address': '123 Main St',
            'city': 'Boston',
            'postal_code': '02101',
            'country': 'United States',
        }
        response = self.client.post(reverse('orders:order_create'), form_data)

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
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            address='123 Main St',
            city='Boston',
            postal_code='02101',
            country='United States',
        )

        # Other user cannot access John's order
        self.client.login(username='janedoe', password='SecurePassword123!')
        response = self.client.get(reverse('orders:order_created', kwargs={'order_id': order.id}))
        self.assertEqual(response.status_code, 403)

        # Owner can access
        self.client.login(username='johndoe', password='SecurePassword123!')
        response = self.client.get(reverse('orders:order_created', kwargs={'order_id': order.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, order.order_number)

    def test_order_list_requires_login(self):
        response = self.client.get(reverse('orders:order_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_order_list_shows_only_user_orders_and_filters(self):
        self.client.login(username='johndoe', password='SecurePassword123!')
        order1 = Order.objects.create(
            user=self.user,
            status=Order.STATUS_PENDING,
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            address='123 Main St',
            city='Boston',
            postal_code='02101',
            country='United States',
        )
        order2 = Order.objects.create(
            user=self.user,
            status=Order.STATUS_DELIVERED,
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            address='123 Main St',
            city='Boston',
            postal_code='02101',
            country='United States',
        )
        # Order belonging to Jane
        Order.objects.create(
            user=self.other_user,
            status=Order.STATUS_DELIVERED,
            first_name='Jane',
            last_name='Doe',
            email='jane@example.com',
            address='456 Jane St',
            city='Boston',
            postal_code='02101',
            country='United States',
        )

        # All orders for John
        response = self.client.get(reverse('orders:order_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, order1.order_number)
        self.assertContains(response, order2.order_number)
        self.assertEqual(len(response.context['orders']), 2)

        # Filter by status 'delivered'
        response = self.client.get(reverse('orders:order_list') + '?status=delivered')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, order2.order_number)
        self.assertNotContains(response, order1.order_number)

    def test_order_detail_view_permissions(self):
        order = Order.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            address='123 Main St',
            city='Boston',
            postal_code='02101',
            country='United States',
        )
        # Unauthorized user
        self.client.login(username='janedoe', password='SecurePassword123!')
        response = self.client.get(reverse('orders:order_detail', kwargs={'order_number': order.order_number}))
        self.assertEqual(response.status_code, 403)

        # Authorized user
        self.client.login(username='johndoe', password='SecurePassword123!')
        response = self.client.get(reverse('orders:order_detail', kwargs={'order_number': order.order_number}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, order.order_number)


class OrderAdminTestCase(TestCase):
    """
    Tests for Django Admin custom actions and displays.
    """

    def setUp(self):
        self.order = Order.objects.create(
            first_name='Admin',
            last_name='Tester',
            email='admin@example.com',
            address='1 Admin Way',
            city='Adminville',
            postal_code='10001',
            country='United States',
        )

    def test_admin_mark_as_paid_and_shipped(self):
        admin = OrderAdmin(Order, None)
        qs = Order.objects.filter(id=self.order.id)

        with patch.object(admin, 'message_user'):
            admin.mark_as_paid(None, qs)
            self.order.refresh_from_db()
            self.assertTrue(self.order.paid)
            self.assertEqual(self.order.status, Order.STATUS_PAID)

            admin.mark_as_shipped(None, qs)
            self.order.refresh_from_db()
            self.assertEqual(self.order.status, Order.STATUS_SHIPPED)
