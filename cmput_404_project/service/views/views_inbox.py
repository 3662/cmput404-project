import json

from dateutil import parser
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
            - 404: if author or page does not exist
        '''
        author_id = kwargs.get('author_id', '')
        return JsonResponse(self._get_post_inbox_items(request, author_id))

    def head(self, request, *args, **kwargs):
        '''
        Handles HEAD request of the same GET request.

        Returns:
            - 200: if successful
            - 404: if author or page does not exist
        '''
        author_id = kwargs.get('author_id', '')
        data_json = json.dumps(self._get_post_inbox_items(request, author_id))
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
            - 200: if successful
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
                object = self._create_post_if_not_exist(data)

            elif t == 'comment':
                object_type = 1
                object = self._create_comment_if_not_exist(data)

            elif t == 'follow':
                object_type = 2
                object = self._create_follow_request(data, author)

            else:
                object_type = 3
                object = self._create_like(data)

            if not InboxItem.objects.filter(object_id=object.id).exists():
                # Only create if the object is not already in the inbox
                # If the object exists in the inbox, it has been already updated at this point.
                InboxItem.objects.create(inbox=inbox, 
                                        object_type=InboxItem.OBJECT_TYPE_CHOICES[object_type][0], 
                                        object_id=object.id)

        except (KeyError, ValueError) as e:
            status_code = 400
            return HttpResponse(e if str(e) != '' else 'The object is invalid', status=status_code)     

        else:
            return HttpResponse("An object is successfully sent to the inbox")


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


    def _get_post_inbox_items(self, request, author_id) -> dict:
        '''
        Returns a dict containing a list of posts in the author_id's inbox.
        '''

        page = int(request.GET.get('page', self.DEFAULT_PAGE))
        size = int(request.GET.get('size', self.DEFAULT_SIZE))

        author = get_object_or_404(Author, id=author_id)

        try:
            inbox = Inbox.objects.get(author=author)
        except ObjectDoesNotExist:
            # create an inbox for this author if it doesn't exist
            inbox = Inbox.objects.create(author=author)

        try:
            q = InboxItem.objects.all().filter(inbox=inbox, object_type=InboxItem.OBJECT_TYPE_CHOICES[0][0])
            q = q.order_by('-published')
            post_items = Paginator(q, size).page(page)
        except EmptyPage:
            raise Http404('Page does not exist')

        data = {}
        data['type'] = 'posts'
        data['items'] = [p.get_detail_dict() for p in post_items]
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
        like_author = self._create_author_if_not_exist(data_dict['author'])
        object_id = data_dict['object'].split('/')[-1]

        if Post.objects.filter(id=object_id).exists():
            object_type = Like.OBJECT_TYPE_CHOICES[0][0]
        elif Comment.objects.filter(id=object_id).exists():
            object_type = Like.OBJECT_TYPE_CHOICES[1][0]
        else:
            raise ValueError('object id: %s is not associated with this author' % object_id)
        
        return Like.objects.create(author=like_author, object_type=object_type, object_id=object_id)


    def _create_comment_if_not_exist(self, data_dict) -> Comment:
        '''
        Creates a Comment if it does not exist.
        If it does exist, update its content and content type.
        The comment author will also be created if it does not exist.
        '''

        comment_author = self._create_author_if_not_exist(data_dict['author'])
        comment_id = data_dict['id'].split('/')[-1]
        content = data_dict['comment']
        published = parser.parse(data_dict['published'])
        content_type = data_dict['contentType']
        if content_type not in map(lambda p:p[0], Comment.CONTENT_TYPE_CHOICES):
            raise ValueError('Invalid content type: %s' % content_type)

        try:
            comment = Comment.objects.get(id=comment_id, author=comment_author)
            # update fields of the comment if exists
            comment.content = content
            comment.content_type = content_type
            comment.save(update_fields=['content', 'content_type'])

        except ObjectDoesNotExist:
            comment = Comment.objects.create(id=comment_id,
                                             author=comment_author,
                                             content=content,
                                             date_created=published,
                                             content_type=content_type)
                                        
        return comment

    
    def _create_follow_request(self, data_dict, author:Author) -> FollowRequest:
        '''
        Creates a FollowRequest between the two authors in data_dict.

        Raises a ValueError if
            - FollowRequest between the two authors already exists, or
            - author in the request and author in the data_dict are not equal.
        '''

        from_author = self._create_author_if_not_exist(data_dict['actor'])
        to_author_id = data_dict['object']['id'].split('/')[-1]
        to_author = get_object_or_404(Author, id=to_author_id)
        if author != to_author:
            # assert target author is the author in the request
            raise ValueError('Target author and to_author in follow object are not equal')

        if FollowRequest.objects.filter(from_author=from_author, to_author=author).exists():
            # raise an exception if follow request between the two author already exists
            raise ValueError('Follow request is already sent') 

        return FollowRequest.objects.create(from_author=from_author, to_author=author)


    
    def _create_post_if_not_exist(self, post_dict) -> Post:
        '''
        If a Post with an id in post_dict does not exist, create one. 
        If the Post already exists, then update the fields with the given information.
        If a post author with an author id in post_dict does not exist, create on.
        If the Author already exists, then update the fields with the given information.
        '''
        
        post_author = self._create_author_if_not_exist(post_dict['author'])
        title = post_dict['title']
        post_id = post_dict['id'].split('/')[-1]
        source = post_dict['source']
        origin = post_dict['origin']
        description = post_dict['description']
        content_type = post_dict['contentType']
        if content_type not in map(lambda p:p[0], Post.CONTENT_TYPE_CHOICES):
            raise ValueError('Invalid content type: %s' % content_type)
        content = post_dict['content']
        categories = ','.join(post_dict['categories'])
        comments_id = post_dict['comments'].split('/')[-1]
        published = parser.parse(post_dict['published'])
        visibility = post_dict['visibility']
        if visibility not in map(lambda p:p[0], Post.VISIBILITY_CHOICES):
            raise ValueError('Invalid visibility: %s' % visibility)

        unlisted = post_dict['unlisted']

        try:
            post = Post.objects.get(id=post_id)
            # update fields of the post if exists
            post.title = title
            post.source = source
            post.origin = origin 
            post.description = description
            post.content_type = content_type 
            post.content = content
            post.categories = categories
            post.published = published
            post.visibility = visibility 
            post.unlisted = unlisted
            post.save(update_fields=['title', 'source', 'origin', 'description', 'content_type', 'content', 'categories', 'published', 'visibility', 'unlisted'])

        except ObjectDoesNotExist:
            post = Post.objects.create(author=post_author,
                                       id=post_id,
                                       title=title,
                                       source=source,
                                       origin=origin,
                                       description=description,
                                       content_type=content_type,
                                       content=content,
                                       categories=categories,
                                       comments_id=comments_id,
                                       published=published,
                                       visibility=visibility,
                                       unlisted=unlisted)
        
        return post


    def _create_author_if_not_exist(self, author_dict) -> Author:
        '''
        If an Author with an author id in author_dict does not exist, 
        create one but without user information.
        If the Author already exists, then update the fields with the given information.
        '''
        author_id = author_dict['id'].split('/')[-1]
        author_display_name = author_dict['displayName']
        author_first_name, author_last_name = author_display_name.strip().split(' ')
        author_host = author_dict['host']
        author_github = author_dict['github']
        author_profile_image = author_dict['profileImage']

        try: 
            author = Author.objects.get(id=author_id)
            # update the fields of the author if exists
            author.first_name = author.first_name
            author.last_name = author.last_name
            author.host = author_host
            author.github = author_github
            author.profile_image = author_profile_image

            author.save(update_fields=['first_name', 'last_name', 'host', 'github', 'profile_image'])

        except ObjectDoesNotExist:
            author = Author.objects.create_without_user(id=author_id, 
                                                        first_name=author_first_name,
                                                        last_name=author_last_name,
                                                        host=author_host,
                                                        github=author_github,
                                                        profile_image=author_profile_image)

        return author




        





