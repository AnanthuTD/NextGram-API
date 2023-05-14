from django.contrib import admin
from .models import UserCommunication, Chat
# Register your models here.
admin.site.register([UserCommunication, Chat])