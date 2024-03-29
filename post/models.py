import os
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.dispatch import receiver
from post.utils.rename_media import rename_media
from django.db.models.signals import post_save

User = get_user_model() 


def upload_to_posts(instance, filename):
    return os.path.join("posts", rename_media(instance, filename))


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    file = models.FileField(upload_to=upload_to_posts, max_length=200)
    likes = models.ManyToManyField("auth.User", related_name='liked')
    # shares = models.ManyToManyField("auth.User")
    caption = models.TextField(blank=True)
    hash_tag = ArrayField(models.CharField(
        max_length=255), blank=True, null=True)
    mentions = ArrayField(models.CharField(
        max_length=255), blank=True, null=True)
    location = models.CharField(max_length=200, blank=True)
    time_stamp = models.DateTimeField(auto_now_add=True)
    private = models.BooleanField(default=False)


def upload_to_stories(instance, filename):
    return os.path.join("stories", rename_media(instance, filename))


class Story(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    file = models.FileField(upload_to=upload_to_stories)
    caption = models.TextField(blank=True)
    hash_tag = ArrayField(models.CharField(
        max_length=255), blank=True, null=True)
    mentions = ArrayField(models.CharField(
        max_length=255), blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)
    time_stamp = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    time_stamp = models.DateTimeField(auto_now_add=True)


@receiver(post_save, sender=Post)
def increase_post_count(sender, instance, created, **kwargs):
    if created:
        profile = instance.user.profile
        profile.post_count += 1
        profile.save()
