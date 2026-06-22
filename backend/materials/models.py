from django.db import models

from base.models import TenantOwnedModel


class MaterialCategory(TenantOwnedModel):
    name = models.CharField(max_length=80)
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ("tenant", "name")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Material(TenantOwnedModel):
    class MaterialType(models.TextChoices):
        FABRIC = "fabric", "Fabric"
        ACCESSORY = "accessory", "Accessory"
        PACKAGING = "packaging", "Packaging"
        OTHER = "other", "Other"

    name = models.CharField(max_length=120)
    code = models.CharField(max_length=60, blank=True)
    material_type = models.CharField(max_length=30, choices=MaterialType.choices)
    category = models.ForeignKey(MaterialCategory, on_delete=models.SET_NULL, null=True, blank=True)
    supplier = models.ForeignKey("suppliers.Supplier", on_delete=models.SET_NULL, null=True, blank=True)
    unit = models.ForeignKey("base.Unit", on_delete=models.PROTECT)
    default_loss_rate = models.DecimalField(max_digits=6, decimal_places=4, default=0)
    remark = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("tenant", "code")
        ordering = ["name"]

    def __str__(self):
        return self.name


class MaterialPrice(TenantOwnedModel):
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name="prices")
    supplier = models.ForeignKey("suppliers.Supplier", on_delete=models.SET_NULL, null=True, blank=True)
    currency = models.ForeignKey("base.Currency", on_delete=models.PROTECT)
    unit_price = models.DecimalField(max_digits=12, decimal_places=4)
    min_quantity = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    effective_date = models.DateField()
    remark = models.TextField(blank=True)

    class Meta:
        ordering = ["material_id", "-effective_date", "min_quantity"]

    def __str__(self):
        return f"{self.material} {self.unit_price}"

# Create your models here.
