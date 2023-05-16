from django.db import models
from django.contrib.auth import get_user_model
import uuid

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
        last_chat =  self.messages.order_by('-timestamp').first()
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
