from django.apps import AppConfig



class ChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat'

    def ready(self):
        from chat.models import Room
        Room.objects.all().delete()
        pass


