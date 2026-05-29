from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/rates/', consumers.ExchangeRateConsumer.as_asgi()),
]
