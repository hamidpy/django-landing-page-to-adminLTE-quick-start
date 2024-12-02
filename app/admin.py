from django.contrib import admin
from app.models import Lead
from .models import Order, Project, Quote, Lead

# Register your models here.
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'amount', 'date')
    list_filter = ('status', 'date')
    search_fields = ('id', 'status')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'window_style', 'status')
    list_filter = ('status',)
    search_fields = ('window_style',)

@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'requested_at')
    search_fields = ('name', 'email', 'phone')

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'service', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'email', 'phone', 'service')

