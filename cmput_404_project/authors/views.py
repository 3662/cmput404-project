from django.shortcuts import render
from social_distribution.models import Author
from django.http import HttpResponse

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
