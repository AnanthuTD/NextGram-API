import asyncio
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from chat.utils.gnerate_room_name import generate_room_name
from .models import Conversation, Chat, User
from asgiref.sync import sync_to_async
from .models import Room


class ChatConsumer(AsyncWebsocketConsumer):
    conversation: Conversation
    recipient_username = None

    def get_or_create_communication(self, sender, recipient_usename):
        receiver = User.objects.get(username=recipient_usename)
        self.conversation, created = Conversation.objects.update_or_create(
            sender=sender, receiver=receiver)

    async def connect(self):
        sender = self.scope['user']
        username = sender.username
        self.recipient_username = self.scope["url_route"]["kwargs"]["room_name"]

        self.room_name = generate_room_name(self.recipient_username, username)
        self.room_group_name = "Chat_%s" % self.room_name

        await sync_to_async(
            self.get_or_create_communication)(sender, self.recipient_username)

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

        await sync_to_async(Room.objects.add)(self.room_group_name, self.channel_name)

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        asyncio.create_task(sync_to_async(Room.objects.remove)(
            self.room_group_name, self.channel_name))

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        chat: Chat = await(sync_to_async(Chat.objects.create)(
            conversation=self.conversation, message=message))

        message = {
            'message': message,
            'timestamp': str(chat.timestamp),
            'sender_username': self.scope['user'].username,
        }

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": "Chat_message", "message": message}
        )
        count = await sync_to_async(Room.objects.count)(self.room_group_name)

        if count == 1:
            user_channel_name = f'user_{self.recipient_username}'

            await self.channel_layer.group_send(
                user_channel_name, {"type": "Chat_message", "message": message})

        # Send JSON response back to WebSocket
        response = {"status": "OK", "message": "Message received"}
        await self.send(text_data=json.dumps(response))

    # Receive message from room group
    async def Chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))


class UserChannelConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        username = user.username

        # Create a channel for the user
        user_channel_name = f'user_{username}'

        # Accept the WebSocket connection
        await self.accept()

        # Add the user's channel to the group
        await self.channel_layer.group_add(user_channel_name, self.channel_name)

    async def disconnect(self, close_code):
        user = self.scope['user']
        username = user.username

        # Remove the user's channel from the group
        user_channel_name = f'user_{username}'
        await self.channel_layer.group_discard(user_channel_name, self.channel_name)

    # Receive message from room group
    async def Chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))
