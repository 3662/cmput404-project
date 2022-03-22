import json

from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator, EmptyPage
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse, Http404
from django.views import View
from posts.forms import PostForm
from django.core.exceptions import ValidationError

from social_distribution.models import Author, Post


class PostView(View):
    http_method_names = ['get', 'head', 'options', 'post', 'delete', 'put']

    def get(self, request, *args, **kwargs):
        '''
        GET [local, remote]: Returns a JSON response with status code of 200 
                             that contains the public post whose id is post_id.
        
        Returns: 
            - 200: if successful
            - 404: if author or post does not exist
        '''
        author_id = kwargs.get('author_id', '')
        post_id = kwargs.get('post_id', '')
        author = get_object_or_404(Author, pk=author_id)
        post = get_object_or_404(Post, pk=post_id, author_id=author_id, visibility="PUBLIC")

        return JsonResponse(post.get_detail_dict())


    def head(self, request, *args, **kwargs):
        '''
        Handles HEAD request of the same GET request.

        Returns: 
            - 200: if the request is successful
            - 404: if author or post does not exist 
        '''
        author_id = kwargs.get('author_id', '')
        post_id = kwargs.get('post_id', '')
        author = get_object_or_404(Author, pk=author_id)
        post = get_object_or_404(Post, pk=post_id, author_id=author_id, visibility="PUBLIC")
        data_json = json.dumps(post.get_detail_dict())

        response = HttpResponse()
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Length'] = str(len(bytes(data_json, 'utf-8')))

        return response
        

    def post(self, request, *args, **kwargs):
        '''
        POST [local]: Updates the post whose id is post_id.

        Returns: 
            - 200: if the update is successful
            - 400: if the data is invalid
            - 403: if the user is not authenticated
            - 404: if author or post does not exist 
        '''
        author_id = kwargs.get('author_id', '')
        post_id = kwargs.get('post_id', '')
        post = get_object_or_404(Post, pk=post_id, author_id=author_id)
        if not request.user.is_authenticated:
            status_code = 403
            message = "You do not have permission to update this author's post."
            return HttpResponse(message, status=status_code)     

        form = PostForm(request.POST)
        if form.is_valid():
            self.update_post(post, form)

            return HttpResponse("Post is successfully updated.")

        status_code = 400
        return HttpResponse('The form is not valid.', status=status_code)     
            

    def delete(self, request, *args, **kwargs):
        '''
        DELETE [local]: removes the post whose id is post_id.

        Returns: 
            - 204: if the deletion was successful
            - 404: if author or post does not exist 
        '''
        author_id = kwargs.get('author_id', '')
        post_id = kwargs.get('post_id', '')
        author = Author.objects.get(id=author_id)
        post = get_object_or_404(Post, pk=post_id, author=author)
        post.delete()
        return HttpResponse('Post successfully deleted', status=204)


    def put(self, request, *args, **kwargs):
        '''
        PUT [local]: creates a post where its id is post_id, if the given form data is valid.

        Note: if the post already exists, it will update the post with the new form data,
        but the user must be authenticated.

        Returns:
            - 200: if the post is successfully updated
            - 201: if the post is successfully created
            - 400: if the data is invalid
            - 403: if the user is not authenticated
            - 404: if author does not exist 
        '''
        status_code = 201

        author_id = kwargs.pop('author_id', '')
        post_id = kwargs.pop('post_id', '')
        author = get_object_or_404(Author, pk=author_id)
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            status_code = 400
            return HttpResponse('Data is not a valid json', status=status_code)

        if Post.objects.filter(id=post_id, author=author).exists():
            if not request.user.is_authenticated:
                status_code = 403
                message = "You do not have permission to update this author's post."
                return HttpResponse(message, status=status_code)     

            # update post with the given data
            post = Post.objects.get(id=post_id, author=author)
            form = PostForm(data)
            if form.is_valid():
                self.update_post(post, form)
                return HttpResponse("Post is successfully updated.")

            status_code = 400
            return HttpResponse('The form is not valid.', status=status_code)     

        try:
            post = Post.objects.create(pk=post_id, author=author, **data)
        except ValidationError as e:
            status_code = 400
            return HttpResponse('The form data is not valid.', status=status_code)
        
        return HttpResponse('Post successfully created', status=status_code)


    def update_post(self, post, form):
        '''Updates the fields of the post with the given valid form'''
        post.title = form.cleaned_data['title']
        post.description = form.cleaned_data['description']
        # TODO image
        # post.image = form.cleaned_data['image']
        post.content_type = form.cleaned_data['content_type']
        post.content = form.cleaned_data['content']
        post.categories = form.cleaned_data['categories']
        post.visibility = form.cleaned_data['visibility']
        post.save(update_fields=['title', 'description', 'content_type', 'content', 'image', 'categories', 'visibility'])
        post.save()     # update modified date

            
class PostsView(View):

    DEFAULT_PAGE = 1
    DEFAULT_SIZE = 15

    http_method_names = ['get', 'head', 'options', 'post']

    def get(self, request, *args, **kwargs):
        '''
        GET [local, remote]: Returns a JSON response that contains a list of the 
        recent posts from author_id. (paginated)

        Default page = 1, size = 15

        Returns:
            - 200: if successful
            - 404: if author or page does not exist
        '''
        author_id = kwargs.get('author_id', '')
        return JsonResponse(self._get_posts(request, author_id))

    def head(self, request, *args, **kwargs):
        '''
        Handles HEAD request of the same GET request.

        Returns:
            - 200: if successful
            - 404: if author or page does not exist
        '''
        author_id = kwargs.get('author_id', '')
        data_json = json.dumps(self._get_posts(request, author_id))
        response = HttpResponse()
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Length'] = str(len(bytes(data_json, 'utf-8')))
        return response

    def post(self, request, *args, **kwargs):
        '''
        POST [local]: Creates a new post, but generates a new id. 

        Returns:
            - 201: if the post is successfully created
            - 400: if the data is invalid
            - 404: if author does not exist 
        '''
        status_code = 201
        author_id = kwargs.get('author_id', '')
        author = get_object_or_404(Author, id=author_id)

        form = PostForm(request.POST)
        if not form.is_valid():
            status_code = 400
            return HttpResponse('The form data is not valid.', status=status_code)
        
        Post.objects.create(author=author, **form.cleaned_data)
        return HttpResponse('Post successfully created', status=status_code)


    def _get_posts(self, request, author_id) -> dict:
        '''
        Returns a dict that contains a list of posts.
        '''
        page = int(request.GET.get('page', self.DEFAULT_PAGE))
        size = int(request.GET.get('size', self.DEFAULT_SIZE))

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
        data['items'] = [p.get_detail_dict() for p in posts]
        return data




        
