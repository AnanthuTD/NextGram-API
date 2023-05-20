from django.urls import path

from . import views

urlpatterns = [
    path('conversations/', views.conversations, name='conversations'),
    path('<username>/load_messages/', views.load_messages, name='load_messages'),
    path('unsend/', views.unsend, name='unsend'),
]
