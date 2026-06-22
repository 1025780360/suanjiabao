from django.db import models

from base.models import TenantOwnedModel


class Process(TenantOwnedModel):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=60, blank=True)
    supplier = models.ForeignKey("suppliers.Supplier", on_delete=models.SET_NULL, null=True, blank=True)
    unit = models.ForeignKey("base.Unit", on_delete=models.PROTECT)
    default_unit_price = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    remark = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("tenant", "code")
        ordering = ["name"]

    def __str__(self):
        return self.name

# Create your models here.
