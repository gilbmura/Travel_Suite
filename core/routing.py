"""
WebSocket URL Routing for Travel Suite
"""

from django.urls import re_path
from .consumers import BusLocationConsumer, NotificationConsumer

websocket_urlpatterns = [
    re_path(r'ws/bus-location/$', BusLocationConsumer.as_asgi()),
    re_path(r'ws/notifications/$', NotificationConsumer.as_asgi()),
]
