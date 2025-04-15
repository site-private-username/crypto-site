from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
import json
import logging

logger = logging.getLogger(__name__)

# class PriceConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         print("🔌 Attempting to connect...")  # This will show in your runserver console
#         try:
#             await self.channel_layer.group_add("prices", self.channel_name)
#             print(f"✅ Added to prices group with channel name: {self.channel_name}")
#             await self.accept()
#             print("✅ Connection accepted")
#
#             # Test if we're really in the group
#             channel_layer = get_channel_layer()
#             groups = channel_layer.groups if hasattr(channel_layer, 'groups') else {}
#             print(f"🔍 Current groups after connection: {groups}")
#         except Exception as e:
#             print(f"❌ Error in connect: {str(e)}")
#             raise
#
#     async def disconnect(self, close_code):
#         print(f"👋 Disconnecting with code: {close_code}")
#         try:
#             await self.channel_layer.group_discard("prices", self.channel_name)
#             print("✅ Removed from prices group")
#         except Exception as e:
#             print(f"❌ Error in disconnect: {str(e)}")
#
#     async def price_update(self, event):
#         print(f"📨 Received price update: {event}")
#         try:
#             await self.send(text_data=json.dumps(event["data"]))
#             print("✅ Sent price update to client")
#         except Exception as e:
#             print(f"❌ Error sending price update: {str(e)}")


class TestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps({
            'message': 'Websocket connection established',
        }))

    async def receive(self, text_data):
        await self.send(text_data=json.dumps({
            'echo': text_data,
        }))

class RandomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("random_group", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("random_group", self.channel_name)

    async def send_message(self, event):
        await self.send(text_data=json.dumps({
            "random_string": event["message"]
        }))


class PriceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("prices", self.channel_name)
        await self.accept()
        print("websocket connection established")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("prices", self.channel_name)

    async def send_price(self, event):
        await self.send(text_data=json.dumps(event["data"]))

