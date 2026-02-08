from django.db import models
from django.contrib.auth import get_user_model
import uuid
from accounts.models import Vendor
from products.models import Product


User = get_user_model()
# Create your models here.
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="orders")
    session_key = models.CharField(max_length=100, null=True, blank=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name="orders")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        indexes = [
            models.Index(fields=["vendor", "status"]),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["user", "vendor"],
                condition=models.Q(status="pending"),
                name="unique_pending_order_per_user_vendor",
            ),
            models.UniqueConstraint(
                fields=["session_key", "vendor"],
                condition=models.Q(status="pending"),
                name="unique_pending_order_per_session_vendor",
            ),
        ]

    def __str__(self):
        return f"Order {self.id} ({self.status})"
    

class OrderItem(models.Model):
    order = models.ForeignKey( Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    total = models.DecimalField(max_digits=12, decimal_places=2)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    
    def save(self, *args, **kwargs):
        self.total = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
