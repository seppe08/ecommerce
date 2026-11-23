from decimal import Decimal

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.catalog.models import Product

from .cart import Cart
from .forms import CartAddProductForm


def is_ajax(request):
    """
    Check if the request is an AJAX / fetch request.
    """
    return request.headers.get(
        "x-requested-with"
    ) == "XMLHttpRequest" or "application/json" in request.headers.get("Accept", "")


def cart_detail(request):
    """
    Display the shopping cart with full breakdown of items, unit prices,
    quantities, line totals, discounts, tax calculation, and checkout CTA.
    """
    cart = Cart(request)
    subtotal = cart.get_total_price()
    discount = cart.get_discount()
    coupon = cart.coupon
    estimated_tax = Decimal("0.00")
    total = cart.get_total_price_after_discount() + estimated_tax

    context = {
        "cart": cart,
        "subtotal": subtotal,
        "discount": discount,
        "coupon": coupon,
        "estimated_tax": estimated_tax,
        "total": total,
        "page_title": "Your Shopping Cart — AuraStore",
    }
    return render(request, "cart/cart_detail.html", context)


@require_POST
def coupon_apply(request):
    """
    Validate and apply a promotional coupon code to the user's cart session.
    """
    from apps.orders.models import Coupon

    cart = Cart(request)
    code = request.POST.get("code", "").strip()

    if not code:
        messages.warning(request, "Please enter a coupon code.")
        return redirect("cart:cart_detail")

    try:
        coupon = Coupon.objects.get(code__iexact=code)
        is_valid, error_msg = coupon.is_valid(cart.get_total_price())
        if not is_valid:
            messages.error(request, error_msg)
            if is_ajax(request):
                return JsonResponse(
                    {"success": False, "message": error_msg}, status=400
                )
            return redirect("cart:cart_detail")

        cart.apply_coupon(coupon)
        discount = cart.get_discount()
        msg = f'Coupon "{coupon.code}" applied! You saved ${discount:.2f}.'
        messages.success(request, msg)

        if is_ajax(request):
            return JsonResponse(
                {
                    "success": True,
                    "message": msg,
                    "code": coupon.code,
                    "discount": f"{discount:.2f}",
                    "cart_total": f"{cart.get_total_price_after_discount():.2f}",
                }
            )

    except Coupon.DoesNotExist:
        error_msg = f'Coupon "{code}" is invalid or does not exist.'
        messages.error(request, error_msg)
        if is_ajax(request):
            return JsonResponse({"success": False, "message": error_msg}, status=404)

    return redirect("cart:cart_detail")


@require_POST
def coupon_remove(request):
    """
    Remove currently applied coupon code from cart session.
    """
    cart = Cart(request)
    cart.remove_coupon()
    msg = "Coupon discount removed."
    messages.info(request, msg)

    if is_ajax(request):
        return JsonResponse(
            {
                "success": True,
                "message": msg,
                "cart_total": f"{cart.get_total_price():.2f}",
            }
        )

    return redirect("cart:cart_detail")


@require_POST
def cart_add(request, product_id):
    """
    Handle adding a product to the cart with quantity validation and stock checks.
    Supports both standard form submission and AJAX requests.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)
    form = CartAddProductForm(request.POST)

    if not product.is_in_stock:
        error_msg = f'Sorry, "{product.name}" is currently out of stock.'
        if is_ajax(request):
            return JsonResponse({"success": False, "message": error_msg}, status=400)
        messages.error(request, error_msg)
        return redirect(request.POST.get("next") or product.get_absolute_url())

    if form.is_valid():
        cd = form.cleaned_data
        requested_qty = cd["quantity"]
        override = cd["override"]

        current_qty = cart.cart.get(str(product.id), {}).get("quantity", 0)
        new_total_qty = requested_qty if override else current_qty + requested_qty

        # Stock bounds check
        if new_total_qty > product.stock:
            if override:
                actual_qty = product.stock
            else:
                actual_qty = max(0, product.stock - current_qty)

            if actual_qty <= 0:
                warning_msg = f'Maximum stock reached for "{product.name}" ({product.stock} available).'
                if is_ajax(request):
                    return JsonResponse(
                        {"success": False, "message": warning_msg}, status=400
                    )
                messages.warning(request, warning_msg)
                return redirect(request.POST.get("next") or "cart:cart_detail")

            cart.add(
                product=product,
                quantity=product.stock if override else actual_qty,
                override_quantity=override,
            )
            msg = f'Added maximum available stock ({product.stock} units) of "{product.name}".'
            messages.warning(request, msg)
        else:
            cart.add(
                product=product, quantity=requested_qty, override_quantity=override
            )
            msg = f'"{product.name}" has been added to your cart.'
            messages.success(request, msg)

        if is_ajax(request):
            return JsonResponse(
                {
                    "success": True,
                    "message": msg,
                    "cart_count": cart.get_item_count(),
                    "cart_total": f"{cart.get_total_price():.2f}",
                }
            )

    return redirect(request.POST.get("next") or "cart:cart_detail")


@require_POST
def cart_remove(request, product_id):
    """
    Remove an item from the cart with flash message and JSON or redirect response.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)

    msg = f'"{product.name}" was removed from your cart.'
    messages.info(request, msg)

    if is_ajax(request):
        return JsonResponse(
            {
                "success": True,
                "message": msg,
                "cart_count": cart.get_item_count(),
                "cart_total": f"{cart.get_total_price():.2f}",
            }
        )

    return redirect("cart:cart_detail")


@require_POST
def cart_update_quantity(request, product_id):
    """
    Increment, decrement, or set exact quantity of a cart item with stock bounds checking.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)

    action = request.POST.get("action")
    raw_quantity = request.POST.get("quantity")
    current_qty = cart.cart.get(str(product.id), {}).get("quantity", 1)

    if action == "increase":
        target_qty = current_qty + 1
    elif action == "decrease":
        target_qty = current_qty - 1
    elif raw_quantity is not None:
        try:
            target_qty = int(raw_quantity)
        except (ValueError, TypeError):
            target_qty = current_qty
    else:
        target_qty = current_qty

    if target_qty <= 0:
        cart.remove(product)
        msg = f'"{product.name}" was removed from your cart.'
        messages.info(request, msg)
        if is_ajax(request):
            return JsonResponse(
                {
                    "success": True,
                    "removed": True,
                    "message": msg,
                    "cart_count": cart.get_item_count(),
                    "cart_total": f"{cart.get_total_price():.2f}",
                }
            )
        return redirect("cart:cart_detail")

    if target_qty > product.stock:
        target_qty = product.stock
        cart.add(product=product, quantity=target_qty, override_quantity=True)
        msg = f'Quantity adjusted to available stock ({product.stock} units) for "{product.name}".'
        messages.warning(request, msg)
    else:
        cart.add(product=product, quantity=target_qty, override_quantity=True)
        msg = f'Quantity updated to {target_qty} for "{product.name}".'
        messages.success(request, msg)

    line_item_total = Decimal(str(product.price)) * target_qty

    if is_ajax(request):
        return JsonResponse(
            {
                "success": True,
                "removed": False,
                "quantity": target_qty,
                "line_total": f"{line_item_total:.2f}",
                "cart_count": cart.get_item_count(),
                "cart_total": f"{cart.get_total_price():.2f}",
                "message": msg,
            }
        )

    return redirect("cart:cart_detail")
