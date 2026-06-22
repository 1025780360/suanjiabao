from django.db import models

from base.models import TenantOwnedModel


class Supplier(TenantOwnedModel):
    class SupplierType(models.TextChoices):
        FABRIC = "fabric", "Fabric"
        ACCESSORY = "accessory", "Accessory"
        PROCESSING = "processing", "Processing"
        PACKAGING = "packaging", "Packaging"
        LOGISTICS = "logistics", "Logistics"
        OTHER = "other", "Other"

    name = models.CharField(max_length=120)
    supplier_type = models.CharField(max_length=30, choices=SupplierType.choices, default=SupplierType.OTHER)
    contact_name = models.CharField(max_length=80, blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=255, blank=True)
    remark = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("tenant", "name")
        ordering = ["name"]

    def __str__(self):
        return self.name

# Create your models here.
