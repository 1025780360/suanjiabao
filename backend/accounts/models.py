from django.contrib.auth.models import AbstractUser
from django.db import models


class Tenant(models.Model):
    class Plan(models.TextChoices):
        FREE = "free", "免费版"
        PRO = "pro", "专业版"
        ULTIMATE = "ultimate", "旗舰版"

    name = models.CharField("企业/档口名称", max_length=120)
    contact_name = models.CharField("联系人", max_length=80, blank=True)
    contact_phone = models.CharField("联系电话", max_length=30, blank=True)
    is_active = models.BooleanField("是否启用", default=True)
    plan = models.CharField("会员等级", max_length=20, choices=Plan.choices, default=Plan.FREE)
    trial_ends_at = models.DateTimeField("试用到期时间", null=True, blank=True)
    # 配额（0=无限）
    style_quota = models.IntegerField("款式上限", default=5)
    style_extra = models.IntegerField("款式扩容", default=0)
    ai_daily_quota = models.IntegerField("AI每日次数", default=5)
    ai_extra = models.IntegerField("AI每日扩容", default=0)
    template_quota = models.IntegerField("模板上限", default=0)
    template_extra = models.IntegerField("模板扩容", default=0)
    can_batch = models.BooleanField("批量报价", default=False)
    can_compare = models.BooleanField("款式对比", default=False)
    can_export = models.BooleanField("导出Excel", default=False)
    can_ai_price = models.BooleanField("AI智能定价", default=False)
    team_size = models.IntegerField("团队人数上限", default=1)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "企业/档口"
        verbose_name_plural = "企业/档口"

    def __str__(self):
        return self.name

    @property
    def total_style_quota(self):
        if self.style_quota == 0: return 0  # 无限
        return self.style_quota + self.style_extra

    @property
    def total_ai_quota(self):
        if self.ai_daily_quota == 0: return 0  # 无限
        return self.ai_daily_quota + self.ai_extra

    @property
    def total_template_quota(self):
        if self.template_quota == 0: return 0
        return self.template_quota + self.template_extra

    def apply_plan(self, plan: str):
        """根据会员等级设置配额"""
        plans = {
            "free": dict(style_quota=5, ai_daily_quota=5, template_quota=0,
                         can_batch=False, can_compare=False, can_export=False,
                         can_ai_price=False, team_size=1),
            "pro": dict(style_quota=100, ai_daily_quota=100, template_quota=3,
                        can_batch=True, can_compare=False, can_export=False,
                        can_ai_price=False, team_size=1),
            "ultimate": dict(style_quota=200, ai_daily_quota=0, template_quota=0,
                             can_batch=True, can_compare=True, can_export=True,
                             can_ai_price=True, team_size=3),
        }
        cfg = plans.get(plan, plans["free"])
        for k, v in cfg.items():
            setattr(self, k, v)
        self.plan = plan
        self.style_extra = 0
        self.ai_extra = 0
        self.template_extra = 0


class Subscription(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "有效"
        EXPIRED = "expired", "已过期"
        CANCELLED = "cancelled", "已取消"

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="subscriptions")
    plan = models.CharField("会员等级", max_length=20, choices=Tenant.Plan.choices)
    status = models.CharField("状态", max_length=20, choices=Status.choices, default=Status.ACTIVE)
    amount = models.DecimalField("金额", max_digits=10, decimal_places=2)
    started_at = models.DateTimeField("生效时间", auto_now_add=True)
    expires_at = models.DateTimeField("到期时间", null=True, blank=True)
    is_extension = models.BooleanField("扩容包", default=False)
    extension_type = models.CharField("扩容类型", max_length=30, blank=True)
    extension_amount = models.IntegerField("扩容数量", default=0)

    class Meta:
        ordering = ["-started_at"]
        verbose_name = "订阅记录"
        verbose_name_plural = "订阅记录"


class User(AbstractUser):
    phone = models.CharField("联系电话", max_length=30, blank=True)
    display_name = models.CharField("用户称呼", max_length=80, blank=True)
    shop_name = models.CharField("店铺名称", max_length=120, blank=True)
    shop_location = models.CharField("店铺位置", max_length=120, blank=True)

    class Meta:
        verbose_name = "用户账号"
        verbose_name_plural = "用户账号"


