from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Category, Product
from services.caching import clear_vendor_cache
import logging

logger = logging.getLogger(__name__)

def inavalidate_cache(instance, what_to_cache):
    try:
        vendor = getattr(instance, 'vendor', None)
        if vendor is None:
            return
        clear_vendor_cache(vendor.slug, what_to_cache)
        logger.info(f"Invalidated category cache for vendor={vendor.slug}")
    except Exception as e:
        logger.warning(f"Failed to invalidate category cache: {e}")
    
@receiver([post_save, post_delete], sender=Category)
def invalidate_category_cache(sender, instance, **kwargs):
    return inavalidate_cache(instance, "category")


@receiver([post_save, post_delete], sender=Product)
def invalidate_product_cache(sender, instance, **kwargs):
    return inavalidate_cache(instance, 'product')