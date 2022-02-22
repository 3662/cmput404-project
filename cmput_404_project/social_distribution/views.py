from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import JsonResponse

from .models import Author

from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder

def authors(request):
    authors = Author.objects.all()
    data = dict()
    data['type'] = 'authors'
    data['items'] = []
    for author in authors:
        data['type'] = author
        data['id'] = author.get('id')
    


    return JsonResponse(data)
