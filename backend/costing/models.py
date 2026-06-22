from django.db import models

from base.models import TenantOwnedModel
from base.models import TimestampedModel


class CostSheet(TenantOwnedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        CONFIRMED = "confirmed", "Confirmed"
        ARCHIVED = "archived", "Archived"

    style = models.ForeignKey("styles.Style", on_delete=models.CASCADE, related_name="cost_sheets")
    bom = models.ForeignKey("bom.Bom", on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=120)
    currency = models.ForeignKey("base.Currency", on_delete=models.PROTECT)
    material_cost = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    process_cost = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    packaging_cost = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    logistics_cost = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    other_cost = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    tax_rate = models.DecimalField(max_digits=6, decimal_places=4, default=0)
    profit_rate = models.DecimalField(max_digits=6, decimal_places=4, default=0)
    total_cost = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    quote_price = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "成本单"
        verbose_name_plural = "成本单"

    def __str__(self):
        return self.name


class CostItem(TenantOwnedModel):
    class ItemType(models.TextChoices):
        MATERIAL = "material", "Material"
        PROCESS = "process", "Process"
        PACKAGING = "packaging", "Packaging"
        LOGISTICS = "logistics", "Logistics"
        OTHER = "other", "Other"

    cost_sheet = models.ForeignKey(CostSheet, on_delete=models.CASCADE, related_name="items")
    item_type = models.CharField(max_length=30, choices=ItemType.choices)
    name = models.CharField(max_length=120)
    quantity = models.DecimalField(max_digits=12, decimal_places=4, default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    amount = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    remark = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["cost_sheet_id", "id"]
        verbose_name = "成本明细"
        verbose_name_plural = "成本明细"

    def __str__(self):
        return self.name


class Quote(TenantOwnedModel):
    cost_sheet = models.ForeignKey(CostSheet, on_delete=models.PROTECT, related_name="quotes")
    quote_no = models.CharField(max_length=80)
    customer_name = models.CharField(max_length=120, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=4)
    total_amount = models.DecimalField(max_digits=14, decimal_places=4)
    valid_until = models.DateField(null=True, blank=True)
    remark = models.TextField(blank=True)

    class Meta:
        unique_together = ("tenant", "quote_no")
        ordering = ["-created_at"]
        verbose_name = "报价单"
        verbose_name_plural = "报价单"

    def __str__(self):
        return self.quote_no


class QuickCategory(TenantOwnedModel):
    key = models.CharField("模板标识", max_length=80)
    name = models.CharField("品类名称", max_length=80)
    description = models.CharField("说明", max_length=160, blank=True)
    fabrics = models.JSONField("默认面料", default=list, blank=True)
    processes = models.JSONField("默认工序", default=list, blank=True)

    class Meta:
        unique_together = ("tenant", "created_by", "key")
        ordering = ["created_at"]
        verbose_name = "用户品类模板"
        verbose_name_plural = "用户品类模板"

    def __str__(self):
        return self.name


class QuickStyle(TenantOwnedModel):
    name = models.CharField("款式名称", max_length=120)
    category = models.CharField("品类", max_length=80, blank=True)
    image = models.ImageField("图片文件", upload_to='styles/', blank=True, null=True)
    image_data = models.TextField("图片数据", blank=True)
    fabrics = models.JSONField("面料明细", default=list, blank=True)
    processes = models.JSONField("工序明细", default=list, blank=True)
    accessory_pack = models.DecimalField("辅料包装费", max_digits=12, decimal_places=4, default=0)
    expected_profit = models.DecimalField("期望利润", max_digits=12, decimal_places=4, default=0)
    minimum_price = models.DecimalField("最低接单价", max_digits=12, decimal_places=4, default=0)
    quote_price = models.DecimalField("建议报价", max_digits=12, decimal_places=4, default=0)
    total_cost = models.DecimalField("单件成本", max_digits=12, decimal_places=4, default=0)
    profit = models.DecimalField("单件利润", max_digits=12, decimal_places=4, default=0)

    class Meta:
        unique_together = ("tenant", "created_by", "name")
        ordering = ["-updated_at"]
        verbose_name = "快速算价款式"
        verbose_name_plural = "快速算价款式"

    def __str__(self):
        return self.name


class AiProviderSetting(TimestampedModel):
    name = models.CharField("配置名称", max_length=80, default="DeepSeek")
    provider = models.CharField("服务商", max_length=40, default="deepseek")
    api_key = models.CharField("API 密钥", max_length=255, blank=True)
    base_url = models.URLField("接口地址", default="https://api.deepseek.com")
    model = models.CharField("模型名称", max_length=80, default="deepseek-v4-flash")
    is_active = models.BooleanField("启用", default=True)
    remark = models.CharField("备注", max_length=255, blank=True)

    class Meta:
        ordering = ["-is_active", "-updated_at"]
        verbose_name = "AI 助手配置"
        verbose_name_plural = "AI 助手配置"

    def __str__(self):
        return f"{self.name}（{self.model}）"


class AiChatMessage(TenantOwnedModel):
    class Role(models.TextChoices):
        USER = "user", "用户"
        ASSISTANT = "assistant", "AI 助手"

    role = models.CharField("角色", max_length=20, choices=Role.choices)
    content = models.TextField("消息内容")
    intent = models.CharField("意图", max_length=40, blank=True)
    cost_draft = models.JSONField("款式/成本草稿", default=dict, blank=True)
    calculation = models.JSONField("计算结果", default=dict, blank=True)
    need_more_info = models.BooleanField("是否需要补充信息", default=False)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "AI 聊天记录"
        verbose_name_plural = "AI 聊天记录"

    def __str__(self):
        label = self.get_role_display()
        return f"{label}: {self.content[:30]}"
