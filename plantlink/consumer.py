import json
from channels.generic.websocket import AsyncWebsocketConsumer

class SensorDataConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'sensor_data'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        print(f"WebSocket connected: {self.channel_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        print(f"WebSocket disconnected: {self.channel_name}")

    async def receive(self, text_data):
        data = json.loads(text_data)
        print(f"WebSocket message received: {data}")
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'sensor_data_message',
                'data': data
            }
        )

    async def sensor_data_message(self, event):
        data = event['data']
        await self.send(text_data=json.dumps(data))
        print(f"WebSocket message sent: {data}")
