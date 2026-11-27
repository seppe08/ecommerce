import uuid

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.db.models import F
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.cart.cart import Cart
from apps.catalog.models import Product

from .forms import CardPaymentForm, OrderCreateForm
from .models import Coupon, Order, OrderItem


def _has_order_access(request, order):
    """Return True if the request user or guest session owns the order."""
    if order.user:
        return request.user.is_authenticated and (
            order.user == request.user or request.user.is_staff
        )
    if request.user.is_staff:
        return True
    guest_ids = request.session.get("guest_order_ids", [])
    return order.id in guest_ids or request.session.get("order_id") == order.id


def _record_guest_order(request, order_id):
    """Record a guest order ID in the session without overwriting prior orders."""
    guest_ids = list(request.session.get("guest_order_ids", []))
    if order_id not in guest_ids:
        guest_ids.append(order_id)
    request.session["guest_order_ids"] = guest_ids
    request.session["order_id"] = order_id


def order_create(request):
    """
    Checkout view: validates non-empty cart, collects shipping details,
    atomically creates Order and OrderItems, decrements product inventory,
    clears cart, and redirects to confirmation.
    """
    cart = Cart(request)
    if cart.get_item_count() == 0:
        messages.warning(
            request, "Your cart is empty. Please add items before checking out."
        )
        return redirect("cart:cart_detail")

    if request.method == "POST":
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = None
            try:
                with transaction.atomic():
                    order = form.save(commit=False)
                    if request.user.is_authenticated:
                        order.user = request.user
                    active_coupon = cart.coupon
                    if active_coupon:
                        locked_coupon = Coupon.objects.select_for_update().get(
                            id=active_coupon.id
                        )
                        is_valid, coupon_err = locked_coupon.is_valid(
                            cart.get_total_price()
                        )
                        if not is_valid:
                            cart.remove_coupon()
                            messages.error(request, coupon_err)
                            raise ValueError("Invalid coupon")
                        order.coupon = locked_coupon
                        order.discount = locked_coupon.calculate_discount(
                            cart.get_total_price()
                        )
                        locked_coupon.times_used = F("times_used") + 1
                        locked_coupon.save(update_fields=["times_used"])
                    order.save()

                    for item in cart:
                        # select_for_update prevents race conditions on inventory decrement
                        try:
                            product = Product.objects.select_for_update().get(
                                id=item["product"].id, is_active=True
                            )
                        except Product.DoesNotExist:
                            messages.error(
                                request,
                                f'Sorry, "{item["product"].name}" is no longer available.',
                            )
                            raise ValueError("Unavailable product")
                        if product.stock < item["quantity"]:
                            messages.error(
                                request,
                                f'Sorry, insufficient stock for "{product.name}". '
                                f"Only {product.stock} units remain available.",
                            )
                            raise ValueError("Insufficient stock")

                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            price=item["price"],
                            quantity=item["quantity"],
                        )
                        product.stock -= item["quantity"]
                        product.save()

                    if request.user.is_authenticated and form.cleaned_data.get(
                        "save_address"
                    ):
                        from apps.accounts.models import Address

                        Address.objects.get_or_create(
                            user=request.user,
                            address=order.address,
                            city=order.city,
                            postal_code=order.postal_code,
                            country=order.country,
                            defaults={
                                "full_name": order.full_name,
                                "phone": order.phone,
                                "is_default": not request.user.addresses.exists(),
                            },
                        )

                # DB transaction committed; now clear session cart and dispatch post-order flow
                cart.clear()
                _record_guest_order(request, order.id)

                if order.payment_method == "stripe":
                    return redirect(
                        "orders:order_payment", order_number=order.order_number
                    )

                send_order_confirmation_email(order)
                messages.success(
                    request,
                    f"Thank you! Your order #{order.order_number} has been placed successfully.",
                )
                return redirect("orders:order_created", order_id=order.id)

            except ValueError:
                # Handled insufficient stock / invalid coupon / unavailable product
                pass

    else:
        # Prepopulate initial data for authenticated customers
        initial = {}
        if request.user.is_authenticated:
            initial["first_name"] = request.user.first_name
            initial["last_name"] = request.user.last_name
            initial["email"] = request.user.email
            phone = getattr(request.user, "phone", "")
            if phone:
                initial["phone"] = phone
            default_address = (
                request.user.addresses.filter(is_default=True).first()
                or request.user.addresses.first()
            )
            if default_address:
                initial["address"] = default_address.address
                initial["city"] = default_address.city
                initial["postal_code"] = default_address.postal_code
                initial["country"] = default_address.country
                if default_address.phone:
                    initial["phone"] = default_address.phone
        form = OrderCreateForm(initial=initial)

    subtotal = cart.get_total_price()
    discount = cart.get_discount()
    total = cart.get_total_price_after_discount()
    context = {
        "cart": cart,
        "form": form,
        "subtotal": subtotal,
        "discount": discount,
        "total": total,
        "coupon": cart.coupon,
        "saved_addresses": (
            request.user.addresses.all() if request.user.is_authenticated else []
        ),
        "page_title": "Checkout — AuraStore",
    }
    return render(request, "orders/order_create.html", context)


