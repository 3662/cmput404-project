import json 

from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse, Http404
from django.views import View

from social_distribution.models import Author
from .views_author import get_author_detail


class FollowersView(View):
    http_method_names = ['get', 'head', 'options']

    def get(self, request, *args, **kwargs):
        '''
        GET [local, remote]: Returns JSON response of the details of the author_id's followers.

        Returns:
            - 200: if successful
            - 404: if author does not exist
        '''
        return JsonResponse(self._get_followers(kwargs.get('author_id', '')))
    
    def head(self, request, *args, **kwargs):
        '''
        Handles HEAD request the same GET request.

        Returns:
            - 200: if successful
            - 404: if author does not exist
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
        '''
        GET [local, remote]: check if foreign_author_id is a follower of author_id

        Returns:
            - 200: if foreign_author_id is a follower of author_id
            - 404: if foreign_author_id is not a follower of author_id, 
                    or if author with author_id does not exist
        '''
        author_id = kwargs.get('author_id', '')
        foreign_author_id = kwargs.get('foreign_author_id', '' )
        author = get_object_or_404(Author, pk=author_id)
        if author.followers.filter(id=foreign_author_id).exists():
            return HttpResponse('The follower author exists in this author.')
        return Http404('The follower author does not exist in this author')


    def delete(self, request, *args, **kwargs):
        '''
        DELETE [local]: remove foreign_author_id as a follower of author_id

        Returns:
            - 200: if deleted successfully
            - 404: if foreign_author_id is not a follower of author_id, 
                    or if author with author_id does not exist,
                    or if author with foreign_author_id does not exist
        '''
        author_id = kwargs.get('author_id', '')
        foreign_author_id = kwargs.get('foreign_author_id', '' )
        author = get_object_or_404(Author, pk=author_id)
        foreign_author = get_object_or_404(Author, pk=foreign_author_id)
        author.followers.remove(foreign_author)
        return HttpResponse('Follower successfully deleted from the author')

        
    def put(self, request, *args, **kwargs):
        '''
        PUT [local]: add foreign_author_id as a follower of author_id.

        Note: Author must be authenticated.

        Returns:
            - 201: if the follower is successfully added to the author
            - 403: if the author is not authenticated
            - 404: if author with author_id or foreign_author_id does not exist 
        '''
        status_code = 201
        if not request.user.is_authenticated:
            status_code = 403
            message = "You do not have permission to add a follower from this author."
            return HttpResponse(message, status=status_code)     

        author_id = kwargs.get('author_id', '')
        foreign_author_id = kwargs.get('foreign_author_id', '' )
        author = get_object_or_404(Author, pk=author_id)
        foreign_author = get_object_or_404(Author, pk=foreign_author_id)
        author.followers.add(foreign_author)
        return HttpResponse('Follower successfully added to the author', status=status_code)
        









