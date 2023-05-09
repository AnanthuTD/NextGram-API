import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=False, blank=False)
    phone = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(blank=True)
    profile_img = models.ImageField(
        upload_to='profile_images', default='default_profile.png')
    location = models.CharField(max_length=100, blank=True)
    id_user = models.UUIDField(unique=True, default=uuid.uuid4)
    gender = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    following = models.ManyToManyField('self', related_name='followers', symmetrical=False)
    post_count = models.PositiveIntegerField(default=0)
