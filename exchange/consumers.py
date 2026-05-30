import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .cache import get_cached_exchange_rates

logger = logging.getLogger(__name__)


class ExchangeRateConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time exchange rate updates.
    Clients connect to this and receive automatic updates when rates change.
    """

    async def connect(self):
        """Handle WebSocket connection"""
        self.room_group_name = 'exchange_rates'

        try:
            # Join the exchange rates group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()
            logger.info(f"WebSocket connected: {self.channel_name}")

            # Send initial rates immediately after connection
            try:
                rates = await self.get_current_rates()
                await self.send(text_data=json.dumps({
                    'type': 'rates_update',
                    'rates': rates
                }))
            except Exception as e:
                logger.error(f"Error sending initial rates: {e}")
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Failed to load exchange rates'
                }))

        except Exception as e:
            logger.error(f"Error during WebSocket connection: {e}")
            await self.close()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        try:
            # Leave the exchange rates group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            logger.info(f"WebSocket disconnected: {self.channel_name} (code: {close_code})")
        except Exception as e:
            logger.error(f"Error during WebSocket disconnection: {e}")

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
                try:
                    rates = await self.get_current_rates()
                    await self.send(text_data=json.dumps({
                        'type': 'rates_update',
                        'rates': rates
                    }))
                except Exception as e:
                    logger.error(f"Error fetching rates for client request: {e}")
                    await self.send(text_data=json.dumps({
                        'type': 'error',
                        'message': 'Failed to fetch rates'
                    }))
            elif message_type == 'ping':
                # Keepalive ping from client
                await self.send(text_data=json.dumps({
                    'type': 'pong'
                }))
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON received: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
        except Exception as e:
            logger.error(f"Error handling client message: {e}")

    async def rates_update(self, event):
        """
        Receive message from room group and send to WebSocket.
        This is called when broadcast_rate_update is triggered via signals.
        """
        try:
            rates = event.get('rates', [])

            # Send message to WebSocket
            await self.send(text_data=json.dumps({
                'type': 'rates_update',
                'rates': rates
            }))
            logger.debug(f"Broadcasted rate update to {self.channel_name}")
        except Exception as e:
            logger.error(f"Error broadcasting rates to {self.channel_name}: {e}")

    async def get_current_rates(self):
        """
        Fetch current exchange rates from Redis cache.
        Falls back to database if cache miss.
        """
        try:
            return await sync_to_async(get_cached_exchange_rates)()
        except Exception as e:
            logger.error(f"Error getting cached rates: {e}")
            # Return empty list as fallback
            return []
