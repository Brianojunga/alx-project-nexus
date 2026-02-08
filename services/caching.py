from django.core.cache import cache
from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)

DEFAULT_CACHE_TIMEOUT = 60 * 15


def get_cache_key(what_to_cache, vendor_slug):
    """Generate a cache key for vendor-specific data"""
    return f"{what_to_cache}_list:{vendor_slug}"


def clear_vendor_cache(vendor_slug, what_to_cache):
    """Clear cache for a specific vendor and data type"""
    try:
        cache_key = get_cache_key(what_to_cache, vendor_slug)
        cache.delete(cache_key)
        logger.info(f"Cleared cache: {cache_key}")
    except Exception as e:
        logger.warning(f"Failed to clear cache: {str(e)}")


def caching(viewset_instance, request, what_to_cache, *args, timeout=DEFAULT_CACHE_TIMEOUT, **kwargs):
    """
    Cache the list response for a viewset.
    """
    from rest_framework import viewsets
    vendor_slug = viewset_instance.kwargs.get("vendor_slug")
    
    if not vendor_slug:
        # If no vendor_slug, don't cache - just return normal list response
        return viewsets.ModelViewSet.list(viewset_instance, request, *args, **kwargs)
    
    cache_key = get_cache_key(what_to_cache, vendor_slug)
    
    # Try to get from cache
    try:
        cached = cache.get(cache_key)
        if cached is not None:
            logger.debug(f"Cache hit: {cache_key}")
            return Response(cached)
    except Exception as e:
        logger.warning(f"Cache retrieval failed: {str(e)}")
    
    # Cache miss - get fresh data
    response = viewsets.ModelViewSet.list(viewset_instance, request, *args, **kwargs)
    
    # Store in cache
    try:
        if response.status_code == 200:
            cache.set(cache_key, response.data, timeout)
            logger.debug(f"Cache set: {cache_key}")
    except Exception as e:
        logger.warning(f"Cache storage failed: {str(e)}")
    
    return response