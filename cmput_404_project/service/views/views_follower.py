import json 

from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse, Http404
from django.views import View

from service.server_authorization import is_server_authorized, is_local_server, get_401_response
from social_distribution.models import Author, Follower


class FollowersView(View):
    http_method_names = ['get', 'head', 'options']

    def get(self, request, *args, **kwargs):
        '''
        GET [local, remote]: Returns JSON response of the details of the author_id's followers.

        Returns:
            - 200: if successful
            - 401: if server is not authorized
            - 404: if author does not exist
        '''
        if not is_server_authorized(request):
            return get_401_response()

        return JsonResponse(self._get_followers(kwargs.get('author_id', '')))
    
    def head(self, request, *args, **kwargs):
        '''
        Handles HEAD request the same GET request.

        Returns:
            - 200: if successful
            - 401: if server is not authorized
            - 404: if author does not exist
        '''
        if not is_server_authorized(request):
            return get_401_response()

        response = HttpResponse()
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Length'] = str(len(bytes(json.dumps(self._get_followers(kwargs.get('author_id', ''))), 'utf-8')))
        return response

    def _get_followers(self, author_id) -> dict:
        '''
        Returns a dict containing followers list
        '''
        author = get_object_or_404(Author, pk=author_id)
        followers = Follower.objects.filter(target_author=author)
        data = {}
        data['type'] = 'followers'
        data['count'] = followers.count()
        data['items'] = [follower.get_detail_dict() for follower in followers]
        return data


class FollowerView(View):
    http_method_names = ['get', 'head', 'options', 'delete', 'put']

    def get(self, request, *args, **kwargs):
        '''
        GET [local, remote]: check if foreign_author_id is a follower of author_id

        Returns:
            - 200: if foreign_author_id is a follower of author_id
            - 401: if server is not authorized
            - 404: if foreign_author_id is not a follower of author_id, 
                    or if author with author_id does not exist
        '''
        if not is_server_authorized(request):
            return get_401_response()

        author_id = kwargs.get('author_id', '')
        foreign_author_id = kwargs.get('foreign_author_id', '' )
        author = get_object_or_404(Author, pk=author_id)
        if Follower.objects.filter(target_author=author, source_author_id=foreign_author_id).exists():
            return HttpResponse('The follower exists in this author.')
        return Http404('The follower does not exist in this author')


    def delete(self, request, *args, **kwargs):
        '''
        DELETE [local]: remove foreign_author_id as a follower of author_id

        Returns:
            - 204: if deleted successfully
            - 401: if server is not authorized 
            - 404: if foreign_author_id is not a follower of author_id, 
                    or if author with author_id does not exist,
                    or if author with foreign_author_id does not exist
        '''
        if not is_local_server(request):
            return get_401_response()

        author_id = kwargs.get('author_id', '')
        foreign_author_id = kwargs.get('foreign_author_id', '' )
        author = get_object_or_404(Author, pk=author_id)
        follower = get_object_or_404(Follower, target_author=author, source_author_id=foreign_author_id)
        follower.delete()
        return HttpResponse('Follower successfully deleted from the author', status=204)

        
    def put(self, request, *args, **kwargs):
        '''
        PUT [local]: add foreign_author_id as a follower of author_id.

        You must provide a JSON object of the foreign_author_id's info.
        See 'Example response' in https://github.com/3662/cmput404-project/wiki/Single-Author-API to look at the structure

        Note: Author must be authenticated.

        Returns:
            - 201: if the follower is successfully added to the author
            - 400: if author object is invalid
            - 401: if server is not authorized 
            - 403: if the author is not authenticated, or host is not local
            - 404: if author with author_id or foreign_author_id does not exist 
        '''
        if not is_local_server(request):
            return get_401_response()

        status_code = 201
        if not request.user.is_authenticated:
            status_code = 403
            message = "You do not have permission to add a follower from this author."
            return HttpResponse(message, status=status_code)     

        author_id = kwargs.get('author_id', '')
        foreign_author_id = kwargs.get('foreign_author_id', '' )
        author = get_object_or_404(Author, pk=author_id)

        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.decoder.JSONDecodeError:
            status_code = 400
            return HttpResponse('Invalid json', status=status_code)

        Follower.objects.create(target_author=author,
                                source_author_id=foreign_author_id,
                                source_author_url=data['id'])

        return HttpResponse('Follower successfully added to the author', status=status_code)
        









