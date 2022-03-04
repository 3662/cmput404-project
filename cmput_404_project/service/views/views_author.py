import json 

from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator, EmptyPage
from django.http import Http404, HttpResponseRedirect, JsonResponse, HttpResponse
from django.views import View

from social_distribution.models import Author
from accounts.forms import AuthorChangeForm


class AuthorsDetailView(View):

    DEFAULT_PAGE = 1
    DEFAULT_SIZE = 25

    http_method_names = ['get', 'head', 'options']

    def get(self, request, *args, **kwargs):
        '''
        Returns JSON response of the details of the authors.

        Default page = 1, size = 25
        '''
        return JsonResponse(self._get_authors(request))

    def head(self, request, *args, **kwargs):
        '''
        Handles HEAD request the same GET request.
        '''
        response = HttpResponse()
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Length'] = str(len(bytes(json.dumps(self._get_authors(request)), 'utf-8')))
        return response

    def _get_authors(self, request) -> dict:
        page = int(request.GET.get('page', self.DEFAULT_PAGE))
        size = int(request.GET.get('size', self.DEFAULT_SIZE))

        try:
            authors = Paginator(Author.objects.all(), size).page(page)
        except EmptyPage:
            raise Http404('Page does not exist')

        data = {}
        data['type'] = 'authors'
        data['items'] = [get_author_detail(author) for author in authors]

        return data


class AuthorDetailView(View):
    http_method_names = ['get', 'head', 'post', 'options']

    def get(self, request, *args, **kwargs):
        '''
        Returns JSON response of the detail of the author with author_id.
        '''
        author = get_object_or_404(Author, pk=kwargs.get('author_id', ''))
        return JsonResponse(get_author_detail(author))

    def head(self, request, *args, **kwargs):
        '''
        Handles HEAD request the same GET request.
        '''
        author = get_object_or_404(Author, pk=kwargs.get('author_id', ''))
        response = HttpResponse()
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Length'] = str(len(bytes(json.dumps(get_author_detail(author)), 'utf-8')))
        return response

    def post(self, request, *args, **kwargs):
        '''
        Update author_id's profile and returns json response of the author's updated details.
        '''
        author_id = kwargs.pop('author_id', '')
        author = get_object_or_404(Author, pk=author_id)
        if not request.user.is_authenticated:
            status_code = 403
            message = "You do not have permission to update this author's post."
            return HttpResponse(message, status=status_code)     

        form = AuthorChangeForm(request.POST)
        if form.is_valid():
            author.first_name = form.cleaned_data['first_name']
            author.last_name = form.cleaned_data['last_name']
            author.github = form.cleaned_data["github"]
            author.profile_image = form.cleaned_data['profile_image']
            author.save(update_fields=['first_name', 'last_name', 'github', 'profile_image'])

            return HttpResponse("Author is successfully updated.")

        status_code = 400
        return HttpResponse('The form is not valid.', status=status_code)     


def get_author_detail(author) -> dict:
    '''
    Returns a dict containing the author information.
    '''
    author_d = {}
    author_d['type'] = 'author'
    author_d['id'] = author.get_id_url()
    author_d['url'] = author.get_profile_url()
    author_d['host'] = author.host
    author_d['displayName'] = author.get_full_name()
    author_d['github'] = author.github
    author_d['profileImage'] = author.profile_image

    return author_d
