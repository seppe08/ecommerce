from .cart import Cart


def cart(request):
    """
    Context processor making the Cart instance globally available
    in all templates for dynamic header counters, badges, and carts.
    """
    return {"cart": Cart(request)}
