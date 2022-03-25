import json

from django.shortcuts import get_object_or_404
from django.views import View
from django.http import JsonResponse, HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage

from social_distribution.models import Author, Post, Like, Comment, Inbox, InboxItem, FollowRequest


class InboxView(View):

    http_method_names = ['get', 'head', 'options', 'post', 'delete']

    DEFAULT_PAGE = 1
    DEFAULT_SIZE = 10

    def get(self, request, *args, **kwargs):
        '''
        GET [local]: if authenticated, get a list of posts sent to AUTHOR_ID (paginated)

        Default page = 1, size = 10

        Returns:
            - 200: if successful
            - 403: if the author is not authenticated
            - 404: if author or page does not exist
        '''
        author_id = kwargs.get('author_id', '')
        return JsonResponse(self._get_inbox_items(request, author_id))

    def head(self, request, *args, **kwargs):
        '''
        Handles HEAD request of the same GET request.

        Returns:
            - 200: if successful
            - 403: if the author is not authenticated
            - 404: if author or page does not exist
        '''
        author_id = kwargs.get('author_id', '')
        data_json = json.dumps(self._get_inbox_items(request, author_id))
        response = HttpResponse()
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Length'] = str(len(bytes(data_json, 'utf-8')))
        return response

    def post(self, request, *args, **kwargs):
        '''
        POST [local, remote]: send a object to the author
            - If the type is “post” then add that post to AUTHOR_ID's inbox
            - If the type is “follow” then add that follow is added to AUTHOR_ID's inbox to approve later
            - If the type is “like” then add that like to AUTHOR_ID's inbox
            - If the type is “comment” then add that comment to AUTHOR_ID's inbox
        
        Returns:
            - 201: if successful
            - 400: if the object is invalid.
            - 404: if the author does not exist.
        '''
        author_id = kwargs.get('author_id', '')
        author = get_object_or_404(Author, id=author_id)

        try:
            inbox = Inbox.objects.get(author=author)
        except ObjectDoesNotExist:
            # create an inbox for this author if it doesn't exist
            inbox = Inbox.objects.create(author=author)

        valid_object_types = ['post', 'follow', 'like', 'comment']
        data = json.loads(request.body)
        try:
            t = data['type'].strip().lower()
            if t not in valid_object_types:
                raise ValueError('The type of the object is invalid')
            
            if t == 'post':
                object_type = 0
                post_id = data['id'].split('/')[-1]
                if Post.objects.filter(id=post_id).exists():
                    post = Post.objects.get(id=post_id)
                    object_id = post.id
                    object_url = post.get_id_url()
                else:
                    object_id = None
                    object_url = data['id'] 

            elif t == 'comment':
                object_type = 1
                comment_id = data['id'].split('/')[-1]
                if Comment.objects.filter(id=comment_id).exists():
                    comment = Comment.objects.get(id=comment_id)
                    object_id = comment.id
                    object_url = comment.get_id_url()
                else:
                    object_id = None
                    object_url = data['id'] 

            elif t == 'follow':
                object_type = 2
                object = self._create_follow_request(data, author)
                object_id = object.id
                object_url = None

            else:
                object_type = 3
                object = self._create_like(data)
                object_id = object.id
                object_url = None

            if not InboxItem.objects.filter(object_id=object_id).exists():
                # Only create if the object is not already in the inbox
                # If the object exists in the inbox, it has been already updated at this point.
                InboxItem.objects.create(inbox=inbox, 
                                        object_type=InboxItem.OBJECT_TYPE_CHOICES[object_type][0], 
                                        object_id=object_id,
                                        object_url=object_url)

        except (KeyError, ValueError) as e:
            status_code = 400
            return HttpResponse(e if str(e) != '' else 'The object is invalid', status=status_code)     

        else:
            return HttpResponse("An object is successfully sent to the inbox", status=201)


    def delete(self, request, *args, **kwargs):
        '''
        DELETE [local]: clears the inbox

        Returns:
            - 204: if successfully cleared
            - 404: if the author does not exist
        '''

        author_id = kwargs.get('author_id', '')
        author = get_object_or_404(Author, id=author_id)

        try:
            inbox = Inbox.objects.get(author=author)
        except ObjectDoesNotExist:
            # create an inbox for this author if it doesn't exist
            inbox = Inbox.objects.create(author=author)
        
        InboxItem.objects.filter(inbox=inbox).delete()
    
        return HttpResponse("The inbox is cleared", status=204)


    def _get_inbox_items(self, request, author_id) -> dict:
        '''
        Returns a dict containing a list of posts in the author_id's inbox.
        '''
        if not request.user.is_authenticated:
            status_code = 403
            message = "You do not have permission to access this author's inbox."
            return HttpResponse(message, status=status_code)     

        page = int(request.GET.get('page', self.DEFAULT_PAGE))
        size = int(request.GET.get('size', self.DEFAULT_SIZE))

        author = get_object_or_404(Author, id=author_id)

        try:
            inbox = Inbox.objects.get(author=author)
        except ObjectDoesNotExist:
            # create an inbox for this author if it doesn't exist
            inbox = Inbox.objects.create(author=author)

        try:
            q = InboxItem.objects.all().filter(inbox=inbox)
            q = q.order_by('-date_created')
            inbox_items = Paginator(q, size).page(page)
        except EmptyPage:
            raise Http404('Page does not exist')

        data = {}
        data['type'] = 'inbox'
        data['items'] = [item.get_detail_dict() for item in inbox_items]
        return data


    def _create_like(self, data_dict) -> Like:
        '''
        Create a Like from data_dict.

        Raises ValueError if
            - @context is invalid, or
            - object id in data_dict is not associated with the author
        '''

        context = data_dict['@context']
        if context != Like.context:
            raise ValueError('Invalid context: %s' % context)
        like_author_id = data_dict['author']['id'].split('/')[-1]
        like_author = None  # can be local or remote author
        if Author.objects.filter(id=like_author_id).exists():
            # is a local author
            like_author = Author.objects.get(id=like_author_id)
        like_author_url = data_dict['author']['id']
        object_url = data_dict['object']

        # object id must exist in our database
        object_id = object_url.split('/')[-1]

        if Post.objects.filter(id=object_id).exists():
            object_type = Like.OBJECT_TYPE_CHOICES[0][0]
        elif Comment.objects.filter(id=object_id).exists():
            object_type = Like.OBJECT_TYPE_CHOICES[1][0]
        else:
            raise ValueError('object id: %s is not associated with this author' % object_id)
        
        return Like.objects.create(author=like_author, 
                                   author_url=like_author_url, 
                                   object_type=object_type, 
                                   object_url=object_url)


    def _create_follow_request(self, data_dict, author:Author) -> FollowRequest:
        '''
        Creates a FollowRequest between the two authors in data_dict.

        Raises a ValueError if
            - FollowRequest between the two authors already exists, or
            - author in the request and author in the data_dict are not equal.
        '''
        # from_author can be from remote server
        from_author_id = data_dict['actor']['id'].split('/')[-1]
        if Author.objects.filter(id=from_author_id).exists():
            from_author = Author.objects.get(id=from_author_id)
        else:
            from_author = None
        from_author_url = data_dict['actor']['url']

        to_author_id = data_dict['object']['id'].split('/')[-1]
        to_author = get_object_or_404(Author, id=to_author_id)
        if author != to_author:
            # assert target author is the author in the request
            raise ValueError('Target author and to_author in follow object must be equal')

        if FollowRequest.objects.filter(from_author_url=from_author_url, to_author=author).exists():
            # raise an exception if follow request between the two author already exists
            raise ValueError('Follow request is already sent') 

        return FollowRequest.objects.create(from_author=from_author,
                                            from_author_url=from_author_url,
                                            to_author=author,
                                            to_author_url=author.get_id_url())