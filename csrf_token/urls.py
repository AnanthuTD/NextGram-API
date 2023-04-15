""" from django.urls import path
from . import views

urlpatterns = [
    path("", views.get_csrf_token, name="csrf_token"),

]
 """