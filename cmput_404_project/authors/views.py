from django.shortcuts import render, redirect
from social_distribution.models import Author, Friends, FollowRequest, Post, Like
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from service.models import ServerNode
import requests
from urllib.parse import urlparse


# Create your views here.

# def index(request):
#     # return HttpResponse("Hello, world. You're at the authors index.")
#     return render(request, 'authors/authors_base.html')


def display_profile(request):
    not_found = True
    author = is_my_profile = host_is_local = friend_status = None

    url = request.GET.get('url')
    if url:
        host = urlparse(url).netloc
        node = None
        for n in ServerNode.objects.all():
            print(n.host, url)
            if url.startswith(n.host):
                node = n
                break
        if node:
            auth = (node.sending_username, node.sending_password)
            response = requests.get(url, auth=auth)
            try:
                author = response.json()
                not_found = False
                myself = Author.objects.filter(id=request.user.id).get()
                is_my_profile = myself.id == url
                friend_status = '1' # TODO: Check the status of friendship
                host_is_local =  host == node.host
            except:
                pass

    posts = []
    for node in ServerNode.objects.all():
        if node.is_local:
            continue
        url = f'{node.host}/authors/'
        auth = (node.sending_username, node.sending_password)
        response = requests.get(url, auth=auth)
        try:
            data = response.json()
            authors = data['items']
            for a in authors:
                if a['id'] == author['id']:
                    url = author['url'] + '/posts/'
                    response = requests.get(url, auth=auth)
                    try:
                        data = response.json()
                        posts.extend(data['items'])
                    except Exception as e:
                        print('Error: URL =', url)
                        print(e)
        except Exception as e:
            print('Error: URL =', url)
            print(e)

    context = {
        'not_found': not_found,
        'author': author,
        'is_my_profile': is_my_profile,
        'friend_status': friend_status,
        'host_is_local': host_is_local,
        'posts': posts,
    }

    return render(request, 'authors/profile.html', context=context)

"""
Retrieve and display all authors saved as Author model instances in the database
"""
def display_authors(request):    
    print('entered author_list_view')
    nodes = []
    for node in ServerNode.objects.all():
        print('host username:password =', node.host, node.sending_username, node.sending_password)

        if node.is_local:
            authors = [author.get_detail_dict() for author in Author.objects.all()]
        else:
            url = f'{node.host}/authors/'
            auth = (node.sending_username, node.sending_password)
            response = requests.get(url, auth=auth)
            try:
                data = response.json()
                authors = data['items']
            except Exception as e:
                print(f'Failed to get authors from {url}')
                print(f'Error: {e}')
                print(f'response.text = {response.text}')
                continue
        # print(authors)
        nodes.append({
            'is_local': node.is_local,
            'host': node.host,
            'authors': authors,
        })
    
    return render(request, 'authors/authors_base.html', {'nodes': nodes})


"""
Retrieve and display a single author
"""
def display_author(request, id):
    author = Author.objects.get(id=id)
    posts = Post.objects.filter(author=author).order_by('-published')
    sender = Author.objects.get(username=request.user)
    s_qs = Friends.objects.filter(sender=sender, status='send').values_list('receiver', flat=True)
    r_qs = Friends.objects.filter(sender=sender, status='accepted').values_list('receiver', flat=True)
    cross_qs = Friends.objects.filter(receiver=sender, status='accepted').values_list('sender', flat=True)
    context = {
        'is_my_profile': request.user.id == id,
        'author': author,
        'posts': posts,
        'f_send': s_qs,
        'f_accept': r_qs,
        'cross_qs': cross_qs,
        'friend': request.user,
        'sender': sender,
        'host_is_local': True,
    }
    return render(request, 'authors/profile.html', context=context)


def author_list_view(request):
    qs = Author.objects.all().exclude(username=request.user)
    sender = Author.objects.get(username=request.user)
    s_qs = Friends.objects.filter(sender=sender, status='send').values_list('receiver', flat=True)
    r_qs = Friends.objects.filter(sender=sender, status='accepted').values_list('receiver', flat=True)
    cross_qs = Friends.objects.filter(receiver=sender, status='accepted').values_list('sender', flat=True)
    context = {'authors': qs,
               'friend': request.user,
               'f_send': s_qs,
               'f_accept': r_qs,
               'cross_qs': cross_qs,
               }
    return render(request, 'authors/author_list.html', context)


