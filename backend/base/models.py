from django.conf import settings
from django.db import models


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TenantOwnedModel(TimestampedModel):
    tenant = models.ForeignKey("accounts.Tenant", verbose_name="企业/档口", on_delete=models.CASCADE)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="创建用户",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_%(class)s_set",
    )

    class Meta:
        abstract = True


class Unit(TimestampedModel):
    name = models.CharField(max_length=40)
    code = models.CharField(max_length=20, unique=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return self.code


class Currency(TimestampedModel):
    name = models.CharField(max_length=40)
    code = models.CharField(max_length=10, unique=True)
    exchange_rate_to_cny = models.DecimalField(max_digits=12, decimal_places=4, default=1)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return self.code


class TaxRate(TimestampedModel):
    name = models.CharField(max_length=80)
    rate = models.DecimalField(max_digits=6, decimal_places=4)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} {self.rate}"

# Create your models here.
