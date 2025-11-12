"""
WebSocket Consumers for Travel Suite
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer


class BusLocationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket Consumer for Real-Time Bus Location Updates.
    Allows clients to receive live bus location data.
    """
    async def connect(self):
        self.room_group_name = 'bus_locations'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Receive message from WebSocket."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'bus_location':
                # Broadcast bus location to all connected clients
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'send_location',
                        'location': data.get('location'),
                        'bus_id': data.get('bus_id'),
                        'timestamp': data.get('timestamp'),
                    }
                )
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format'
            }))

    async def send_location(self, event):
        """Send location message to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'bus_location',
            'bus_id': event['bus_id'],
            'location': event['location'],
            'timestamp': event.get('timestamp'),
        }))


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket Consumer for Real-Time Notifications.
    Allows clients to receive booking, payment, and ticket notifications.
    """
    async def connect(self):
        self.user = self.scope["user"]
        self.room_group_name = f'notifications_{self.user.id}' if self.user.is_authenticated else 'notifications_anonymous'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def notify(self, event):
        """Send notification to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': event.get('notification_type'),
            'message': event.get('message'),
            'data': event.get('data'),
        }))
