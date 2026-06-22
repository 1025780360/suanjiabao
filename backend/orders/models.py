from django.db import models

from base.models import TenantOwnedModel


class Order(TenantOwnedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        CONFIRMED = "confirmed", "Confirmed"
        PRODUCING = "producing", "Producing"
        SHIPPED = "shipped", "Shipped"
        CLOSED = "closed", "Closed"
        CANCELED = "canceled", "Canceled"

    order_no = models.CharField(max_length=80)
    style = models.ForeignKey("styles.Style", on_delete=models.PROTECT)
    quote = models.ForeignKey("costing.Quote", on_delete=models.SET_NULL, null=True, blank=True)
    customer_name = models.CharField(max_length=120, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    estimated_cost = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    actual_cost = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    delivery_date = models.DateField(null=True, blank=True)
    remark = models.TextField(blank=True)

    class Meta:
        unique_together = ("tenant", "order_no")
        ordering = ["-created_at"]

    @property
    def revenue(self):
        return self.quantity * self.unit_price

    @property
    def estimated_profit(self):
        return self.revenue - self.estimated_cost

    def __str__(self):
        return self.order_no

# Create your models here.
