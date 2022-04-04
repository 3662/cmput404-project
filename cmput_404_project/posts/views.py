import re
from django.shortcuts import render, redirect
from social_distribution.models import Author, Post, Comment, Like, Friends
from django.http import HttpResponse
from .forms import PostForm, PostLike, PrivatePostForm, CommentForm
from django.utils import timezone
import hashlib
from django.utils.text import slugify
import time
import uuid
import requests
from requests.auth import HTTPBasicAuth
from urllib.parse import urlparse
from service.requests import get_b64_server_credential
from service.models import ServerNode

from base64 import b64encode

def display_public_posts(request):
    # posts = Post.objects.filter(visibility='PUBLIC').exclude(author=request.user).order_by('-published')
    # posts = Post.objects.filter(visibility='PUBLIC', unlisted=False).order_by('-published')
    # for post in posts:
    #     post.comments = get_post_comments(post)

    comment_form = CommentForm(request.POST)
    new_post_form = PostForm()

    # Access posts from other connected nodes
    foreign_posts = []
    for node in ServerNode.objects.all():
        if node.is_local:
            continue
        url = f'{node.host}/authors/'
        auth = (node.sending_username, node.sending_password)
        response = requests.get(url, auth=auth)
        try:
            data = response.json()
            authors = data['items']
            for author in authors:
                url = author['url'] + '/posts/'
                response = requests.get(url, auth=auth)
                try:
                    data = response.json()
                    foreign_posts.extend(data['items'])
                except Exception as e:
                    print('Error: URL =', url)
                    print(e)
        except Exception as e:
            print('Error: URL =', url)
            print(e)
    # print(foreign_posts)
    context = {
        # 'posts': posts,
        'author': request.user,
        'comment_form': comment_form,
        'new_post_form': new_post_form,
        'fps': foreign_posts,
        'author_id': request.user.id,
    }

    return render(request, 'posts/public_posts.html', context)

def display_private_posts(request):
    posts = Post.objects.filter(visibility='PRIVATE').filter(recipient=request.user.id)
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

def create_post(form, author, visibility='PUBLIC', recipient='', share_from=''):
    obj = form.save(commit=False)  
    obj.author = author
    obj.visibility = visibility
    if recipient is not '':
        obj.recipient = recipient
    if share_from is not '':
        obj.share_from = share_from

    # TODO set proper URls
    obj.source = ""
    obj.origin = ""

    obj.save()

def get_friends_list(request):
    f_qs_list = []
    friends_list = []
    authors = Friends.objects.filter(sender=request.user, status='accepted').values_list('receiver', flat=True)
    for qs in authors:
        cross_qs = Friends.objects.filter(sender=qs, receiver=request.user, status='accepted').count()
        if cross_qs > 0:
            f_qs_list.append(qs)
    f_qs = Author.objects.filter(id__in=f_qs_list)
    for qs in f_qs:
        if qs.id in authors:
            friends_list.append(qs.id)
    print(friends_list)
    return friends_list

def new_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        form.save(commit=False)
        if form.cleaned_data["visibility"] == "FRIENDS":
            friends = get_friends_list(request)
            for friend in friends:
                form = PostForm(request.POST)
                form.save(commit=False)
                create_post(form, request.user, 'PRIVATE', friend)

        else:
            create_post(form, request.user, form.cleaned_data["visibility"])
    #     # print(post)
    #     #TODO: send this post to appropriate inboxes
    #     #-----------------------------
    #     # post_id = '...'
    #     # inbox_item = {
    #     #     **data,
    #     #     "type": "post",
    #     #     "id": post_id,
    #     #     "source": "http://lastplaceigotthisfrom.com/posts/yyyyy",
    #     #     "origin": "http://whereitcamefrom.com/posts/zzzzz",
    #     #     "author": request.user.get_detail_dict,
    #     #     "comments": post_id+"/comments",
    #     #     "published": "2015-03-09T13:07:04+00:00",
    #     # }
    #     # url = "http://127.0.0.1:8000/service/authors/{}/inbox".format(request.user.id)
    #     # post_request = requests.post(url, data=inbox_item))

    #     return redirect("/")
    # else:
    #     form = PostForm()

    #     return render(request, "posts/new_post.html", {'form': form})

    if request.method == "POST":
        return redirect("/")
    else:
        form = PostForm()
        return render(request, "posts/new_post.html", {'form': form, 'author_id': request.user.id})


def new_private_post(request):
    if request.method == "POST":
        form = PrivatePostForm(request.POST)
        create_post(form, request.user, 'PRIVATE', request.POST.get('recipient'))

        return redirect("/")
    else:
        form = PrivatePostForm()
        qs = Author.objects.all().exclude(username=request.user)
        context = {
            'form': form,
            'authors': qs
        }

        return render(request, "posts/new_private_post.html", context)

def share_post(request, id):
    print('SHARE CALLED')
    if request.method == "POST":   
        obj = Post.objects.get(id=id)
        if obj.visibility == "PUBLIC":
            share_from = obj.author
            obj.pk = None
            #obj.save
            obj.visibility = "PUBLIC"
            obj.share_from = share_from
            obj.author = request.user
            obj.save()
        else:
            friends = get_friends_list(request)
            for friend in friends:
                obj = Post.objects.get(id=id)
                share_from = obj.author
                obj.pk = None
                obj.visibility = "PRIVATE"
                obj.share_from = share_from
                obj.author = request.user
                obj.recipient = friend
                obj.save()

    return redirect("/")

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
