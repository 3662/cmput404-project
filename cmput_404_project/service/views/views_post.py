import json 

from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from django.http import JsonResponse, HttpResponse, Http404
from django.views import View

from social_distribution.models import Author, Post
from .views_author import get_author_detail

DEFAULT_PAGE = 1
DEFAULT_SIZE = 15


class PostView(View):
    http_method_names = ['get', 'head', 'options', 'post', 'delete', 'put']

    def get(self, request, *args, **kwargs):
        '''
        GET [local, remote]: Returns a JSON respone that contains the public post whose id is post_id.
        '''

        
        raise NotImplementedError()

    def head(self, request, *args, **kwargs):
        '''
        Handles HEAD request of the same GET request.
        '''
        raise NotImplementedError()

    def post(self, request, *args, **kwargs):
        '''
        POST [local]: Updates the post whose id is post_id.

        Note: author must be authenticated.
        '''
        raise NotImplementedError()

    def delete(self, request, *args, **kwargs):
        '''
        DELETE [local]: removes the post whose id is post_id.
        '''
        raise NotImplementedError()

    def put(self, request, *args, **kwargs):
        '''
        PUT [local]: creates a post where its id is post_id.
        '''
        raise NotImplementedError()


class PostsView(View):
    http_method_names = ['get', 'head', 'options', 'post']

    def get(self, request, *args, **kwargs):
        '''
        GET [local, remote]: Returns a JSON response that contains a list of the 
        recent posts from author_id.
        '''
        author_id = kwargs.get('author_id', '')
        return JsonResponse(self._get_posts(request, author_id))

    def head(self, request, *args, **kwargs):
        '''
        Handles HEAD request of the same GET request.
        '''
        author_id = kwargs.get('author_id', '')
        data_json = json.dumps(self._get_posts(request, author_id))
        response = HttpResponse()
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Length'] = str(len(bytes(data_json, 'utf-8')))
        return response

    def post(self, request, *args, **kwargs):
        '''
        POST [local]: Creates an empty post. It only generates a new id. 
        '''
        author_id = kwargs.get('author_id', '')
        author = get_object_or_404(Author, pk=author_id)
        p = Post.objects.create(author=author)
        p.save()
        return JsonResponse(get_post_detail(p, author))

    def _get_posts(self, request, author_id) -> dict:
        '''
        Returns a dict that contains a list of posts.
        '''
        page = int(request.GET.get('page', DEFAULT_PAGE))
        size = int(request.GET.get('size', DEFAULT_SIZE))

        author = get_object_or_404(Author, pk=author_id)
        try:
            q = Post.objects.all().filter(author=author)
            q = q.filter(visibility='PUBLIC')
            q = q.order_by('-published')
            posts = Paginator(q, size).page(page)
        except EmptyPage:
            raise Http404('Page does not exist')

        data = {}
        data['type'] = 'posts'
        data['items'] = [get_post_detail(p, author) for p in posts]
        return data



def get_post_detail(post, author) -> dict:
    '''
    Returns a dict that contains a post detail.
    '''
    d = {}
    d['type'] = 'post'
    d['title'] = post.title
    d['id'] = f"{author.host}authors/{author.id}/posts/{post.id}"
    d['source'] = post.source
    d['origin'] = post.origin
    d['description'] = post.description
    d['contentType'] = post.content_type
    d['author'] = get_author_detail(author)
    d['categories'] = [] if post.categories == '' else post.categories.strip().split(',')
    # TODO comments

    return d

        
