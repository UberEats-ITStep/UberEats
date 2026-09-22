from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class BiteUpUserAdmin(UserAdmin):
    ordering = ("email",)
    list_display = (
        "email",
        "username",
        "role",
        "is_verified",
        "is_staff",
        "is_active",
    )
    list_filter = ("role", "is_verified", "is_staff", "is_active")
    search_fields = ("email", "username", "firebase_uid")
    readonly_fields = ("created_at",)
    fieldsets = UserAdmin.fieldsets + (
        (
            "BiteUp account",
            {"fields": ("role", "is_verified", "firebase_uid", "created_at")},
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("BiteUp account", {"fields": ("email", "role", "is_verified")}),
    )
