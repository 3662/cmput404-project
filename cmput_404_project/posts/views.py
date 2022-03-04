from django.shortcuts import render, redirect
from social_distribution.models import Post, Like, Author
from django.http import HttpResponse
from .forms import PostForm, PostLike, PrivatePostForm
from django.utils import timezone
import hashlib
from django.utils.text import slugify
import time
import uuid


def display_public_posts(request):
    posts = Post.objects.filter(visibility='PUBLIC').exclude(author=request.user).order_by('-published')
    context = {
        'posts': posts,
        'author': request.user,
    }

    return render(request, 'posts/public_posts.html', context)

def display_private_posts(request):
    posts = Post.objects.filter(visibility='PRIVATE').filter(recepient=request.user.id)
    context = {
        'posts': posts,
        'author': request.user,
    }

    return render(request, 'posts/private_posts.html', context)

def display_own_posts(request):
    posts = Post.objects.filter(author=request.user).order_by('-published')

    return render(request, 'posts/own_posts.html', {'posts': posts})

def edit_post(request, id):
    post = Post.objects.filter(id=id)[0]

    if request.method == "POST":
        form = PostForm(request.POST)

        obj = form.save(commit=False)   

        obj.author = post.author
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
        obj.visibility = 'PRIVATE'

        # TODO set proper URls
        obj.source = ""
        obj.origin = ""

        obj.save()

        return redirect("/")
    else:
        form = PostForm()

        return render(request, "posts/new_post.html", {'form': form})

def new_private_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        obj = form.save(commit=False)  
        obj.author = request.user
        obj.visibility = 'PRIVATE'
        obj.recepient = request.POST.get('recepient')

        # TODO set proper URls
        obj.source = ""
        obj.origin = ""

        obj.save()

        return redirect("/")
    else:
        form = PrivatePostForm()

        return render(request, "posts/new_private_post.html", {'form': form})        

def display_like(request):
    like = Like.objects.all()
    return render(request, 'posts/display_like.html', {'like': like})

def like_post1(request):
    if request.method == "POST":
        id = request.POST.get('post_id')
        post = Post.objects.get(id=id)
        like, inserted = Like.objects.get_or_create(author=request.user, post=post)
        if not inserted:
            post.liked.remove(request.user)
            rec = Like.objects.get(author=request.user, post=post)
            rec.delete()
        else:
            post.liked.add(request.user)
            post.save()
            like.save()
    return redirect('/posts/')
