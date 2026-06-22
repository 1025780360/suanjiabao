from django.contrib import admin

from .models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "supplier_type", "contact_name", "contact_phone", "is_active")
    search_fields = ("name", "contact_name", "contact_phone")
    list_filter = ("supplier_type", "is_active")

# Register your models here.
