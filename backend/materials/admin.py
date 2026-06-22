from django.contrib import admin

from .models import Material, MaterialCategory, MaterialPrice


@admin.register(MaterialCategory)
class MaterialCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "parent")
    search_fields = ("name",)


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "tenant", "material_type", "supplier", "unit", "is_active")
    search_fields = ("name", "code")
    list_filter = ("material_type", "is_active")


@admin.register(MaterialPrice)
class MaterialPriceAdmin(admin.ModelAdmin):
    list_display = ("material", "supplier", "currency", "unit_price", "min_quantity", "effective_date")
    search_fields = ("material__name", "supplier__name")

# Register your models here.
