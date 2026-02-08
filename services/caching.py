from django.core.cache import cache
from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)

DEFAULT_CACHE_TIMEOUT = 60 * 15


def get_cache_key(what_to_cache, vendor_slug):
    return f"{what_to_cache}_list:{vendor_slug}"


def clear_vendor_cache(vendor_slug, what_to_cache):
    try:
        cache_key = get_cache_key(what_to_cache, vendor_slug)
        cache.delete(cache_key)
        logger.info(f"Cleared cache: {cache_key}")
    except Exception as e:
        logger.warning(f"Failed to clear cache: {str(e)}")


def caching(self, request, what_to_cache, timeout=DEFAULT_CACHE_TIMEOUT, *args, **kwargs):
    vendor_slug = self.kwargs.get("vendor_slug")
    if not vendor_slug:
        return super().list(request, *args, **kwargs)
    cache_key = get_cache_key(what_to_cache, vendor_slug)
    
    try:
        cached = cache.get(cache_key)
        if cached is not None:
            logger.debug(f"Cache hit: {cache_key}")
            return Response(cached)
    except Exception as e:
        logger.warning(f"Cache retrieval failed: {str(e)}")
    
    response = super().list(request, *args, **kwargs)
    
    try:
        cache.set(cache_key, response.data, timeout)
        logger.debug(f"Cache set: {cache_key}")
    except Exception as e:
        logger.warning(f"Cache storage failed: {str(e)}")
    
    return response
