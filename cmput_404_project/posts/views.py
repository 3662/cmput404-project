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
from requests.auth import HTTPBasicAuth


def display_public_posts(request):
    # posts = Post.objects.filter(visibility='PUBLIC').exclude(author=request.user).order_by('-published')
    posts = Post.objects.filter(visibility='PUBLIC').order_by('-published')
    for post in posts:
        post.comments = get_post_comments(post)

    comment_form = CommentForm(request.POST)

    team9_auth = HTTPBasicAuth('group_9', 'be69f300764182cd7a9be3bd0e2b4954814f7d253c64d5ae37f4a394c50565e7') 

    # Access posts from other connected nodes
    foreign_posts = []

    authors_response = requests.get(
        'https://socialdistribution-t13.herokuapp.com/api/v1/authors',
        auth=team9_auth
    )
    data = authors_response.json()
    for author in data['items']:
        id = author['id']
        post_response = requests.get(
            f'https://socialdistribution-t13.herokuapp.com/api/v1/authors/{id}/posts/',
            auth=team9_auth
        )
        data = post_response.json()
        foreign_posts.extend(data['items'])

    context = {
        'posts': posts,
        'author': request.user,
        'comment_form': comment_form,
        'fps': foreign_posts,
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

        ##from felipes branch
        data = {
            'title': form['title'].value(),
            'description': form['description'].value(),
            'content_type': form['content_type'].value(),
            'content': form['content'].value(),
            'image': form['image'].value(),
            'categories': form['categories'].value(),
            'visibility': form['visibility'].value(),
        }
        post_url = "http://127.0.0.1:8000/service/authors/{}/posts".format(request.user.id)
        post_request = requests.post(post_url, data)

        # post_id = 'where_do_i_get_the_post_id_before_even_creating_it'
        # inbox_item = {
        #     **data,
        #     "type": "post",
        #     "id": post_id,
        #     "source": "http://lastplaceigotthisfrom.com/posts/yyyyy",
        #     "origin": "http://whereitcamefrom.com/posts/zzzzz",
        #     "author": request.user.get_detail_dict,
        #     "comments": post_id+"/comments",
        #     "published": "2015-03-09T13:07:04+00:00",
        # }
        # post_url = "http://127.0.0.1:8000/service/authors/{}/inbox".format(request.user.id)
        # post_request = requests.post(post_url, data=inbox_item))

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
