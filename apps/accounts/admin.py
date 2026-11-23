from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Address, CustomUser


class AddressInline(admin.StackedInline):
    model = Address
    extra = 0


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("username", "email", "phone", "is_staff", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        ("Additional Info", {"fields": ("phone", "birth_date", "profile_picture")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Additional Info", {"fields": ("phone", "birth_date", "profile_picture")}),
    )
    inlines = (AddressInline,)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "city", "country", "is_default", "created_at")
    list_filter = ("is_default", "country", "created_at")
    search_fields = ("user__username", "full_name", "address", "city", "postal_code")
