from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Order
from services.caching import clear_vendor_cache
import logging

logger = logging.getLogger(__name__)


@receiver([post_save, post_delete], sender=Order)
def invalidate_order_cache(sender, instance, **kwargs):
    try:
        vendor = getattr(instance, 'vendor', None)
        if vendor is None:
            return
        clear_vendor_cache(vendor.slug, 'order')
        logger.info(f"Invalidated order cache for vendor={vendor.slug}")
    except Exception as e:
        logger.warning(f"Failed to invalidate order cache: {e}")
