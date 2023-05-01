import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from post.utils.rename_media import rename_media

User = get_user_model()

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post_id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    file = models.FileField(upload_to=rename_media)
    like = ArrayField(models.CharField(max_length=255), null=True, blank=True)
    shares = ArrayField(models.CharField(max_length=255), null=True, blank=True)
    description = models.TextField(blank=True)
    hash_tag = ArrayField(models.CharField(max_length=255), blank=True, null=True)
    mentions = ArrayField(models.CharField(max_length=255), blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)
    time_stamp = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    time_stamp = models.DateTimeField(auto_now_add=True)
    

