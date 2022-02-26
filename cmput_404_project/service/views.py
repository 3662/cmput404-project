from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage
from django.http import Http404, JsonResponse

from social_distribution.models import Author

DEFAULT_PAGE = 1
DEFAULT_SIZE = 25

def authors(request):
    page = int(request.GET.get('page', DEFAULT_PAGE))
    size = int(request.GET.get('size', DEFAULT_SIZE))

    try:
        authors = Paginator(Author.objects.all(), size).page(page)
    except EmptyPage:
        raise Http404('Page does not exist')
    
    data = dict()
    data['type'] = 'authors'
    data['items'] = []
    author_d = {}
    for author in authors:
        author_d['type'] = 'author'
        author_d['id'] = f"{author.host}authors/{author.id}"
        data['url'] = f"{author.host}authors/{author.id}"
        author_d['host'] = author.host
        author_d['displayName'] = author.get_full_name()
        author_d['github'] = author.github
        author_d['profileImage'] = author.profile_image

        data['items'].append(author_d)
        author_d = {}
    
    return JsonResponse(data)
