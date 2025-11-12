import json
from channels.generic.websocket import AsyncWebsocketConsumer


class BusLocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'bus_locations'
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

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_location',
                'location': data['location'],
                'bus_id': data['bus_id'],
            }
        )

    async def send_location(self, event):
        await self.send(text_data=json.dumps({
            'bus_id': event['bus_id'],
            'location': event['location'],
        }))
