from django.db import models

from base.models import TenantOwnedModel


class Style(TenantOwnedModel):
    style_no = models.CharField(max_length=80)
    name = models.CharField(max_length=120)
    image = models.ImageField(upload_to="styles/", blank=True)
    season = models.CharField(max_length=40, blank=True)
    category = models.CharField(max_length=80, blank=True)
    remark = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("tenant", "style_no")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.style_no} {self.name}"


class StyleColor(TenantOwnedModel):
    style = models.ForeignKey(Style, on_delete=models.CASCADE, related_name="colors")
    name = models.CharField(max_length=80)
    code = models.CharField(max_length=40, blank=True)

    class Meta:
        unique_together = ("style", "name")
        ordering = ["style_id", "name"]

    def __str__(self):
        return self.name


class StyleSize(TenantOwnedModel):
    style = models.ForeignKey(Style, on_delete=models.CASCADE, related_name="sizes")
    name = models.CharField(max_length=40)
    ratio = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("style", "name")
        ordering = ["style_id", "id"]

    def __str__(self):
        return self.name

# Create your models here.
