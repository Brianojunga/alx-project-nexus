from django.db import models
from accounts.models import Vendor
from orders.models import Order

# Create your models here.
class VendorSubAccount(models.Model):
    vendor = models.OneToOneField(Vendor, on_delete=models.CASCADE, related_name="paystack_account")
    subaccount_code = models.CharField(max_length=100, unique=True)
    percentage_charge = models.DecimalField(max_digits=10, decimal_places=2, default=98.50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vendor.user.email} - {self.subaccount_code}"
    

class Payment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    channel=models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reference} ({self.status})"