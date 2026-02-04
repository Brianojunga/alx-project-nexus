from django.db import models
from accounts.models import Vendor

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=20)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='categories')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["vendor", "name"],
                name="unique_category_per_vendor"
            )
        ]

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=False, blank=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='products')
    photo = models.ImageField(upload_to='product_photos/', null=True, blank=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    quantity = models.PositiveIntegerField(default=1, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name