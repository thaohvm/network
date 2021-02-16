import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .forms import NewPostForm
from .models import User, Post


@login_required(login_url='/login')
def index(request):
    return HttpResponseRedirect(reverse("post"))


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


@login_required(login_url='/login')
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


@login_required(login_url='/login')
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


@csrf_exempt
@login_required(login_url='/login')
def like(request):
    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=400)
    data = json.loads(request.body)
    try:
        post = Post.objects.get(id=int(data["id"]))
        # Make update
        if data["action"] == "like":
            if request.user not in post.like.all():
                post.like.add(request.user)
                post.save()
        else:
            if request.user in post.like.all():
                post.like.remove(request.user)
                post.save()
        return JsonResponse({"action": data["action"], "likes": len(post.like.all())}, status=200)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post doesn't exist."}, status=400)
