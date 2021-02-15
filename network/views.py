from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse

from .forms import NewPostForm
from .models import User, Post


def index(request):
    return render(request, "network/index.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@login_required
def post(request):
    if request.method == "POST":
        form = NewPostForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            return HttpResponseRedirect(reverse("post"))
    else:
        # GET
        posts = sorted(Post.objects.all(), reverse=True, key=lambda p: p.time)
        # Tuples of (post, like->boolean)
        data = [(post, request.user in post.like.all()) for post in posts]
        return render(request, "network/post.html", {
            "data": data,
            "new_post_form": NewPostForm(None, initial={}),
        })


@login_required
def profile(request, username=None):
    if request.method == "GET":
        try:
            user = User.objects.get(
                username=username) if username else request.user
            posts = Post.objects.filter(user=user)
            return render(request, "network/profile.html", {
                "user": user,
                "posts": posts,
            })
        except User.DoesNotExist:
            return HttpResponseBadRequest("Invalid username!")


@login_required
def like(request):
    if request.method == "POST":
        pass