def order_created(request, order_id):
    """
    Order confirmation view: renders invoice receipt and confirmation message.
    """
    order = get_object_or_404(
        Order.objects.prefetch_related("items__product"), id=order_id
    )

    if not _has_order_access(request, order):
        raise PermissionDenied("You do not have permission to view this order.")

    context = {
        "order": order,
        "page_title": f"Order Confirmation #{order.order_number} — AuraStore",
    }
    return render(request, "orders/order_created.html", context)


@login_required
def order_list(request):
    """
    Customer portal view displaying authenticated customer's order history
    with status badges and filter controls.
    """
    orders = Order.objects.filter(user=request.user).prefetch_related("items__product")

    status_filter = request.GET.get("status")
    if status_filter and status_filter in dict(Order.STATUS_CHOICES):
        orders = orders.filter(status=status_filter)

    context = {
        "orders": orders,
        "current_status": status_filter or "all",
        "status_choices": Order.STATUS_CHOICES,
        "page_title": "My Orders — AuraStore",
    }
    return render(request, "orders/order_list.html", context)


def order_detail(request, order_number):
    """
    Detailed order receipt and invoice view for a specific order number.
    """
    order = get_object_or_404(
        Order.objects.prefetch_related("items__product"),
        order_number=order_number,
    )

    if not _has_order_access(request, order):
        raise PermissionDenied("You do not have permission to view this order invoice.")

    context = {
        "order": order,
        "page_title": f"Invoice #{order.order_number} — AuraStore",
    }
    return render(request, "orders/order_detail.html", context)


