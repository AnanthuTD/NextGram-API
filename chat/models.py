from django.db.models.signals import post_migrate
from django.db import models
from django.contrib.auth import get_user_model
import uuid
from django.dispatch import receiver
from django.db.models import Q

User = get_user_model()


class Conversation(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='communications')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    converdation_id = models.UUIDField(default=uuid.uuid4, primary_key=True)

    @property
    def last_message(self):
        last_chat = self.messages.order_by('-timestamp').first()
        return last_chat.message if last_chat else ''

    class Meta:
        ordering = ['-updated_at']


class Chat(models.Model):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name='messages')
    message = models.TextField(blank=False, null=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def save(self, *args, **kwargs):
        if not self.message.strip():
            return  # Do not save if message is empty or contains only whitespace
        super().save(*args, **kwargs)


class Presence(models.Model):
    room = models.ForeignKey("Room", on_delete=models.CASCADE)
    channel_name = models.CharField(
        max_length=255, help_text="Reply channel for connection that is present"
    )

    def __str__(self):
        return self.channel_name

    class Meta:
        unique_together = [("room", "channel_name")]


class RoomManager(models.Manager):
    def add(self, room_channel_name, user_channel_name):
        room, created = Room.objects.get_or_create(
            room_name=room_channel_name)
        room.add_presence(user_channel_name)
        return room

    def remove(self, room_channel_name, user_channel_name):
        try:
            room = Room.objects.get(room_name=room_channel_name)
        except Room.DoesNotExist:
            return
        room.remove_presence(channel_name=user_channel_name)

    def count(self, room_channel_name):
        try:
            room = Room.objects.get(room_name=room_channel_name)
        except Room.DoesNotExist:
            return 0
        return room.count_presences()


class Room(models.Model):
    room_name = models.CharField(
        max_length=255, unique=True, help_text="Group channel name for this room"
    )

    objects = RoomManager()  # Corrected variable name

    def add_presence(self, channel_name):

        presence, created = Presence.objects.get_or_create(
            room=self, channel_name=channel_name)
        # You can do something with the `authed_user` if needed

    def remove_presence(self, channel_name=None, presence=None):
        if presence is None:
            try:
                presence = Presence.objects.get(
                    room=self, channel_name=channel_name)
            except Presence.DoesNotExist:
                return
        presence.delete()

    def count_presences(self, channel_name=None):
        return Presence.objects.filter(room=self).count()
