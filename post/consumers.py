import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Comment, Post
from asgiref.sync import sync_to_async


class CommentConsumer(AsyncWebsocketConsumer):
    recipient_username = None

    def create_comment(self, author, comment):
        post = Post.objects.get(post_id=self.room_name)
        return Comment.objects.create(
            author=author, comment=comment, post=post)

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "Chat_%s" % self.room_name

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        comment = text_data_json["comment"]

        newComment: Comment = await sync_to_async(self.create_comment)(
            author=self.scope['user'], comment=comment)

        comment = {
            'id': newComment.id,
            'comment': newComment.comment,
            'time_stamp': str(newComment.time_stamp),
            'author': self.scope['user'].username,
            'profile_img': await sync_to_async(self.get_profile_img_url)()
        }

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": "Chat_message", "message": comment}
        )

        # Send JSON response back to WebSocket
        response = {"status": "OK", "message": "Message received"}
        await self.send(text_data=json.dumps(response))

    # Receive message from room group
    async def Chat_message(self, event):
        message = event["message"]
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))

    def get_profile_img_url(self):
        return self.scope['user'].profile.profile_img.url
