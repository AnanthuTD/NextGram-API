from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False, blank=False)
    phone = models.IntegerField(blank=True, null=True, unique=True)
    email = models.EmailField(blank=True, null=True, unique=True)
    # user_name = models.CharField(max_length=20, unique=True, null=False, blank=False)
    id_user = models.IntegerField(unique=True)
    bio = models.TextField(blank=True)
    profile_img = models.ImageField(upload_to='profile_images',default='default-profile-pic.svg')
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.username
