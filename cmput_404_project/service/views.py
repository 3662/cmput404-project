from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import JsonResponse

from social_distribution.models import Author


def authors_json(request):
    # TODO pagination
    authors = Author.objects.all()
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
