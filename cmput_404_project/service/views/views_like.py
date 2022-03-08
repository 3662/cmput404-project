import json

from django.shortcuts import get_object_or_404
from django.views import View
from django.http import JsonResponse, HttpResponse, Http404

from social_distribution.models import Author, Post, Like 

class PostLikesView(View):

    http_method_names = ['get', 'head', 'options']

    def get(self, request, *args, **kwargs):
        '''
        GET [local, remote] returns a list of likes from other authors on AUTHOR_ID's post POST_ID

        Returns:
            - 200 if successful
            - 404 if post does not exist
        '''
        author_id = kwargs.get('author_id', '')
        post_id = kwargs.get('post_id', '')
        return JsonResponse(self._get_likes(author_id, post_id))

    def head(self, request, *args, **kwargs):
        '''
        Handles HEAD request of the same GET request.

        Returns:
            - 200: if successful
            - 404: if post does not exist
        '''
        author_id = kwargs.get('author_id', '')
        post_id = kwargs.get('post_id', '')
        data_json = json.dumps(self._get_likes(author_id, post_id))
        response = HttpResponse()
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Length'] = str(len(bytes(data_json, 'utf-8')))
        return response


    def _get_likes(self, author_id, post_id):
        '''
        Returns a dict that contains a list of likes.
        '''
        get_object_or_404(Post, pk=post_id, author_id=author_id)
        likes = Like.objects.filter(object_type=Like.OBJECT_TYPE_CHOICES[0][0], object_id=post_id).all()

        data = {}
        data['type'] = 'liked'
        data['items'] = [l.get_detail_dict() for l in likes]
        return data
