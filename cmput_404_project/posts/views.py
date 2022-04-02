from django.shortcuts import render, redirect
from social_distribution.models import Post, Comment, Like
from django.http import HttpResponse
from .forms import PostForm, PostLike, PrivatePostForm, CommentForm
from django.utils import timezone
import hashlib
from django.utils.text import slugify
import time
import uuid
import requests


def display_public_posts(request):
    context = {
        'author_id': request.user.id,
    }

    return render(request, 'posts/public_posts.html', context)

def display_private_posts(request):
    posts = Post.objects.filter(visibility='PRIVATE').filter(recepient=request.user.id)
    context = {
        'posts': posts,
        'author': request.user,
    }

    return render(request, 'posts/private_posts.html', context)

def get_post_comments(post):
    comments = Comment.objects.filter(post=post)
    return comments

def display_own_posts(request):
    posts = Post.objects.filter(author=request.user).order_by('-published')

    return render(request, 'posts/own_posts.html', {'posts': posts})

def edit_post(request, id):
    post = Post.objects.filter(id=id)[0]

    if request.method == "POST":
        form = PostForm(request.POST)

        obj = Post.objects.get(id=id)
        obj.title = form['title'].value()
        obj.description = form['description'].value()
        obj.content_type = form['content_type'].value()
        obj.content = form['content'].value()
        obj.image = form['image'].value()
        obj.categories = form['categories'].value()
        obj.visibility = form['visibility'].value()
        print(obj.visibility)
        obj.save()

        return redirect("/")
    else:
        data = {
            'title': post.title,
            'description': post.description,
            'content_type': post.content_type,
            'content': post.content,
            'image': post.image,
            'categories': post.categories,
            'visibility': post.visibility,
        }

        form = PostForm(data)

        return render(request, "posts/edit_post.html", {'form': form})

def delete_post(request, id):
    Post.objects.filter(id=id).delete()

    return redirect("/")

def new_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)

        data = {
            'title': form['title'].value(),
            'description': form['description'].value(),
            'content_type': form['content_type'].value(),
            'content': form['content'].value(),
            'image': form['image'].value(),
            'categories': form['categories'].value(),
            'visibility': form['visibility'].value(),
        }

        # post_url = "https://cmput404-project-team9.herokuapp.com/service/authors/{}/posts".format(request.user.id)
        post_url = "http://127.0.0.1:8000/service/authors/{}/posts".format(request.user.id)

        post_request = requests.post(post_url, data)

        return redirect("/")
    else:
        form = PostForm()

        return render(request, "posts/new_post.html", {'form': form})

def new_private_post(request):
    if request.method == "POST":
        form = PrivatePostForm(request.POST)
        if not form.is_valid():
            print('ERRORS', form.errors)
        obj = form.save(commit=False)  
        obj.author = request.user
        obj.visibility = 'PRIVATE'
        obj.recepient = request.POST.get('recepient')
        print('NOW')

        # TODO set proper URls
        obj.source = ""
        obj.origin = ""

        obj.save()

        return redirect("/")
    else:
        form = PrivatePostForm()

        return render(request, "posts/new_private_post.html", {'form': form})        


def add_comment(request, id):
    if request.method == "POST":
        post = Post.objects.get(id=id)
        content = request.POST.get('content')
        author = request.user
        comment = Comment.objects.create(content=content, author=author, post=post)
        comment.save()
        
    return redirect('/posts/')
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
