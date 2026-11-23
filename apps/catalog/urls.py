from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.ProductListView.as_view(), name="product_list"),
    path(
        "category/<slug:category_slug>/",
        views.ProductListView.as_view(),
        name="product_list_by_category",
    ),
    path("wishlist/", views.wishlist_detail, name="wishlist_detail"),
    path(
        "wishlist/toggle/<int:product_id>/",
        views.wishlist_toggle,
        name="wishlist_toggle",
    ),
    path("<slug:slug>/review/", views.add_review, name="add_review"),
    path("<slug:slug>/", views.ProductDetailView.as_view(), name="product_detail"),
]
