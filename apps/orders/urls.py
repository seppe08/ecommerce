from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("create/", views.order_create, name="order_create"),
    path("payment/<str:order_number>/", views.order_payment, name="order_payment"),
    path("cancel/<str:order_number>/", views.order_cancel, name="order_cancel"),
    path("webhook/stripe/", views.stripe_webhook, name="stripe_webhook"),
    path("created/<int:order_id>/", views.order_created, name="order_created"),
    path("my-orders/", views.order_list, name="order_list"),
    path("<str:order_number>/", views.order_detail, name="order_detail"),
]
