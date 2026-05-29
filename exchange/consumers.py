import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .cache import get_cached_exchange_rates


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

    async def get_current_rates(self):
        """
        Fetch current exchange rates from Redis cache.
        Falls back to database if cache miss.
        """
        return await sync_to_async(get_cached_exchange_rates)()
