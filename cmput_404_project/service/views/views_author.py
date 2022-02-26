from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator, EmptyPage
from django.http import Http404, JsonResponse

from social_distribution.models import Author

DEFAULT_PAGE = 1
DEFAULT_SIZE = 25


@require_http_methods(["GET"])
def authors_detail(request):
    '''
    Returns JSON response of the details of the authors.

    Default page = 1, size = 25
    '''
    page = int(request.GET.get('page', DEFAULT_PAGE))
    size = int(request.GET.get('size', DEFAULT_SIZE))

    try:
        authors = Paginator(Author.objects.all(), size).page(page)
    except EmptyPage:
        raise Http404('Page does not exist')
    
    data = {}
    data['type'] = 'authors'
    data['items'] = [get_author_detail(author) for author in authors]
    
    return JsonResponse(data)


@require_http_methods(["GET"])
def author_detail(request, author_id):
    '''
    Returns JSON response of the detail of the author with author_id.
    '''
    author = get_object_or_404(Author, pk=author_id)
    return JsonResponse(get_author_detail(author))


def get_author_detail(author) -> dict:
    '''
    Returns a dict containing the author information.
    '''
    author_d = {}
    author_d['type'] = 'author'
    author_d['id'] = f"{author.host}authors/{author.id}"
    author_d['url'] = f"{author.host}authors/{author.id}"
    author_d['host'] = author.host
    author_d['displayName'] = author.get_full_name()
    author_d['github'] = author.github
    author_d['profileImage'] = author.profile_image

    return author_d
