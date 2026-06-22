from django.contrib import admin

from .models import Process


@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "tenant", "supplier", "unit", "default_unit_price", "is_active")
    search_fields = ("name", "code")
    list_filter = ("is_active",)

# Register your models here.
