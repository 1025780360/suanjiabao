from django.contrib import admin

from .models import Style, StyleColor, StyleSize


class StyleColorInline(admin.TabularInline):
    model = StyleColor
    extra = 0


class StyleSizeInline(admin.TabularInline):
    model = StyleSize
    extra = 0


@admin.register(Style)
class StyleAdmin(admin.ModelAdmin):
    list_display = ("style_no", "name", "tenant", "season", "category", "is_active", "created_at")
    search_fields = ("style_no", "name")
    list_filter = ("is_active", "season", "category")
    inlines = [StyleColorInline, StyleSizeInline]

# Register your models here.
