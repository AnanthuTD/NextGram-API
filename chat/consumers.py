import json
from pprint import pprint
import uuid

from channels.generic.websocket import AsyncWebsocketConsumer

from chat.utils.gnerate_room_name import generate_room_name

from .models import UserCommunication, Chat

import asyncio

from asgiref.sync import sync_to_async


def get_or_create_communication_async(sender, recipient):
    communicated_user, created = UserCommunication.objects.get_or_create(
        user=sender, defaults={'user': sender})
    communicated_user.communicated_with.add(recipient)


class ChatConsumer(AsyncWebsocketConsumer):
    room_id:uuid.UUID
    async def connect(self):
        sender = self.scope['user']
        username = sender.username
        recipient = self.scope["url_route"]["kwargs"]["room_name"]

        self.room_id = generate_room_name(recipient, username)
        self.room_name = str(self.room_id)
        self.room_group_name = "chat_%s" % self.room_name

        asyncio.ensure_future(sync_to_async(
            get_or_create_communication_async)(sender, recipient))

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message": message}
        )

        # Send JSON response back to WebSocket
        response = {"status": "OK", "message": "Message received"}
        await self.send(text_data=json.dumps(response))

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        print(self.room_id)
        asyncio.ensure_future(sync_to_async(Chat.objects.create)(
            room_id=uuid.UUID(self.room_name), message=message))
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))
