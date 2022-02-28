from django.shortcuts import render,redirect
from social_distribution.models import Author,Friends
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView

# Create your views here.

# def index(request):
#     # return HttpResponse("Hello, world. You're at the authors index.")
#     return render(request, 'authors/authors_base.html')

"""
Retrieve and display all authors saved as Author model instances in the database
"""
def display_authors(request):
    authors = Author.objects.all()

    return render(request, 'authors/authors_base.html', {'authors': authors})

"""
Retrieve and display a single author
"""
def display_author(request, id):
    author = Author.objects.get(id=id)

    return HttpResponse(author)


def author_list_view(request):
    qs = Author.objects.all().exclude(username=request.user)
    sender = Author.objects.get(username=request.user)
    s_qs = Friends.objects.filter(sender=sender, status='send').values_list('receiver',flat=True)
    r_qs = Friends.objects.filter(sender=sender, status='accepted').values_list('receiver',flat=True)
    context = {'authors': qs,
               'friend': request.user,
               'f_send': s_qs,
               'f_accept': r_qs,
               }
    return render(request, 'authors/author_list.html', context)

def author_friend_view(request):
    if request.method == "POST":
        user = request.POST.get('user')
        action_flag = request.POST.get('action_flag')

        recv = Author.objects.get(id=user)
        send = Author.objects.get(username=request.user)
        if action_flag=='I':
            friend, inserted = Friends.objects.get_or_create(receiver=recv, sender=send,status='send')
            #if not inserted:
            if inserted:
                #post.liked.remove(request.user)
                #rec=Like.objects.get(author=request.user, post=post)
                #rec.delete()
            #else:
                #post.liked.add(request.user)
                #recv.save()
                friend.save()
        if action_flag=='R':
            Friends.objects.get(receiver=recv, sender=send,status='send').delete()
            #friend.delete()
        if action_flag=='F':
            Friends.objects.get(receiver=recv, sender=send,status='accepted').delete()
            send.followers.remove(recv)

    return redirect('/authors/author_list')
    #return redirect('/')


def pending_action_list_view(request):
    me = Author.objects.get(username=request.user)
    qs = Author.objects.all().exclude(username=request.user)
    f_qs = Friends.objects.filter(status='send',receiver=me).exclude(sender=me).values_list('sender',flat=True)
    context = {
        'authors':qs,
        'f_qs':f_qs,
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
            #me.followers.remove(sender)

    return redirect('/authors/pending_action_list_view')

