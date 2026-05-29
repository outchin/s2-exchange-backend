"""
Django signals for cache invalidation and WebSocket broadcasting.

When exchange rates are updated in the database:
1. Invalidate Redis cache
2. Broadcast update to all WebSocket clients via Redis pub/sub
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import ExchangeRate, ExchangeRateTier
from .cache import invalidate_exchange_rates_cache, get_cached_exchange_rates


@receiver(post_save, sender=ExchangeRate)
@receiver(post_delete, sender=ExchangeRate)
def exchange_rate_changed(sender, instance, **kwargs):
    """
    When ExchangeRate is saved or deleted:
    1. Invalidate cache
    2. Broadcast updated rates to all WebSocket clients
    """
    # Invalidate cache
    invalidate_exchange_rates_cache()

    # Get fresh rates from cache (will fetch from DB and cache)
    rates = get_cached_exchange_rates()

    # Broadcast to all WebSocket clients via Redis pub/sub
    channel_layer = get_channel_layer()
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            'exchange_rates',
            {
                'type': 'rates_update',
                'rates': rates
            }
        )


@receiver(post_save, sender=ExchangeRateTier)
@receiver(post_delete, sender=ExchangeRateTier)
def exchange_rate_tier_changed(sender, instance, **kwargs):
    """
    When ExchangeRateTier is saved or deleted:
    1. Invalidate cache
    2. Broadcast updated rates to all WebSocket clients
    """
    # Invalidate cache
    invalidate_exchange_rates_cache()

    # Get fresh rates from cache (will fetch from DB and cache)
    rates = get_cached_exchange_rates()

    # Broadcast to all WebSocket clients via Redis pub/sub
    channel_layer = get_channel_layer()
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            'exchange_rates',
            {
                'type': 'rates_update',
                'rates': rates
            }
        )
