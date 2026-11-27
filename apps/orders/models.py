import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone

from apps.catalog.models import Product


class Coupon(models.Model):
    """
    Promotional coupon model supporting percentage-off or fixed-amount discounts,
    validity timeframes, minimum order spends, and usage tracking.
    """

    DISCOUNT_TYPE_PERCENT = "percent"
    DISCOUNT_TYPE_FIXED = "fixed"
    DISCOUNT_TYPE_CHOICES = (
        (DISCOUNT_TYPE_PERCENT, "Percentage (%)"),
        (DISCOUNT_TYPE_FIXED, "Fixed Amount ($)"),
    )

    code = models.CharField(max_length=50, unique=True, db_index=True)
    discount_type = models.CharField(
        max_length=10,
        choices=DISCOUNT_TYPE_CHOICES,
        default=DISCOUNT_TYPE_PERCENT,
    )
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Percentage off (e.g., 20 for 20%) or fixed amount (e.g., 15.00 for $15).",
    )
    min_purchase_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Minimum subtotal required to apply coupon.",
    )
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    usage_limit = models.PositiveIntegerField(
        default=0,
        help_text="Maximum number of times this coupon can be used (0 for unlimited).",
    )
    times_used = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"
        ordering = ("-created_at",)

    def __str__(self):
        if self.discount_type == self.DISCOUNT_TYPE_PERCENT:
            return f"{self.code} ({int(self.discount_value)}% off)"
        return f"{self.code} (${self.discount_value:.2f} off)"

    def is_valid(self, subtotal=Decimal("0.00")):
        """
        Check if coupon is active, within date window, below usage limit, and meets min spend.
        """
        now = timezone.now()
        if not self.is_active:
            return False, "This coupon is no longer active."
        if now < self.valid_from or now > self.valid_to:
            return False, "This coupon has expired or is not yet valid."
        if self.usage_limit > 0 and self.times_used >= self.usage_limit:
            return False, "This coupon has reached its maximum redemption limit."
        if Decimal(str(subtotal)) < self.min_purchase_amount:
            return (
                False,
                f"Minimum cart subtotal of ${self.min_purchase_amount:.2f} required for this coupon.",
            )
        return True, ""

    def calculate_discount(self, subtotal):
        """
        Calculate discount amount clamped to the subtotal.
        """
        subtotal = Decimal(str(subtotal))
        if self.discount_type == self.DISCOUNT_TYPE_PERCENT:
            discount = (subtotal * self.discount_value) / Decimal(100)
        else:
            discount = self.discount_value
        return min(subtotal, max(Decimal("0.00"), discount))


class Order(models.Model):
    """
    Customer order record tracking customer credentials, shipping address,
    fulfillment status, and total purchase value.
    """

    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_PAID = "paid"
    STATUS_SHIPPED = "shipped"
    STATUS_DELIVERED = "delivered"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_PAID, "Paid"),
        (STATUS_SHIPPED, "Shipped"),
        (STATUS_DELIVERED, "Delivered"),
        (STATUS_CANCELLED, "Cancelled"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="orders",
        null=True,
        blank=True,
    )
    order_number = models.CharField(
        max_length=64,
        unique=True,
        editable=False,
        db_index=True,
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default="United States")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    paid = models.BooleanField(default=False)
    payment_method = models.CharField(
        max_length=20,
        choices=(
            ("stripe", "Credit or Debit Card (Stripe)"),
            ("cod", "Cash on Delivery"),
        ),
        default="stripe",
    )
    stripe_payment_intent_id = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )
    coupon = models.ForeignKey(
        Coupon,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="orders",
    )
    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ("-created_at",)
        indexes = (
            models.Index(fields=("-created_at",)),
            models.Index(fields=("order_number",)),
            models.Index(fields=("status",)),
        )

    def __str__(self):
        return f"Order #{self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            "orders:order_detail", kwargs={"order_number": self.order_number}
        )

    def get_subtotal_cost(self):
        return sum(item.get_cost() for item in self.items.all())

    def get_total_cost(self):
        subtotal = self.get_subtotal_cost()
        discount = self.discount or Decimal("0.00")
        return max(Decimal("0.00"), subtotal - discount)

    def mark_as_paid(self, payment_intent_id=None):
        """Mark order as paid and transition status to STATUS_PAID."""
        self.paid = True
        self.status = self.STATUS_PAID
        if payment_intent_id:
            self.stripe_payment_intent_id = payment_intent_id
        self.save(
            update_fields=["paid", "status", "stripe_payment_intent_id", "updated_at"]
        )

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class OrderItem(models.Model):
    """
    Individual product line item associated with an order.
    """

    order = models.ForeignKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        related_name="order_items",
        on_delete=models.PROTECT,
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    def __str__(self):
        return f"{self.quantity}x {self.product.name} (Order {self.order.order_number})"

    def get_cost(self):
        return Decimal(str(self.price)) * self.quantity
