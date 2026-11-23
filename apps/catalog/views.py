from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView

from .forms import ReviewForm
from .models import Category, Product, Review, Wishlist


class ProductListView(ListView):
    model = Product
    template_name = "catalog/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.category = None

    def get_queryset(self):
        queryset = (
            Product.objects.filter(is_active=True)
            .select_related("category")
            .prefetch_related("images")
        )

        category_slug = self.kwargs.get("category_slug") or self.request.GET.get(
            "category"
        )
        if category_slug:
            self.category = get_object_or_404(
                Category, slug=category_slug, is_active=True
            )
            queryset = queryset.filter(category=self.category)

        # Keyword Search
        q = self.request.GET.get("q", "").strip()
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) | Q(description__icontains=q) | Q(sku__icontains=q)
            )

        # Featured Filter
        if self.request.GET.get("featured") in ["true", "1"]:
            queryset = queryset.filter(featured=True)

        # Sorting
        sort = self.request.GET.get("sort", "newest")
        sort_mapping = {
            "price_asc": "price",
            "price_desc": "-price",
            "name": "name",
            "newest": "-created_at",
        }
        order_field = sort_mapping.get(sort, "-created_at")
        return queryset.order_by(order_field)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = (
            Category.objects.filter(is_active=True)
            .annotate(
                product_count=Count("products", filter=Q(products__is_active=True))
            )
            .order_by("name")
        )
        context["categories"] = categories
        context["current_category"] = self.category
        context["search_query"] = self.request.GET.get("q", "").strip()
        context["current_sort"] = self.request.GET.get("sort", "newest")
        context["is_featured"] = self.request.GET.get("featured") in ["true", "1"]
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = "catalog/product_detail.html"
    context_object_name = "product"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return (
            Product.objects.filter(is_active=True)
            .select_related("category")
            .prefetch_related("images")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        context["primary_image"] = product.primary_image
        context["gallery_images"] = product.images.all()
        context["related_products"] = (
            Product.objects.filter(category=product.category, is_active=True)
            .exclude(pk=product.pk)
            .select_related("category")
            .prefetch_related("images")[:4]
        )
        context["reviews"] = product.reviews.select_related("user").all()
        context["review_count"] = product.review_count
        context["average_rating"] = product.average_rating
        context["rating_distribution"] = product.get_rating_distribution()
        context["review_form"] = ReviewForm()
        if self.request.user.is_authenticated:
            context["user_review"] = product.reviews.filter(
                user=self.request.user
            ).first()
            context["user_in_wishlist"] = Wishlist.objects.filter(
                user=self.request.user, products=product
            ).exists()
        else:
            context["user_review"] = None
            context["user_in_wishlist"] = False
        return context


@login_required
@require_POST
def add_review(request, slug):
    """
    Submit or update a product review.
    Automatically checks if user has an order containing this product.
    """
    product = get_object_or_404(Product, slug=slug, is_active=True)
    form = ReviewForm(request.POST)

    if form.is_valid():
        from apps.orders.models import Order

        is_verified = Order.objects.filter(
            user=request.user,
            items__product=product,
            paid=True,
        ).exists()

        Review.objects.update_or_create(
            product=product,
            user=request.user,
            defaults={
                "rating": int(form.cleaned_data["rating"]),
                "title": form.cleaned_data["title"],
                "comment": form.cleaned_data["comment"],
                "is_verified_purchase": is_verified,
            },
        )
        messages.success(request, "Thank you! Your product review has been submitted.")
    else:
        messages.error(request, "Please check your review form inputs.")

    return redirect("catalog:product_detail", slug=product.slug)


@login_required
@require_POST
def wishlist_toggle(request, product_id):
    """
    Toggle a product in the user's wishlist via AJAX or standard POST.
    """
    product = get_object_or_404(Product, id=product_id, is_active=True)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)

    if wishlist.products.filter(id=product.id).exists():
        wishlist.products.remove(product)
        in_wishlist = False
        msg = f'"{product.name}" was removed from your wishlist.'
    else:
        wishlist.products.add(product)
        in_wishlist = True
        msg = f'"{product.name}" was saved to your wishlist.'

    messages.info(request, msg)

    is_ajax_req = request.headers.get(
        "x-requested-with"
    ) == "XMLHttpRequest" or "application/json" in request.headers.get("Accept", "")
    if is_ajax_req:
        return JsonResponse(
            {
                "success": True,
                "in_wishlist": in_wishlist,
                "wishlist_count": wishlist.products.count(),
                "message": msg,
            }
        )

    return redirect(request.POST.get("next") or product.get_absolute_url())


@login_required
def wishlist_detail(request):
    """
    Customer portal view displaying all saved wishlist items.
    """
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    products = (
        wishlist.products.filter(is_active=True)
        .select_related("category")
        .prefetch_related("images")
    )

    context = {
        "products": products,
        "wishlist_count": products.count(),
        "page_title": "My Wishlist — AuraStore",
    }
    return render(request, "catalog/wishlist.html", context)
