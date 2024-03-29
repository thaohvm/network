
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("post", views.post, name="post"),
    path("profile", views.profile, name="profile"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("like", views.like, name="like"),
    path("follow", views.follow, name="follow"),
    path("following", views.following_list, name="followinglist"),
]
