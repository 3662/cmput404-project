from django.shortcuts import render, redirect
from social_distribution.models import Post
from django.http import HttpResponse
from .forms import PostForm
from django.utils import timezone
import hashlib
from django.utils.text import slugify
import time

def display_public_posts(request):
    posts = Post.objects.all().order_by('-published')

    return render(request, 'posts/public_posts.html', {'posts': posts})

def display_own_posts(request):
    posts = Post.objects.filter(author=request.user).order_by('-published')

    return render(request, 'posts/own_posts.html', {'posts': posts})

def edit_post(request, id):
    post = Post.objects.filter(id=id)[0]

    if request.method == "POST":
        form = PostForm(request.POST)

        obj = form.save(commit=False)   

        obj.author = post.author
        obj.id = post.id
        obj.source = post.source
        obj.origin = post.origin

        obj.save()

        return redirect("/")
    else:
        data = {
            'title': post.title,
            'description': post.description,
            'image': post.image,
        }

        form = PostForm(data)

        return render(request, "posts/edit_post.html", {'form': form})

def new_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        obj = form.save(commit=False)                
        obj.author = request.user
        obj.id = create_post_id(request.user.username)

        # TODO set proper URls
        obj.source = ""
        obj.origin = ""

        obj.save()

        return redirect("/")
    else:
        form = PostForm()

        return render(request, "posts/new_post.html", {'form': form})

def create_post_id(username):
    sha = hashlib.sha256()
    sha.update(bytes(username+str(int(time.time())), 'utf-8'))

    return slugify(sha.hexdigest())