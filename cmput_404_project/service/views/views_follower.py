import json 

from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse, Http404
from django.views import View

from social_distribution.models import Author
from .views_author import get_author_detail


class FollowersDetailView(View):
    http_method_names = ['get', 'head', 'options']

    def get(self, request, *args, **kwargs):
        '''
        Returns JSON response of the details of the author_id's followers.
        '''
        return JsonResponse(self._get_followers(kwargs.get('author_id', '')))
    
    def head(self, request, *args, **kwargs):
        '''
        Handles HEAD request the same GET request.
        '''
        response = HttpResponse()
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Length'] = str(len(bytes(json.dumps(self._get_followers(kwargs.get('author_id', ''))), 'utf-8')))
        return response


    def _get_followers(self, author_id) -> dict:
        '''
        Returns a dict containing followers list
        '''
        author = get_object_or_404(Author, pk=author_id)
        data = {}
        data['type'] = 'followers'
        data['items'] = [get_author_detail(follower) for follower in author.followers.all()]
        return data


class FollowerView(View):
    http_method_names = ['get', 'head', 'options', 'delete', 'put']

    def get(self, request, *args, **kwargs):
        # TODO implement this method
        pass

    def delete(self, request, *args, **kwargs):
        author_id = kwargs.get('author_id', '')
        foreign_author_id = kwargs.get('foreign_author_id', '' )
        author = get_object_or_404(Author, pk=author_id)
        foreign_author = get_object_or_404(Author, pk=foreign_author_id)
        author.followers.remove(foreign_author)
        return HttpResponse('Follower successfully deleted')
        
    def put(self, request, *args, **kwargs):
        '''
        Add foreign_author_id as a follower of author_id.

        Note: must be authenticated.
        '''
        if not request.user.is_authenticated:
            return Http404('Must be signed in')

        author_id = kwargs.get('author_id', '')
        foreign_author_id = kwargs.get('foreign_author_id', '' )
        author = get_object_or_404(Author, pk=author_id)
        foreign_author = get_object_or_404(Author, pk=foreign_author_id)
        author.followers.add(foreign_author)
        return HttpResponse('Follower successfully added')
        









