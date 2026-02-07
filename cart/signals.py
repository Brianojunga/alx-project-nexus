from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import CartItem
from services.caching import clear_vendor_cache
import logging

logger = logging.getLogger(__name__)


@receiver([post_save, post_delete], sender=CartItem)
def update_cart_total(sender, instance, **kwargs):
    cart = instance.cart
    cart.total = cart.compute_total()
    cart.save(update_fields=['total', 'updated_at'])

    
    # invalidate cart list cache for vendor
    try:
        vendor = getattr(cart, 'vendor', None)
        if vendor:
            clear_vendor_cache(vendor.slug, 'cart')
            logger.info(f"Cleared cart cache for vendor={vendor.slug}")
    except Exception as e:
        logger.warning(f"Failed to clear cart cache: {e}")