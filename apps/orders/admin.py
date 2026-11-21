from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ("product",)
    extra = 0
    readonly_fields = ("get_cost",)

    def get_cost(self, instance):
        if instance.pk:
            return f"${instance.get_cost():.2f}"
        return "-"

    get_cost.short_description = "Cost"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "full_name",
        "email",
        "status",
        "paid",
        "order_total_display",
        "created_at",
    )
    list_filter = ("status", "paid", "created_at")
    search_fields = ("order_number", "first_name", "last_name", "email", "phone")
    readonly_fields = (
        "order_number",
        "created_at",
        "updated_at",
        "order_total_display",
    )
    inlines = (OrderItemInline,)
    actions = ("mark_as_paid", "mark_as_shipped", "mark_as_delivered")

    def order_total_display(self, obj):
        return f"${obj.get_total_cost():.2f}"

    order_total_display.short_description = "Total"

    @admin.action(description="Mark selected orders as Paid")
    def mark_as_paid(self, request, queryset):
        rows_updated = queryset.update(paid=True, status=Order.STATUS_PAID)
        self.message_user(
            request, f"{rows_updated} order(s) successfully marked as paid."
        )

    @admin.action(description="Mark selected orders as Shipped")
    def mark_as_shipped(self, request, queryset):
        rows_updated = queryset.update(status=Order.STATUS_SHIPPED)
        self.message_user(
            request, f"{rows_updated} order(s) successfully marked as shipped."
        )

    @admin.action(description="Mark selected orders as Delivered")
    def mark_as_delivered(self, request, queryset):
        rows_updated = queryset.update(status=Order.STATUS_DELIVERED)
        self.message_user(
            request, f"{rows_updated} order(s) successfully marked as delivered."
        )
