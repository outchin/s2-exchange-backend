"""
Redis caching utilities for S2Exchange.

Architecture:
- Exchange rates are cached in Redis for fast reads
- Cache is invalidated when rates are updated in database
- WebSocket broadcasts cache updates to all connected clients
"""

from django.core.cache import cache
from django.conf import settings
from .models import ExchangeRate


CACHE_KEY_ALL_RATES = 's2exchange:rates:all'


def get_cached_exchange_rates():
    """
    Get exchange rates from cache. If not in cache, fetch from DB and cache it.

    Returns:
        list: List of exchange rate dictionaries
    """
    cached_rates = cache.get(CACHE_KEY_ALL_RATES)

    if cached_rates is not None:
        return cached_rates

    # Not in cache, fetch from database
    rates = ExchangeRate.objects.filter(is_active=True).select_related('currency').prefetch_related('tiers').order_by('currency__sort_order')
    rates_data = [rate.to_api_dict() for rate in rates]

    # Cache for TTL duration
    cache.set(
        CACHE_KEY_ALL_RATES,
        rates_data,
        timeout=settings.CACHE_TTL_EXCHANGE_RATES
    )

    return rates_data


def invalidate_exchange_rates_cache():
    """
    Invalidate the exchange rates cache.
    Called when rates are updated in the database.
    """
    cache.delete(CACHE_KEY_ALL_RATES)


def warm_exchange_rates_cache():
    """
    Preload exchange rates into cache.
    Useful for deployment initialization.
    """
    invalidate_exchange_rates_cache()
    return get_cached_exchange_rates()
