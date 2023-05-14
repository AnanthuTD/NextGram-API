from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class UserCommunication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_communications')
    communicated_with = models.ManyToManyField(User, related_name='communications_with')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username}'s communications" # type: ignore
    

class Chat(models.Model):
    room_id = models.UUIDField(primary_key=True)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

