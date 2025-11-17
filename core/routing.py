"""
WebSocket URL Routing for Travel Suite
"""

from django.urls import re_path
from .consumers import BusLocationConsumer, NotificationConsumer, OperatorConsumer

websocket_urlpatterns = [
    re_path(r'ws/bus-location/$', BusLocationConsumer.as_asgi()),
    re_path(r'ws/notifications/$', NotificationConsumer.as_asgi()),
    re_path(r'ws/operators/$', OperatorConsumer.as_asgi()),
]