def order_payment(request, order_number):
    """
    Payment view for Stripe / Credit Card checkout.
    Verifies order ownership/session, renders card payment form,
    processes card payment (real Stripe or simulated test sandbox),
    marks order as paid, and redirects to order_created.
    """
    order = get_object_or_404(
        Order.objects.prefetch_related("items__product"),
        order_number=order_number,
    )

    if not _has_order_access(request, order):
        raise PermissionDenied("You do not have permission to pay for this order.")

    if order.paid:
        messages.info(request, f"Order #{order.order_number} has already been paid.")
        return redirect("orders:order_created", order_id=order.id)

    stripe_pub_key = getattr(
        settings, "STRIPE_PUBLISHABLE_KEY", "pk_test_aurastore_mock_key"
    )
    stripe_sec_key = getattr(
        settings, "STRIPE_SECRET_KEY", "sk_test_aurastore_mock_key"
    )

    if request.method == "POST":
        # Allow user to switch to COD
        if request.POST.get("switch_to_cod") == "1":
            order.payment_method = "cod"
            order.save(update_fields=["payment_method", "updated_at"])
            send_order_confirmation_email(order)
            messages.info(
                request,
                f"Payment method updated to Cash on Delivery for Order #{order.order_number}.",
            )
            return redirect("orders:order_created", order_id=order.id)

        # If a real Stripe key is configured, redirect to PCI-compliant Stripe Checkout Session
        if stripe_sec_key and not stripe_sec_key.startswith("sk_test_aurastore_mock"):
            try:
                import stripe

                stripe.api_key = stripe_sec_key
                success_url = request.build_absolute_uri(
                    reverse("orders:order_created", kwargs={"order_id": order.id})
                )
                cancel_url = request.build_absolute_uri(
                    reverse(
                        "orders:order_payment",
                        kwargs={"order_number": order.order_number},
                    )
                )
                checkout_session = stripe.checkout.Session.create(
                    mode="payment",
                    customer_email=order.email,
                    line_items=[
                        {
                            "price_data": {
                                "currency": "usd",
                                "product_data": {
                                    "name": f"AuraStore Order #{order.order_number}",
                                },
                                "unit_amount": int(order.get_total_cost() * 100),
                            },
                            "quantity": 1,
                        }
                    ],
                    metadata={"order_number": order.order_number},
                    success_url=success_url,
                    cancel_url=cancel_url,
                )
                return redirect(checkout_session.url)
            except stripe.StripeError as e:
                messages.error(request, f"Payment gateway communication error: {e!s}")
                return render(
                    request,
                    "orders/order_payment.html",
                    {
                        "order": order,
                        "form": CardPaymentForm(),
                        "stripe_pub_key": stripe_pub_key,
                        "page_title": f"Pay Order #{order.order_number} — AuraStore",
                    },
                )

        # Sandbox / mock mode using CardPaymentForm
        form = CardPaymentForm(request.POST)
        if form.is_valid():
            card_number = form.cleaned_data["card_number"]
            # Simulation of card decline if card ends with 0002
            if card_number.endswith("0002"):
                messages.error(
                    request,
                    "Your card was declined by the issuer. Please try another card or switch to Cash on Delivery.",
                )
            else:
                payment_intent_id = f"pi_mock_{uuid.uuid4().hex[:16]}"
                order.mark_as_paid(payment_intent_id=payment_intent_id)
                send_order_confirmation_email(order)
                messages.success(
                    request,
                    f"Payment successful! Order #{order.order_number} is confirmed and paid.",
                )
                return redirect("orders:order_created", order_id=order.id)
    else:
        form = CardPaymentForm()

    context = {
        "order": order,
        "form": form,
        "stripe_pub_key": stripe_pub_key,
        "page_title": f"Pay Order #{order.order_number} — AuraStore",
    }
    return render(request, "orders/order_payment.html", context)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Handle incoming Stripe webhook notifications with mandatory signature verification
    in production and idempotent order fulfillment.
    """
    payload = request.body
    sig_header = request.headers.get("stripe-signature", "")
    webhook_secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", "")

    if not webhook_secret:
        return HttpResponse(status=400)

    import stripe

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except (ValueError, stripe.SignatureVerificationError):
        return HttpResponse(status=400)

    event_type = event.get("type", "")
    if event_type in ("payment_intent.succeeded", "checkout.session.completed"):
        obj = event.get("data", {}).get("object", {})
        order_number = obj.get("metadata", {}).get("order_number")
        payment_intent_id = obj.get("payment_intent") or obj.get("id")
        if order_number:
            try:
                order = Order.objects.get(order_number=order_number)
                if not order.paid:
                    order.mark_as_paid(payment_intent_id=payment_intent_id)
                    send_order_confirmation_email(order)
            except Order.DoesNotExist:
                pass

    return JsonResponse({"status": "success"})


def send_order_confirmation_email(order):
    """
    Dispatch itemized plaintext and HTML confirmation receipt email to the customer.
    """
    subject = f"Order Confirmation #{order.order_number} — AuraStore"
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "orders@aurastore.com")
    to = [order.email]

    context = {"order": order}
    text_content = render_to_string("orders/emails/order_confirmation.txt", context)
    html_content = render_to_string("orders/emails/order_confirmation.html", context)

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=True)


@login_required
@require_POST
def order_cancel(request, order_number):
    """
    Allow customer to cancel a pending order and atomically restore inventory stock.
    """
    order = get_object_or_404(Order, order_number=order_number)

    if order.user != request.user and not request.user.is_staff:
        raise PermissionDenied("You do not have permission to cancel this order.")

    if order.status != Order.STATUS_PENDING:
        messages.error(
            request,
            f"Order #{order.order_number} cannot be cancelled because it is already {order.get_status_display()}.",
        )
        return redirect("orders:order_detail", order_number=order.order_number)

    with transaction.atomic():
        for item in order.items.select_related("product"):
            product = Product.objects.select_for_update().get(id=item.product.id)
            product.stock += item.quantity
            product.save(update_fields=["stock"])

        if order.coupon_id:
            locked_coupon = Coupon.objects.select_for_update().get(id=order.coupon_id)
            if locked_coupon.times_used > 0:
                locked_coupon.times_used = F("times_used") - 1
                locked_coupon.save(update_fields=["times_used"])

        order.status = Order.STATUS_CANCELLED
        order.save(update_fields=["status", "updated_at"])

    messages.success(
        request,
        f"Order #{order.order_number} has been cancelled and its inventory was replenished.",
    )
    return redirect("orders:order_detail", order_number=order.order_number)
