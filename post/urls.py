from django.urls import path
from . import views

urlpatterns = [
    path('', views.post, name="post"),
    path('story/', views.story, name="story"),
    path('stories/', views.stories, name="stories"),
    path('<str:other_user>/posts/', views.post, name='fetch_data_other'),
    path('allPost/', views.allPost, name="allPost"),
    path('<uuid:post_id>/like/', views.like, name="like"),
    path('<uuid:post_id>/dislike/', views.dislike, name="dislike"),
    path('comments/', views.comments, name="comments"),
]
