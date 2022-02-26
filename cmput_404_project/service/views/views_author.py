from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator, EmptyPage
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.db.models import F

from social_distribution.models import Author
from accounts.forms import AuthorChangeForm

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


@require_http_methods(["GET", "POST"])
def author_detail(request, author_id):
    '''
    GET: Returns JSON response of the detail of the author with author_id.
    POST: Update author_id's profile and returns json response of the author's updated details.
    '''
    author = get_object_or_404(Author, pk=author_id)
    if request.method == 'GET':
        return JsonResponse(get_author_detail(author))
    else:
        # TODO test POST request
        if not request.user.is_authenticated():
            return render(request, '/accounts/login/')     # TODO change redirect url 
        form = AuthorChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            author.first_name = form.cleaned_data['first_name']
            author.last_name = form.cleaned_data['last_name']
            author.github = form.cleaned_data["github"]
            author.profile_image = form.cleaned_data['profile_image']
            author.save(update_fields=['first_name', 'last_name', 'github', 'profile_image'])

            return HttpResponseRedirect(f'/service/authors/{author_id}')


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