class Membership(models.Model):
    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Admin"
        STAFF = "staff", "Staff"
        VIEWER = "viewer", "Viewer"

    tenant = models.ForeignKey(Tenant, verbose_name="企业/档口", on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(User, verbose_name="用户账号", on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField("角色", max_length=20, choices=Role.choices, default=Role.STAFF)
    is_active = models.BooleanField("是否启用", default=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        unique_together = ("tenant", "user")
        ordering = ["tenant_id", "user_id"]
        verbose_name = "企业成员"
        verbose_name_plural = "企业成员"

    def __str__(self):
        return f"{self.tenant} - {self.user} ({self.role})"


class UserQuota(models.Model):
    """每日用量追踪"""
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE, related_name="daily_quotas")
    date = models.DateField("日期", auto_now_add=True)
    ai_used = models.IntegerField("AI已用次数", default=0)

    class Meta:
        unique_together = ("membership", "date")
        verbose_name = "每日用量"
        verbose_name_plural = "每日用量"


class SupportRoom(models.Model):
    """客服聊天室"""
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name="support_room")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="support_rooms")
    is_active = models.BooleanField("活跃", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "客服聊天室"
        verbose_name_plural = "客服聊天室"


class SupportMessage(models.Model):
    """客服消息"""
    room = models.ForeignKey(SupportRoom, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField("内容")
    is_staff = models.BooleanField("客服发送", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "客服消息"
        verbose_name_plural = "客服消息"


class PaymentMethod(models.Model):
    """管理员配置的收款方式"""
    name = models.CharField("方式名称", max_length=80)
    qr_image = models.ImageField("收款码图片", upload_to="payment_qr/", blank=True)
    qr_image_data = models.TextField("收款码图片数据", blank=True)
    instructions = models.TextField("付款说明", blank=True)
    is_active = models.BooleanField("启用", default=True)

    class Meta:
        verbose_name = "收款方式"
        verbose_name_plural = "收款方式"

    def __str__(self):
        return self.name


class PaymentRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "待确认"
        CONFIRMED = "confirmed", "已到账"
        REJECTED = "rejected", "已拒绝"

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="payment_requests")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="payment_requests")
    plan = models.CharField("目标会员", max_length=20, choices=Tenant.Plan.choices)
    amount = models.DecimalField("金额", max_digits=10, decimal_places=2)
    extension_type = models.CharField("扩容类型", max_length=30, blank=True)
    extension_amount = models.IntegerField("扩容数量", default=0)
    status = models.CharField("状态", max_length=20, choices=Status.choices, default=Status.PENDING)
    admin_note = models.CharField("管理员备注", max_length=255, blank=True)
    created_at = models.DateTimeField("申请时间", auto_now_add=True)
    confirmed_at = models.DateTimeField("确认时间", null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "付款申请"
        verbose_name_plural = "付款申请"

    def confirm(self):
        """确认到账，执行升级"""
        self.status = self.Status.CONFIRMED
        from django.utils import timezone
        from datetime import timedelta
        self.confirmed_at = timezone.now()
        if self.extension_type:
            # 扩容
            if self.extension_type == "style":
                self.tenant.style_extra += self.extension_amount
            elif self.extension_type == "ai":
                self.tenant.ai_extra += self.extension_amount
            elif self.extension_type == "template":
                self.tenant.template_extra += self.extension_amount
            Subscription.objects.create(
                tenant=self.tenant, plan=self.tenant.plan, amount=self.amount,
                is_extension=True, extension_type=self.extension_type,
                extension_amount=self.extension_amount,
            )
        else:
            # 升级套餐：根据 admin_note 判断计费周期计算到期时间
            billing = self.admin_note or "月付"
            days = {"月付": 30, "季付": 90, "年付": 365}.get(billing, 30)
            self.tenant.apply_plan(self.plan)
            self.tenant.trial_ends_at = timezone.now() + timedelta(days=days)
            Subscription.objects.create(
                tenant=self.tenant, plan=self.plan, amount=self.amount,
                expires_at=self.tenant.trial_ends_at,
            )
        self.tenant.save()
        self.save()

# Create your models here.
