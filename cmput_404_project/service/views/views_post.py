import json

from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator, EmptyPage
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse, Http404
from django.views import View
from posts.forms import PostForm
from django.core.exceptions import ValidationError

from social_distribution.models import Author, Post
from .views_author import get_author_detail


class PostView(View):
    http_method_names = ['get', 'head', 'options', 'post', 'delete', 'put']

    def get(self, request, *args, **kwargs):
        '''
        GET [local, remote]: Returns a JSON response that contains the public post whose id is post_id.
        '''
        author_id = kwargs.get('author_id', '')
        post_id = kwargs.get('post_id', '')
        author = get_object_or_404(Author, pk=author_id)
        post = get_object_or_404(Post, pk=post_id, author_id=author_id, visibility="PUBLIC")

        return JsonResponse(get_post_detail(post, author))


    def head(self, request, *args, **kwargs):
        '''
        Handles HEAD request of the same GET request.
        '''
        author_id = kwargs.get('author_id', '')
        post_id = kwargs.get('post_id', '')
        author = get_object_or_404(Author, pk=author_id)
        post = get_object_or_404(Post, pk=post_id, author_id=author_id, visibility="PUBLIC")
        data_json = json.dumps(get_post_detail(post, author))

        response = HttpResponse()
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Length'] = str(len(bytes(data_json, 'utf-8')))

        return response
        

    def post(self, request, *args, **kwargs):
        '''
        POST [local]: Updates the post whose id is post_id.

        Note: author must be authenticated.
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
        '''
        author_id = kwargs.get('author_id', '')
        post_id = kwargs.get('post_id', '')
        post = get_object_or_404(Post, pk=post_id, author_id=author_id, visibility="PUBLIC")
        post.delete()
        return HttpResponse('Post successfully deleted')


    def put(self, request, *args, **kwargs):
        '''
        PUT [local]: creates a post where its id is post_id, if the given form data is valid.

        Note: if the post already exists, it will update the post with the new form data,
        but the user must be authenticated.
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
        POST [local]: Creates a new post, but generates a new id. 

        If the post creation is successful, returns a JsonResponse with the content of the post.
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
        data['items'] = [get_post_detail(p, author) for p in posts]
        return data



def get_post_detail(post, author) -> dict:
    '''
    Returns a dict that contains a post detail.
    '''
    d = {}
    d['type'] = 'post'
    d['title'] = post.title
    d['id'] = post.get_id_url()
    d['source'] = post.source
    d['origin'] = post.origin
    d['description'] = post.description
    d['contentType'] = post.content_type
    d['content'] = post.content
    d['author'] = get_author_detail(author)
    d['categories'] = post.get_list_of_categories()
    d['count'] = post.count
    d['published'] = post.get_iso_published()
    d['visibility'] = post.visibility
    d['unlisted'] = post.unlisted

    # TODO comments

    return d

        
