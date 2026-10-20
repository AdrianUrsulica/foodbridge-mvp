from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class FoodBridgeUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("FoodBridge", {"fields": ("role",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("FoodBridge", {"fields": ("email", "role")}),
    )