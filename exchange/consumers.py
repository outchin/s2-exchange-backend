import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ExchangeRate


class ExchangeRateConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time exchange rate updates.
    Clients connect to this and receive automatic updates when rates change.
    """

    async def connect(self):
        # Join the exchange rates group
        self.room_group_name = 'exchange_rates'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Send initial rates immediately after connection
        rates = await self.get_current_rates()
        await self.send(text_data=json.dumps({
            'type': 'rates_update',
            'rates': rates
        }))

    async def disconnect(self, close_code):
        # Leave the exchange rates group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Handle messages from WebSocket client.
        Clients can request rate refresh.
        """
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')

            if message_type == 'request_rates':
                # Client requested fresh rates
                rates = await self.get_current_rates()
                await self.send(text_data=json.dumps({
                    'type': 'rates_update',
                    'rates': rates
                }))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))

    async def rates_update(self, event):
        """
        Receive message from room group and send to WebSocket.
        This is called when broadcast_rate_update is triggered.
        """
        rates = event['rates']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'rates_update',
            'rates': rates
        }))

    @database_sync_to_async
    def get_current_rates(self):
        """
        Fetch current exchange rates from database.
        """
        rates = ExchangeRate.objects.filter(is_active=True).order_by('order')
        return [
            {
                'id': rate.id,
                'currency': rate.currency,
                'buy_rate': float(rate.buy_rate),
                'sell_rate': float(rate.sell_rate),
                'last_updated': rate.last_updated.isoformat() if rate.last_updated else None,
                'buy_tiers': [
                    {
                        'direction': tier.get('direction', ''),
                        'min_amount': float(tier.get('min_amount', 0)),
                        'max_amount': float(tier.get('max_amount')) if tier.get('max_amount') else None,
                        'rate': float(tier.get('rate', 0)),
                        'label': tier.get('label', '')
                    } for tier in rate.buy_tiers
                ] if rate.buy_tiers else [],
                'sell_tiers': [
                    {
                        'direction': tier.get('direction', ''),
                        'min_amount': float(tier.get('min_amount', 0)),
                        'max_amount': float(tier.get('max_amount')) if tier.get('max_amount') else None,
                        'rate': float(tier.get('rate', 0)),
                        'label': tier.get('label', '')
                    } for tier in rate.sell_tiers
                ] if rate.sell_tiers else [],
            }
            for rate in rates
        ]
