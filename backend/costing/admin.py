from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html, format_html_join

from .models import AiChatMessage, AiProviderSetting, CostItem, CostSheet, QuickCategory, QuickStyle, Quote


class CostItemInline(admin.TabularInline):
    model = CostItem
    extra = 0


@admin.register(CostSheet)
class CostSheetAdmin(admin.ModelAdmin):
    list_display = ("name", "style", "tenant", "total_cost", "quote_price", "status", "created_at")
    search_fields = ("name", "style__style_no", "style__name")
    list_filter = ("status",)
    inlines = [CostItemInline]


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ("quote_no", "tenant", "customer_name", "quantity", "unit_price", "total_amount", "created_at")
    search_fields = ("quote_no", "customer_name")


@admin.register(QuickCategory)
class QuickCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "key", "tenant", "created_by", "fabric_count", "process_count", "created_at")
    search_fields = ("name", "key", "created_by__username")
    list_filter = ("tenant", "created_by")

    @admin.display(description="面料项")
    def fabric_count(self, obj):
        return len(obj.fabrics or [])

    @admin.display(description="工序项")
    def process_count(self, obj):
        return len(obj.processes or [])


@admin.register(QuickStyle)
class QuickStyleAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "tenant",
        "user_link",
        "quote_price",
        "total_cost",
        "profit",
        "fabric_count",
        "process_count",
        "updated_at",
    )
    search_fields = (
        "name",
        "category",
        "created_by__username",
        "created_by__display_name",
        "created_by__shop_name",
    )
    list_filter = ("tenant", "created_by", "category")
    readonly_fields = (
        "image_preview",
        "fabric_details",
        "process_details",
        "summary_details",
        "tenant",
        "created_by",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        ("1. 款式基础信息", {"fields": ("name", "category", "tenant", "created_by", "image_preview")}),
        ("2. 报价结果", {"fields": ("summary_details",)}),
        ("3. 成本明细", {"fields": ("fabric_details", "process_details", "accessory_pack", "expected_profit")}),
        ("4. 原始数据", {"fields": ("image_data", "fabrics", "processes"), "classes": ("collapse",)}),
        ("5. 创建和更新时间", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    @admin.display(description="用户")
    def user_link(self, obj):
        if not obj.created_by_id:
            return "-"
        url = reverse("admin:accounts_user_change", args=[obj.created_by_id])
        label = obj.created_by.display_name or obj.created_by.username
        return format_html('<a href="{}">{}</a>', url, label)

    @admin.display(description="图片预览")
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width:220px;max-height:220px;border-radius:12px;border:1px solid #ddd;" />',
                obj.image.url,
            )
        if obj.image_data:
            return format_html(
                '<img src="{}" style="max-width:220px;max-height:220px;border-radius:12px;border:1px solid #ddd;" />',
                obj.image_data,
            )
        return "无图片"

    @admin.display(description="面料明细")
    def fabric_details(self, obj):
        rows = []
        total = 0
        for item in obj.fabrics or []:
            name = item.get("name", "未命名面料")
            price = float(item.get("price") or 0)
            usage = float(item.get("usage") or 0)
            amount = price * usage
            total += amount
            rows.append((name, f"¥{price:.2f}", f"{usage:.3f}m", f"¥{amount:.2f}"))
        return format_html(
            '<table style="border-collapse:collapse;min-width:520px;background:#fff;">'
            '<thead><tr>'
            '<th style="border:1px solid #ddd;padding:8px;background:#f6f7f8;">面料名称</th>'
            '<th style="border:1px solid #ddd;padding:8px;background:#f6f7f8;">单价</th>'
            '<th style="border:1px solid #ddd;padding:8px;background:#f6f7f8;">单件用量</th>'
            '<th style="border:1px solid #ddd;padding:8px;background:#f6f7f8;">金额</th>'
            '</tr></thead>'
            '<tbody>{}</tbody>'
            '<tfoot><tr><th colspan="3" style="border:1px solid #ddd;padding:8px;text-align:right;background:#fff8e1;">面料合计</th>'
            '<th style="border:1px solid #ddd;padding:8px;background:#fff8e1;">¥{:.2f}</th></tr></tfoot></table>',
            format_html_join(
                "",
                '<tr><td style="border:1px solid #ddd;padding:8px;">{}</td>'
                '<td style="border:1px solid #ddd;padding:8px;">{}</td>'
                '<td style="border:1px solid #ddd;padding:8px;">{}</td>'
                '<td style="border:1px solid #ddd;padding:8px;">{}</td></tr>',
                rows,
            )
            if rows
            else format_html('<tr><td colspan="4">无面料明细</td></tr>'),
            total,
        )

    @admin.display(description="工序明细")
    def process_details(self, obj):
        rows = []
        total = 0
        for item in obj.processes or []:
            name = item.get("name", "未命名工序")
            fee = float(item.get("fee") or 0)
            total += fee
            rows.append((name, f"¥{fee:.2f}"))
        return format_html(
            '<table style="border-collapse:collapse;min-width:360px;background:#fff;">'
            '<thead><tr>'
            '<th style="border:1px solid #ddd;padding:8px;background:#f6f7f8;">工序名称</th>'
            '<th style="border:1px solid #ddd;padding:8px;background:#f6f7f8;">加工费用</th>'
            '</tr></thead>'
            '<tbody>{}</tbody>'
            '<tfoot><tr><th style="border:1px solid #ddd;padding:8px;text-align:right;background:#fff8e1;">工序合计</th>'
            '<th style="border:1px solid #ddd;padding:8px;background:#fff8e1;">¥{:.2f}</th></tr></tfoot></table>',
            format_html_join(
                "",
                '<tr><td style="border:1px solid #ddd;padding:8px;">{}</td>'
                '<td style="border:1px solid #ddd;padding:8px;">{}</td></tr>',
                rows,
            )
            if rows
            else format_html('<tr><td colspan="2">无工序明细</td></tr>'),
            total,
        )

    @admin.display(description="报价摘要")
    def summary_details(self, obj):
        return format_html(
            '<div style="display:grid;grid-template-columns:repeat(2,minmax(0,180px));gap:12px;max-width:420px;">'
            '<div style="padding:12px;border:1px solid #ddd;border-radius:8px;background:#f8fbff;"><b>建议报价</b><br><span style="font-size:22px;">¥{}</span></div>'
            '<div style="padding:12px;border:1px solid #ddd;border-radius:8px;background:#fff8e1;"><b>最低接单价</b><br><span style="font-size:22px;">¥{}</span></div>'
            '<div style="padding:12px;border:1px solid #ddd;border-radius:8px;background:#f6f7f8;"><b>单件成本</b><br><span style="font-size:22px;">¥{}</span></div>'
            '<div style="padding:12px;border:1px solid #ddd;border-radius:8px;background:#f3fff1;"><b>单件利润</b><br><span style="font-size:22px;">¥{}</span></div>'
            '</div>',
            obj.quote_price,
            obj.minimum_price,
            obj.total_cost,
            obj.profit,
        )

    @admin.display(description="面料项")
    def fabric_count(self, obj):
        return len(obj.fabrics or [])

    @admin.display(description="工序项")
    def process_count(self, obj):
        return len(obj.processes or [])


@admin.register(AiProviderSetting)
class AiProviderSettingAdmin(admin.ModelAdmin):
    list_display = ("name", "provider", "model", "base_url", "key_status", "is_active", "updated_at")
    list_filter = ("provider", "is_active")
    search_fields = ("name", "provider", "model", "base_url", "remark")
    fieldsets = (
        ("DeepSeek 配置", {"fields": ("name", "provider", "is_active", "api_key", "base_url", "model")}),
        ("备注", {"fields": ("remark",)}),
    )

    @admin.display(description="密钥状态")
    def key_status(self, obj):
        if not obj.api_key:
            return "未填写"
        return f"已填写（尾号 {obj.api_key[-4:]}）"


@admin.register(AiChatMessage)
class AiChatMessageAdmin(admin.ModelAdmin):
    list_display = ("created_at", "tenant", "created_by", "role", "intent", "need_more_info", "short_content")
    list_filter = ("tenant", "created_by", "role", "intent", "need_more_info")
    search_fields = ("content", "created_by__username", "created_by__display_name")
    readonly_fields = ("tenant", "created_by", "created_at", "updated_at")

    @admin.display(description="消息内容")
    def short_content(self, obj):
        return obj.content[:60]
