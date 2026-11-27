from decimal import Decimal

from django.conf import settings

from apps.catalog.models import Product

CART_SESSION_ID = getattr(settings, "CART_SESSION_ID", "cart")
COUPON_SESSION_ID = "coupon_id"


class Cart:
    """
    Session-backed shopping cart engine managing item quantities,
    line totals, discount calculations, and session persistence.
    """

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_ID)
        if not cart:
            cart = self.session[CART_SESSION_ID] = {}
        self.cart = cart
        self.coupon_id = self.session.get(COUPON_SESSION_ID)
        self._cached_coupon = None
        self._coupon_loaded = False

    @property
    def coupon(self):
        """
        Retrieve and validate currently applied coupon from session (cached per request).
        """
        if self._coupon_loaded:
            if self._cached_coupon is not None:
                valid, _ = self._cached_coupon.is_valid(self.get_total_price())
                if valid:
                    return self._cached_coupon
                self.remove_coupon()
            return None

        self._coupon_loaded = True
        if self.coupon_id:
            from apps.orders.models import Coupon

            try:
                coupon = Coupon.objects.get(id=self.coupon_id)
                valid, _ = coupon.is_valid(self.get_total_price())
                if valid:
                    self._cached_coupon = coupon
                    return coupon
                # Purge invalid/expired coupon
                self.remove_coupon()
            except Coupon.DoesNotExist:
                self.remove_coupon()
        return None

    def apply_coupon(self, coupon):
        """
        Store coupon id in session and update instance.
        """
        self.coupon_id = coupon.id
        self._cached_coupon = coupon
        self._coupon_loaded = True
        self.session[COUPON_SESSION_ID] = coupon.id
        self.save()

    def remove_coupon(self):
        """
        Remove coupon id from session and reset instance.
        """
        self.coupon_id = None
        self._cached_coupon = None
        self._coupon_loaded = True
        if COUPON_SESSION_ID in self.session:
            del self.session[COUPON_SESSION_ID]
            self.save()

    def get_discount(self):
        """
        Calculate discount amount based on active coupon.
        """
        coupon = self.coupon
        if coupon:
            return coupon.calculate_discount(self.get_total_price())
        return Decimal("0.00")

    def get_total_price_after_discount(self):
        """
        Calculate subtotal minus active coupon discount.
        """
        return max(Decimal("0.00"), self.get_total_price() - self.get_discount())

    def add(self, product, quantity=1, override_quantity=False):
        """
        Add a product to the cart or update its quantity.
        """
        product_id = str(product.id)
        quantity = max(1, int(quantity))

        if product_id not in self.cart:
            self.cart[product_id] = {
                "quantity": 0,
                "price": str(product.price),
            }

        if override_quantity:
            self.cart[product_id]["quantity"] = quantity
        else:
            self.cart[product_id]["quantity"] += quantity

        # Update price to current product price in case catalog updated
        self.cart[product_id]["price"] = str(product.price)
        self.save()

    def remove(self, product):
        """
        Remove a product from the cart. Accepts a Product instance or ID.
        """
        product_id = str(getattr(product, "id", product))
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self):
        """
        Mark the session as modified so Django saves it.
        """
        try:
            self.session.modified = True
        except AttributeError:
            pass

    def __iter__(self):
        """
        Iterate over the items in the cart, querying Product objects from the database
        and yielding dicts with product instance, unit price, and calculated line total.
        """
        product_ids = list(self.cart.keys())
        products = Product.objects.filter(id__in=product_ids)
        product_map = {str(p.id): p for p in products}

        # Purge stale keys if product was deleted from DB
        stale_ids = [pid for pid in product_ids if pid not in product_map]
        if stale_ids:
            for pid in stale_ids:
                del self.cart[pid]
            self.save()

        for product_id, item_data in list(self.cart.items()):
            product = product_map.get(product_id)
            if product:
                item = item_data.copy()
                item["product"] = product
                item["price"] = Decimal(item["price"])
                item["total_price"] = item["price"] * item["quantity"]
                yield item

    def __len__(self):
        """
        Count total quantity of items in the cart.
        """
        return sum(item["quantity"] for item in self.cart.values())

    def get_item_count(self):
        """
        Return the total number of items in the cart.
        """
        return sum(item["quantity"] for item in self.cart.values())

    def get_total_price(self):
        """
        Calculate total price across all items in the cart.
        """
        return sum(
            Decimal(item["price"]) * item["quantity"] for item in self.cart.values()
        )

    def clear(self):
        """
        Empty the cart and remove it from the session.
        """
        self.cart = {}
        self.coupon_id = None
        self._cached_coupon = None
        self._coupon_loaded = True
        if CART_SESSION_ID in self.session:
            del self.session[CART_SESSION_ID]
        if COUPON_SESSION_ID in self.session:
            del self.session[COUPON_SESSION_ID]
        self.save()
