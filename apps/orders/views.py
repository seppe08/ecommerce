from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from apps.cart.cart import Cart
from apps.catalog.models import Product

from .forms import OrderCreateForm
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

                    # Order successfully created; clear cart from session
                    cart.clear()
                    request.session["order_id"] = order.id
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
        form = OrderCreateForm(initial=initial)

    subtotal = cart.get_total_price()
    context = {
        "cart": cart,
        "form": form,
        "subtotal": subtotal,
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
