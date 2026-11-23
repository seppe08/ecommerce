import json
import uuid

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.cart.cart import Cart
from apps.catalog.models import Product

from .forms import CardPaymentForm, OrderCreateForm
from .models import Order, OrderItem


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
            try:
                with transaction.atomic():
                    order = form.save(commit=False)
                    if request.user.is_authenticated:
                        order.user = request.user
                    active_coupon = cart.coupon
                    if active_coupon:
                        order.coupon = active_coupon
                        order.discount = cart.get_discount()
                        active_coupon.times_used += 1
                        active_coupon.save(update_fields=["times_used"])
                    order.save()

                    for item in cart:
                        # select_for_update prevents race conditions on inventory decrement
                        product = Product.objects.select_for_update().get(
                            id=item["product"].id
                        )
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

                    # Order successfully created; clear cart from session
                    cart.clear()
                    request.session["order_id"] = order.id

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
                # Handled insufficient stock; redisplay checkout with error
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

    # Security check: guest must have order_id in session; authenticated must own order or be staff
    if order.user:
        if not request.user.is_authenticated or (
            order.user != request.user and not request.user.is_staff
        ):
            raise PermissionDenied("You do not have permission to view this order.")
    else:
        # Guest order: allow if placed in current session
        session_order_id = request.session.get("order_id")
        if not request.user.is_staff and session_order_id != order.id:
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

    if order.user:
        if not request.user.is_authenticated or (
            order.user != request.user and not request.user.is_staff
        ):
            raise PermissionDenied(
                "You do not have permission to view this order invoice."
            )
    else:
        session_order_id = request.session.get("order_id")
        if not request.user.is_staff and session_order_id != order.id:
            raise PermissionDenied(
                "You do not have permission to view this order invoice."
            )

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

    # Permission check: order owner or guest with session order_id or staff
    if order.user:
        if not request.user.is_authenticated or (
            order.user != request.user and not request.user.is_staff
        ):
            raise PermissionDenied("You do not have permission to pay for this order.")
    else:
        session_order_id = request.session.get("order_id")
        if not request.user.is_staff and session_order_id != order.id:
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
            messages.info(
                request,
                f"Payment method updated to Cash on Delivery for Order #{order.order_number}.",
            )
            return redirect("orders:order_created", order_id=order.id)

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
                # If a live/real stripe key is configured (not the default mock key)
                if stripe_sec_key and not stripe_sec_key.startswith(
                    "sk_test_aurastore_mock"
                ):
                    try:
                        import stripe

                        stripe.api_key = stripe_sec_key
                        intent = stripe.PaymentIntent.create(
                            amount=int(order.get_total_cost() * 100),
                            currency="usd",
                            metadata={"order_number": order.order_number},
                            description=f"AuraStore Order #{order.order_number}",
                        )
                        payment_intent_id = intent.id
                    except stripe.StripeError as e:
                        messages.error(
                            request, f"Payment gateway communication error: {e!s}"
                        )
                        return render(
                            request,
                            "orders/order_payment.html",
                            {
                                "order": order,
                                "form": form,
                                "stripe_pub_key": stripe_pub_key,
                                "page_title": f"Pay Order #{order.order_number} — AuraStore",
                            },
                        )

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
    Handle incoming Stripe webhook notifications.
    """
    payload = request.body
    sig_header = request.headers.get("stripe-signature", "")
    webhook_secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", "")

    if webhook_secret:
        import stripe

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        except (ValueError, stripe.SignatureVerificationError):
            return HttpResponse(status=400)
    else:
        try:
            event = json.loads(payload.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return HttpResponse(status=400)

    event_type = event.get("type", "")
    if event_type == "payment_intent.succeeded":
        intent = event.get("data", {}).get("object", {})
        order_number = intent.get("metadata", {}).get("order_number")
        if order_number:
            try:
                order = Order.objects.get(order_number=order_number)
                order.mark_as_paid(payment_intent_id=intent.get("id"))
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

        order.status = Order.STATUS_CANCELLED
        order.save(update_fields=["status", "updated_at"])

    messages.success(
        request,
        f"Order #{order.order_number} has been cancelled and its inventory was replenished.",
    )
    return redirect("orders:order_detail", order_number=order.order_number)
