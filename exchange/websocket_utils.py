from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def broadcast_rate_update(rates_data):
    """
    Broadcast exchange rate updates to all connected WebSocket clients.

    Args:
        rates_data: List of rate dictionaries to broadcast
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'exchange_rates',
        {
            'type': 'rates_update',
            'rates': rates_data
        }
    )
