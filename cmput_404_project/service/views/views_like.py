import json

from django.shortcuts import get_object_or_404
from django.views import View
from django.http import JsonResponse, HttpResponse, Http404

from service.server_authorization import is_server_authorized, get_401_response
from social_distribution.models import Author, Post, Like, Comment


class PostLikesView(View):

    http_method_names = ['get', 'head', 'options']

    def get(self, request, *args, **kwargs):
        '''
        GET [local, remote] returns a list of likes from other authors on AUTHOR_ID's post POST_ID

        Returns:
            - 200 if successful
            - 401: if server is not authorized
            - 404 if post does not exist
        '''
        if not is_server_authorized(request):
            return get_401_response()

        author_id = kwargs.get('author_id', '')
        post_id = kwargs.get('post_id', '')
        return JsonResponse(self._get_likes(author_id, post_id))

    def head(self, request, *args, **kwargs):
        '''
        Handles HEAD request of the same GET request.

        Returns:
            - 200: if successful
            - 401: if server is not authorized
            - 404: if post does not exist
        '''
        if not is_server_authorized(request):
            return get_401_response()

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
        post_author = get_object_or_404(Author, pk=author_id)
        post = get_object_or_404(Post, pk=post_id, author=post_author)
        likes = Like.objects.filter(object_type=Like.OBJECT_TYPE_CHOICES[0][0], object_url=post.get_id_url()).all()

        data = {}
        data['type'] = 'liked'
        data['items'] = [l.get_detail_dict() for l in likes]
        return data


class CommentLikesView(View):

    http_method_names = ['get', 'head', 'options']

    def get(self, request, *args, **kwargs):
        '''
        GET [local, remote] returns a list of likes from other authors on AUTHOR_ID's post POST_ID comment COMMENT_ID.

        Returns:
            - 200 if successful
            - 401: if server is not authorized
            - 404 if post does not exist
        '''
        if not is_server_authorized(request):
            return get_401_response()

        author_id = kwargs.get('author_id', '')
        post_id = kwargs.get('post_id', '')
        comment_id = kwargs.get('comment_id', '')
        return JsonResponse(self._get_likes(author_id, post_id, comment_id))


    def head(self, request, *args, **kwargs):
        '''
        Handles HEAD request of the same GET request.

        Returns:
            - 200: if successful
            - 401: if server is not authorized
            - 404: if post does not exist
        '''
        if not is_server_authorized(request):
            return get_401_response()

        author_id = kwargs.get('author_id', '')
        post_id = kwargs.get('post_id', '')
        comment_id = kwargs.get('comment_id', '')
        data_json = json.dumps(self._get_likes(author_id, post_id, comment_id))
        response = HttpResponse()
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Length'] = str(len(bytes(data_json, 'utf-8')))
        return response


    def _get_likes(self, author_id, post_id, comment_id):
        '''
        Returns a dict that contains a list of likes.
        '''
        post_author = get_object_or_404(Author, pk=author_id)
        post = get_object_or_404(Post, pk=post_id, author=post_author)
        comment = get_object_or_404(Comment, pk=comment_id, post=post)
        likes = Like.objects.filter(object_type=Like.OBJECT_TYPE_CHOICES[1][0], object_url=comment.get_id_url()).all()

        data = {}
        data['type'] = 'liked'
        data['items'] = [l.get_detail_dict() for l in likes]
        return data