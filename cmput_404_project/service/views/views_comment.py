import json

from django.shortcuts import get_object_or_404
from django.core.paginator import EmptyPage
from django.http import JsonResponse, HttpResponse, Http404
from django.views import View
from django.core.exceptions import ValidationError

from posts.forms import CommentForm
from social_distribution.models import Author, Post, Comment


class CommentsView(View):

    DEFAULT_PAGE = 1
    DEFAULT_SIZE = 5

    http_method_names = ['get', 'head', 'options', 'post']

    def get(self, request, *args, **kwargs):
        '''
        GET [local, remote]: get the list of comments of the post whose id is post_id (paginated)

        Returns:
            - 200: if successful
            - 404: if author or post does not exist
        '''
        author_id = kwargs.get('author_id', '')
        post_id = kwargs.get('post_id', '')
        return JsonResponse(self._get_comments(request, author_id, post_id))

    def head(self, request, *args, **kwargs):
        '''
        Handles HEAD request of the same GET request.

        Returns:
            - 200: if successful
            - 404: if author or post does not exist
        '''
        author_id = kwargs.get('author_id', '')
        post_id = kwargs.get('post_id', '')
        data_json = json.dumps(self._get_comments(request, author_id, post_id))
        response = HttpResponse()
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Length'] = str(len(bytes(data_json, 'utf-8')))
        return response

    def post(self, request, *args, **kwargs):
        '''
        POST [local]: if you post an object of “type”:”comment”, it will add your comment to the post whose id is post_id

        Returns:
            - 201: if the comment is added to the post
            - 400: if the comment data is invalid
            - 404: if the post or author does not exist
        '''
        author_id = kwargs.get('author_id', '')
        post_id = kwargs.get('post_id', '')
        author = get_object_or_404(Author, id=author_id)
        post = get_object_or_404(Post, id=post_id, author=author)

        data = json.loads(request.body)
        # assume the data has a format of the one in the requirements but without 'published' and 'id' fields.
        # assume the comment object has not been created yet
        try:
            if data['type'] != 'comment':
                raise ValueError()
            content_type = data['contentType']
            content = data['comment']
            comment_author_id_url = data['author']['id']
            comment_author_id = comment_author_id_url.split('/')[-1]
            comment_author = None
            if Author.objects.filter(id=comment_author_id).exists():
                comment_author = Author.objects.get(id=comment_author_id)

        except (KeyError, ValueError):
            status_code = 400
            return HttpResponse('The form is invalid', status=status_code)     
        else:
            status_code = 201
            comment = Comment.objects.create(author=comment_author, author_url=comment_author_id_url, post=post, content_type=content_type, content=content)
            return JsonResponse(comment.get_detail_dict(), status=status_code)

        
    def _get_comments(self, request, author_id, post_id):
        '''
        Returns a dict that contains a list of comments.
        '''
        page = int(request.GET.get('page', self.DEFAULT_PAGE))
        size = int(request.GET.get('size', self.DEFAULT_SIZE))

        post = get_object_or_404(Post, pk=post_id, author_id=author_id)

        try:
            return post.get_comments_src_dict(page, size)
        except EmptyPage:
            raise Http404('Page does not exist')
        

