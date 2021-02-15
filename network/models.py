from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    follower = models.ManyToManyField(
        "User", blank=True, related_name="user_follower")
    following = models.ManyToManyField(
        "User", blank=True, related_name="user_following")


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=256, blank=True)
    time = models.DateTimeField(auto_now=True)
    like = models.ManyToManyField(User, blank=True, related_name="user_like")

    def __str__(self):
        return f"{self.user} - {self.content}"
