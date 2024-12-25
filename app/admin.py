from django.contrib import admin
from .models import Lead, Order, Project, Quote  # No need to add 'app'


# Register your models here.
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "amount", "date")
    list_filter = ("status", "date")
    search_fields = ("id", "status")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "window_style", "status")
    list_filter = ("status",)
    search_fields = ("window_style",)


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "created_at")
    search_fields = ("name", "email")


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "email",
        "phone",
        "service",
        "status",
        "created_at",
        "is_active",
    )  # Includes all necessary fields
    list_filter = (
        "status",
        "service",
        "created_at",
    )  # Added 'service' for filtering by type of service
    search_fields = ("name", "email", "phone", "service")  # Remains unchanged
