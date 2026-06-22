from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.urls import reverse
from django.utils.html import format_html

from .models import Membership, PaymentMethod, PaymentRequest, Subscription, SupportMessage, SupportRoom, Tenant, User, UserQuota


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("档口资料", {"fields": ("display_name", "shop_name", "shop_location", "phone")}),
    )
    list_display = ("username", "display_name", "shop_name", "phone", "style_count", "is_active")
    list_filter = ("is_active", "memberships__tenant")
    search_fields = ("username", "display_name", "shop_name", "phone")

    @admin.display(description="款式数")
    def style_count(self, obj):
        count = obj.created_quickstyle_set.count()
        url = reverse("admin:costing_quickstyle_changelist") + f"?created_by__id__exact={obj.id}"
        return format_html('<a href="{}">{} 款</a>', url, count)


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("name", "plan", "style_quota", "ai_daily_quota", "member_count", "is_active", "created_at")
    list_filter = ("plan", "is_active")
    search_fields = ("name", "contact_name")
    actions = ["set_free", "set_pro", "set_ultimate"]

    @admin.display(description="成员数")
    def member_count(self, obj): return obj.memberships.count()

    @admin.action(description="设为免费版")
    def set_free(self, request, qs):
        for t in qs: t.apply_plan("free"); t.save()

    @admin.action(description="设为专业版")
    def set_pro(self, request, qs):
        for t in qs: t.apply_plan("pro"); t.save()

    @admin.action(description="设为旗舰版")
    def set_ultimate(self, request, qs):
        for t in qs: t.apply_plan("ultimate"); t.save()


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("tenant", "user", "role", "is_active", "created_at")
    search_fields = ("tenant__name", "user__username")
    list_filter = ("role", "is_active")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("tenant", "plan", "amount", "status", "started_at")
    list_filter = ("plan", "status")


@admin.register(UserQuota)
class UserQuotaAdmin(admin.ModelAdmin):
    list_display = ("membership", "date", "ai_used")


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")


@admin.register(PaymentRequest)
class PaymentRequestAdmin(admin.ModelAdmin):
    list_display = ("tenant", "plan", "amount", "status", "created_at")
    list_filter = ("status", "plan")
    actions = ["confirm_payment"]

    @admin.action(description="确认到账并开通")
    def confirm_payment(self, request, qs):
        for pr in qs.filter(status="pending"):
            pr.confirm()


@admin.register(SupportRoom)
class SupportRoomAdmin(admin.ModelAdmin):
    list_display = ("tenant", "user", "is_active", "updated_at")


@admin.register(SupportMessage)
class SupportMessageAdmin(admin.ModelAdmin):
    list_display = ("room", "sender", "is_staff", "created_at")
