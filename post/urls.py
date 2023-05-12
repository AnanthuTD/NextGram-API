from django.urls import path
from . import views

urlpatterns = [
    path('', views.post, name="post"),
    path('allPost/', views.allPost, name="allPost"),
    path('<uuid:post_id>/like/', views.like, name="like"),
    path('<uuid:post_id>/dislike/', views.dislike, name="dislike"),
    path('comments/', views.comments, name="comments"),
]
