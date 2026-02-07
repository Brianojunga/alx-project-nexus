from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model

from products.models import Product
from accounts.models import Vendor

User = get_user_model()


# Create your models here.
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='carts')
    session_key = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    is_active = models.BooleanField(default=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='vendor')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def compute_total(self):
        total = sum(item.total for item in self.items.select_related('product').all())
        return Decimal(total).quantize(Decimal('0.01'))

    def __str__(self):
        if self.user:
            return f"Cart (User: {self.user})"
        return f"Cart (Guest: {self.session_key})"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('cart', 'product')

    @property
    def total(self):
        price = Decimal(self.product.price)
        discount = Decimal(self.product.discount) / Decimal('100') if self.product.discount else Decimal('0')
        total = price * (Decimal('1') - discount) * Decimal(self.quantity)
        return total.quantize(Decimal('0.01'))

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


