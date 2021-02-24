import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, JsonResponse
from django.core.paginator import Paginator
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .forms import NewPostForm, EditPostForm
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


@csrf_exempt
@login_required(login_url='/login')
def post(request):
    if request.method == "POST":
        form = NewPostForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
        return HttpResponseRedirect(reverse("post"))
    elif request.method == "PUT":
        data = json.loads(request.body)
        try:
            post_id = data["id"]
            post = Post.objects.get(id=int(post_id))
            if request.user == post.user:
                post.content = data["content"]
                post.save()
                return JsonResponse({"id": post_id}, status=200)
            else:
                return JsonResponse({"id": post_id, "error": "Permission denied."}, status=403)
        except Post.DoesNotExist:
            return JsonResponse({"id": post_id, "error": "Post doesn't exist."}, status=400)
    else:
        # GET
        posts = sorted(Post.objects.all(), reverse=True, key=lambda p: p.time)

        # Tuples of (post, like->boolean)
        data = [(post, request.user in post.like.all()) for post in posts]

        # Paginator
        paginator = Paginator(data, 10)  # Show 10 post per page.
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, "network/post.html", {
            "new_post_form": NewPostForm(None, initial={}),
            "page_obj": page_obj,
        })


@login_required(login_url='/login')
def profile(request, username=None):
    if request.method == "GET":
        try:
            user = User.objects.get(
                username=username) if username else request.user
            posts = sorted(Post.objects.filter(user=user), reverse=True, key=lambda p:p.time)
            # Paginator
            paginator = Paginator(posts, 10)  # Show 10 post per page.
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            return render(request, "network/profile.html", {
                "user": user,
                "posts": posts,
                "show_follow": user != request.user,
                "followed": request.user in user.follower.all(),
                "followers": len(user.follower.all()),
                "followings": len(user.following.all()),
                "page_obj": page_obj
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


@csrf_exempt
@login_required(login_url='/login')
def follow(request):
    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=400)
    data = json.loads(request.body)
    try:
        user = User.objects.get(id=int(data["id"]))
        # Make update
        if data["action"] == "Follow":
            if request.user not in user.follower.all():
                user.follower.add(request.user)
                user.save()
                request.user.following.add(user)
                request.user.save()
        else:
            if request.user in user.follower.all():
                user.follower.remove(request.user)
                user.save()
                request.user.following.remove(user)
                request.user.save()
        return JsonResponse({"action": data["action"], "followers": len(user.follower.all())}, status=200)
    except User.DoesNotExist:
        return JsonResponse({"error": "User doesn't exist."}, status=400)


@login_required(login_url='/login')
def following_list(request):
    if request.method == "GET":
        posts = []
        following_list = request.user.following.all()
        for fl in following_list:
            posts.extend(Post.objects.filter(user=fl))
        return render(request, 'network/following.html', {
            "following_list": following_list,
            "posts": posts
        })