def author_friend_view(request):
    if request.method == "POST":
        user = request.POST.get('user')
        action_flag = request.POST.get('action_flag')
        recv = Author.objects.get(id=user)
        send = Author.objects.get(username=request.user)

        if action_flag == 'I':
            friend, inserted = Friends.objects.get_or_create(receiver=recv, sender=send,status='send')
            if inserted:
                #post.liked.remove(request.user)
                #rec=Like.objects.get(author=request.user, post=post)
                #rec.delete()
            #else:
                #summary = str(request.user) + " wants to follow " + str(recv.username)
                follower, inserted = FollowRequest.objects.get_or_create(to_author=recv, from_author=send) #, summary=summary)
                friend.save()
                follower.save()
        if action_flag == 'R':
            #if (Friends.objects.get(receiver=recv, sender=send,status='send').count())>0:
            Friends.objects.get(receiver=recv, sender=send, status='send').delete()
            #if FollowRequest.objects.get(to_author=recv, from_author=send).count() > 0:
            FollowRequest.objects.get(to_author=recv, from_author=send).delete()
        if action_flag == 'F':
            Friends.objects.get(receiver=recv, sender=send, status='accepted').delete()
            FollowRequest.objects.get(to_author=recv, from_author=send).delete()
            send.followers.remove(recv)

    return redirect('/authors/author_list')


def pending_action_list_view(request):
    me = Author.objects.get(username=request.user)
    qs = Author.objects.all().exclude(username=request.user)
    f_qs = Friends.objects.filter(status='send', receiver=me).exclude(sender=me).values_list('sender', flat=True)
    context = {
        'authors': qs,
        'f_qs': f_qs,
    }
    return render(request, 'authors/pending_response.html', context)


def pending_action_view(request):
    if request.method == "POST":
        user = request.POST.get('user')
        accept = request.POST.get('accept')
        sender = Author.objects.get(id=user)
        me = Author.objects.get(username=request.user)
        if accept == 'A':
            friend = Friends.objects.filter(receiver=me, sender=sender,status='send').update(status='accepted')
            me.followers.add(sender)
        if accept == 'R':
            friend = Friends.objects.filter(receiver=me, sender=sender,status='send')
            friend.delete()

    return redirect('/authors/pending_action_list_view')


def follower_view(request, id):
    authors = Author.objects.all()
    f_qs = Author.objects.filter(username=request.user).values_list('followers', flat=True)
    context = {
        'authors': authors,
        'f_qs': f_qs,
    }
    furl = f'service/author/{request.user.id}/follower/followers_list.html'
    return render(request, 'authors/followers_list.html', {'user_id': id})


def follower_view1(request):
    author = Author.objects.get(username=request.user)
    f_qs = FollowRequest.objects.filter(to_author=author)
    return render(request, 'authors/follower_list1.html', {'f_qs': f_qs})


def friends_view(request):
    authors = Author.objects.all()
    return render(request, 'authors/follower_list.html', {'authors': authors})


def friends_view(request):
    f_qs_list = []
    authors = Friends.objects.filter(sender=request.user, status='accepted').values_list('receiver', flat=True)
    for qs in authors:
        cross_qs = Friends.objects.filter(sender=qs, receiver=request.user, status='accepted').count()
        if cross_qs > 0:
            f_qs_list.append(qs)
    f_qs = Author.objects.filter(id__in=f_qs_list)
    context = {
        'authors': authors,
        'f_qs': f_qs,
    }
    return render(request, 'authors/friends_list.html', context)


def author_profile_view(request):
    if request.method == "POST":
        user = request.POST.get('user')
        action_flag = request.POST.get('action_flag')
        recv = Author.objects.get(id=user)
        send = Author.objects.get(username=request.user)

        if action_flag == 'I':
            friend, inserted = Friends.objects.get_or_create(receiver=recv, sender=send,status='send')
            if inserted:
                #post.liked.remove(request.user)
                #rec=Like.objects.get(author=request.user, post=post)
                #rec.delete()
            #else:
                #summary = str(request.user) + " wants to follow " + str(recv.username)
                follower, inserted = FollowRequest.objects.get_or_create(to_author=recv, from_author=send) #, summary=summary)
                friend.save()
                follower.save()
        if action_flag == 'R':
            #if (Friends.objects.get(receiver=recv, sender=send,status='send').count())>0:
            Friends.objects.get(receiver=recv, sender=send, status='send').delete()
            #if FollowRequest.objects.get(to_author=recv, from_author=send).count() > 0:
            FollowRequest.objects.get(to_author=recv, from_author=send).delete()
        if action_flag == 'F':
            Friends.objects.get(receiver=recv, sender=send, status='accepted').delete()
            FollowRequest.objects.get(to_author=recv, from_author=send).delete()
            send.followers.remove(recv)

    return redirect(f'/authors/{user}')


def like_post2(request):
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
    return redirect(f'/authors/{post.author.id}')

def display_inbox(request):
    if not request.user.is_authenticated:
        status_code = 403
        message = 'You have to sign in to view the inbox.'
        message += '<br><a href="/">Go to homepage</a>'
        return HttpResponse(message, status=status_code)
    context = {
        'author_id': request.user.id,
        'author': request.user,
    }
    return render(request, 'authors/inbox.html', context)
