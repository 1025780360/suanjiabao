from django.db import models

from base.models import TenantOwnedModel


class Bom(TenantOwnedModel):
    style = models.ForeignKey("styles.Style", on_delete=models.CASCADE, related_name="boms")
    version = models.CharField(max_length=40, default="v1")
    description = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("style", "version")
        ordering = ["style_id", "-created_at"]

    def __str__(self):
        return f"{self.style} {self.version}"


class BomItem(TenantOwnedModel):
    bom = models.ForeignKey(Bom, on_delete=models.CASCADE, related_name="items")
    material = models.ForeignKey("materials.Material", on_delete=models.PROTECT)
    color = models.ForeignKey("styles.StyleColor", on_delete=models.SET_NULL, null=True, blank=True)
    size = models.ForeignKey("styles.StyleSize", on_delete=models.SET_NULL, null=True, blank=True)
    usage = models.DecimalField(max_digits=12, decimal_places=4)
    loss_rate = models.DecimalField(max_digits=6, decimal_places=4, default=0)
    remark = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["bom_id", "id"]

    @property
    def total_usage(self):
        return self.usage * (1 + self.loss_rate)

    def __str__(self):
        return f"{self.bom} - {self.material}"

# Create your models here.
