from django.contrib import admin

from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_no", "tenant", "style", "customer_name", "quantity", "unit_price", "status", "delivery_date")
    search_fields = ("order_no", "customer_name", "style__style_no", "style__name")
    list_filter = ("status",)

# Register your models here.
