import json

from django.shortcuts import get_object_or_404
from django.views import View
from django.http import JsonResponse, HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist

from social_distribution.models import Author, Post, Like, Comment, Inbox, InboxItem


class InboxView(View):

    http_method_names = ['get', 'head', 'options', 'post', 'delete']

    def get(self, request, *args, **kwargs):
        author_id = kwargs.get('author_id', '')
        author = get_object_or_404(Author, id=author_id)

        try:
            inbox = Inbox.objects.get(author=author)
        except ObjectDoesNotExist:
            # create an inbox for this author if it doesn't exist
            inbox = Inbox.objects.create(author=author)

        raise NotImplementedError()

    def head(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        '''
        POST [local, remote]: send a object to the author
            - If the type is “post” then add that post to AUTHOR_ID's inbox
            - If the type is “follow” then add that follow is added to AUTHOR_ID's inbox to approve later
            - If the type is “like” then add that like to AUTHOR_ID's inbox
            - If the type is “comment” then add that comment to AUTHOR_ID's inbox
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
                object_id = data['id'].split('/')
                InboxItem.objects.create(inbox=inbox, object_type=InboxItem.OBJECT_TYPE_CHOICES[0][0])
            elif t == 'follow':
                self._create_follow_request(data)



        except (KeyError, ValueError) as e:
            status_code = 400
            return HttpResponse(e if str(e) != '' else 'The form is invalid', status=status_code)     

    def delete(self, request, *args, **kwargs):
        pass

    def _create_follow_request(self, data_dict):
        '''
        Creates a FollowRequest object using data_dict.

        :raises KeyError: if appropriate keys do not exist in data_dict.
        '''
        # TODO use AuthorProfile instead of Author
        from_author_dict = data_dict['actor']
        to_author_dict = data_dict['object']

        from_author_id = from_author_dict['id'].split('/')[-1]
        to_author_id = to_author_dict['id'].split('/')[-1]

