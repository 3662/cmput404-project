from django.shortcuts import render, redirect
from social_distribution.models import Author, Post, Comment, Like, Friends
from django.http import HttpResponse
from .forms import PostForm, PostLike, PrivatePostForm, CommentForm
from django.utils import timezone
import hashlib
from django.utils.text import slugify
import time
import uuid


def display_public_posts(request):
    # posts = Post.objects.filter(visibility='PUBLIC').exclude(author=request.user).order_by('-published')
    posts = Post.objects.filter(visibility='PUBLIC').order_by('-published')
    for post in posts:
        post.comments = get_post_comments(post)

    comment_form = CommentForm(request.POST)

    context = {
        'posts': posts,
        'author': request.user,
        'comment_form': comment_form,
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

def create_post(form, author, visibility='PUBLIC', recipient=''):
    obj = form.save(commit=False)  
    obj.author = author
    obj.visibility = visibility
    if recipient is not '':
        obj.recipient = recipient

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
        return redirect("/")
    else:
        form = PostForm()

        return render(request, "posts/new_post.html", {'form': form})

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
