from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Vendor
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


@receiver([post_save, post_delete], sender=Vendor)
def invalidate_vendor_list_cache(sender, instance, **kwargs):
    try:
        cache.delete('vendors_approved')
        cache.delete('vendors_pending')
        logger.info('Cleared vendors_approved and vendors_pending cache')
    except Exception as e:
        logger.warning(f'Failed to clear vendor list caches: {e}')
