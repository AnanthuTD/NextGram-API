from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name="signup"),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view , name="logout"),
    path('profile/', views.profile, name="profile"),
    path('get_profile/<username>/', views.get_profile, name="get_profile"),
    path('follow/', views.follow, name="follow"),
    path('<uuid:id_user>/follow/', views.unfollow, name="unfollow"),
    path('followers/', views.followers, name='followers'),
    path('followings/', views.followings, name='followings'),
    path('search/', views.search, name='search'),
    path('interests/', views.user_interests, name='user_interests'),
    path('suggested-users/', views.suggested_users, name='suggested_users'),
]
