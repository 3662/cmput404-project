from django.shortcuts import render
from .models import Author
from django.http import HttpResponse

# Create your views here.

# def index(request):
#     # return HttpResponse("Hello, world. You're at the authors index.")
#     return render(request, 'authors/authors_base.html')

"""
Retrieve and display all authors saved as Author model instances in the database
"""
def display_authors(request):
    authors = Author.objects.all().order_by('display_name')

    return render(request, 'authors/authors_base.html', {'authors': authors})

"""
Retrieve and display a single author
"""
def display_author(request, slug):
    author = Author.objects.get(slug=slug)

    return HttpResponse(author)
