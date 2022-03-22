import json

from django.shortcuts import get_object_or_404
from django.views import View
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ObjectDoesNotExist

from social_distribution.models import Author, Inbox, InboxItem

class LikedView(View):

    http_method_names = ['get', 'head', 'options']

    def get(self, request, *args, **kwargs):
        '''
        GET [local, remote]: returns a list of likes of what public objects AUTHOR_ID liked.

        Returns:
            - 200: if successful
            - 404: if the author does not exist
        '''
        author_id = kwargs.get('author_id', '')
        return JsonResponse(self._get_public_likes(author_id))

        
    def head(self, request, *args, **kwargs):
        '''
        Handles HEAD request of the same GET request.

        Returns:
            - 200: if successful
            - 404: if the author does not exist
        '''
        author_id = kwargs.get('author_id', '')
        data_json = json.dumps(self._get_public_likes(author_id))
        response = HttpResponse()
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Length'] = str(len(bytes(data_json, 'utf-8')))
        return response


    def _get_public_likes(self, author_id) -> dict:
        '''
        Returns a dict that contains a list of public Likes made by author_id. 
        '''

        author = get_object_or_404(Author, id=author_id)

        try:
            inbox = Inbox.objects.get(author=author)
        except ObjectDoesNotExist:
            # create an inbox for this author if it doesn't exist
            inbox = Inbox.objects.create(author=author)

        items = InboxItem.filter(inbox=inbox) 

        data = {}
        data['type'] = 'liked'
        data['items'] = [item.get_detail_dict() 
                         for item in items 
                         if item.is_object_public()]

        return data
