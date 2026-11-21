from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from .models import Category, Product


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
        return context
