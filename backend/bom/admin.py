from django.contrib import admin

from .models import Bom, BomItem


class BomItemInline(admin.TabularInline):
    model = BomItem
    extra = 0


@admin.register(Bom)
class BomAdmin(admin.ModelAdmin):
    list_display = ("style", "version", "tenant", "is_active", "created_at")
    search_fields = ("style__style_no", "style__name", "version")
    list_filter = ("is_active",)
    inlines = [BomItemInline]

# Register your models here.
