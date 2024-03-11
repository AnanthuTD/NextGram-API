# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.search, name='search_api'),
    path('<str:hashtag>/hashtag/', views.search_by_hashtag, name='search_by_hashtag'),
]
