import json
from channels.generic.websocket import AsyncWebsocketConsumer

class MyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # self.group_name = 'computer_status_updates'

        # await self.channel_layer.group_add(
        #     self.group_name,
        #     self.channel_name
        # )

        await self.accept()

    async def disconnect(self, close_code):
        # await self.channel_layer.group_discard(
        #     self.group_name,
        #     self.channel_name
        # )
        pass

    async def send_status_update(self, event):
        # message = event['message']
        # print(1234567890235182538464846388789348296341830571037)
        # # Send message back to WebSocket client
        # await self.send(text_data=json.dumps({
        #     'id': message['id'],
        #     'name': message['computer_name'],
        #     'status': message['status']
        # }))

        await self.send(text_data="Send this")