import uuid
import requests

from urllib.parse import urlparse
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.paginator import Paginator

from .managers import AuthorManager


class Author(AbstractUser):

    type = 'author'
    class Meta:
        verbose_name = 'Author'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # id = models.SlugField(primary_key=True, max_length=64, unique=True)
    host = models.URLField()
    github = models.URLField()
    profile_image = models.URLField()
    followers = models.ManyToManyField('self')
    following = models.ManyToManyField('self')      # TODO is following field necessary?
    objects = AuthorManager()
    REQUIRED_FIELDS = ['first_name', 'last_name', 'host', 'github', 'profile_image']


    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    def get_id_url(self):
        return f'{self.host}service/authors/{self.id}'

    def get_profile_url(self):
        return f'{self.host}authors/{self.id}'

    def get_detail_dict(self) -> dict:
        '''
        Returns a dict containing the author information.
        '''
        d = {}
        d['type'] = self.type
        d['id'] = self.get_id_url()
        d['url'] = self.get_profile_url()
        d['host'] = self.host
        d['displayName'] = self.get_full_name()
        d['github'] = self.github
        d['profileImage'] = self.profile_image
        return d

    def __str__(self):
        return self.username


class Post(models.Model):

    VISIBILITY_CHOICES = [
        ('PUBLIC', 'Public'),
        ('FRIENDS', 'Friends'),
        ('PRIVATE', 'Private'),
    ]

    CONTENT_TYPE_CHOICES = [
        ('text/plain', 'text'),
        ('text/markdown', 'markdown'),
        ('application/base64', 'application'),
        ('image/png;base64', 'png'),
        ('image/jpeg;base64', 'jpeg')
    ]

    DEFAULT_COMMENTS_PAGE = 1
    DEFAULT_COMMENTS_SIZE = 5


    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None, null=True, blank=True)
    source = models.URLField(null=True, default=None)
    origin = models.URLField(null=True, default=None)
    image = models.URLField(null=True, default=None)
    title = models.CharField(max_length=100, default='')
    description = models.TextField(max_length=150, default='')
    content_type = models.CharField(max_length=18, choices=CONTENT_TYPE_CHOICES, default='text/plain')
    content = models.TextField(max_length=1000, default='')
    categories = models.CharField(max_length=100, default='')
    count = models.IntegerField(default=0)
    published = models.DateTimeField(default=timezone.now, editable=False)
    modified = models.DateTimeField(default=timezone.now)
    visibility = models.CharField(max_length=7, choices=VISIBILITY_CHOICES, default='PUBLIC')
    # authors = Author.objects.all()
    # author_choices = []
    # for person in authors:
    #     author_choices.append((person.id, person.get_full_name()))
    # recepient = models.UUIDField(null=True, choices=author_choices, default=None)
    unlisted = models.BooleanField(default=False)
    liked = models.ManyToManyField(Author, blank=True, related_name='likes')
    comments_id = models.UUIDField(default=uuid.uuid4, editable=False)

    type = 'post'

    def save(self, *args, **kwargs):
        '''Upon save, update timestamps of the post'''
        self.modified = timezone.now()
        return super(Post, self).save(*args, **kwargs)

    def get_id_url(self):
        return f'{self.author.get_id_url()}/posts/{self.id}'

    def get_comments_id_url(self):
        return f'{self.get_id_url()}/comments'

    def get_list_of_categories(self):
        return [] if self.categories == '' else self.categories.strip().split(',')

    def get_iso_published(self):
        return self.published.replace(microsecond=0).isoformat()

    def get_iso_modified(self):
        return self.modified.replace(microsecond=0).isoformat()

    def get_detail_dict(self, page=DEFAULT_COMMENTS_PAGE, size=DEFAULT_COMMENTS_SIZE) -> dict:
        '''
        Returns a dict that contains a post detail.
        '''
        d = {}
        d['type'] = self.type
        d['title'] = self.title
        d['id'] = self.get_id_url()
        d['source'] = self.source
        d['origin'] = self.origin
        d['description'] = self.description
        d['contentType'] = self.content_type
        d['content'] = self.content
        d['author'] = self.author.get_detail_dict()
        d['categories'] = self.get_list_of_categories()
        d['count'] = self.count
        d['comments'] = self.get_comments_id_url()
        d['commentsSrc'] = self.get_comments_src_dict(page, size)
        d['published'] = self.get_iso_published()
        d['visibility'] = self.visibility
        d['unlisted'] = self.unlisted

        return d

    def get_comments_src_dict(self, page=DEFAULT_COMMENTS_PAGE, size=DEFAULT_COMMENTS_SIZE) -> dict:
        '''
        Returns a dict that contains the details of the comments for the post
        '''
        q = Comment.objects.filter(post=self).order_by('-date_created')
        comments = Paginator(q, size).page(page)

        data = {}
        data['type'] = 'comments'
        data['page'] = page
        data['size'] = size
        data['post'] = self.get_id_url()
        data['id'] = self.get_comments_id_url()
        data['comments'] = [c.get_detail_dict() for c in comments]
        return data


class FollowRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    from_author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='follow_request_from', null=True)
    from_author_url = models.URLField(max_length=1000, editable=False, null=False)
    to_author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='follow_request_to', null=True)
    to_author_url = models.URLField(max_length=1000, editable=False, null=False)
    date_created = models.DateTimeField(default=timezone.now, editable=False)

    type = 'Follow'

    def get_iso_date_created(self):
        return self.date_created.replace(microsecond=0).isoformat()

    def get_summary(self):
        '''Returns a summary for this FollowRequest object.'''
        if self.from_author:
            from_first_name = self.from_author.first_name
        else:
            from_full_name = request_detail_dict(self.from_author_url).get('displayName', '')
            from_first_name = '' if from_full_name == '' else from_full_name.strip().split(' ')[0]

        if self.to_author:
            to_first_name = self.to_author.first_name
        else:
            to_full_name = request_detail_dict(to_author_url).get('displayName', '')
            to_first_name = '' if to_full_name == '' else to_full_name.strip().split(' ')[0]

        return f'{from_first_name} wants to follow {to_first_name}'

    def get_detail_dict(self) -> dict:
        '''
        Returns a dict that contains a FollowRequest objects's detail.
        '''
        d = {}
        d['type'] = self.type
        d['summary'] = self.get_summary()
        d['actor'] = self.from_author.get_detail_dict() if self.from_author else request_detail_dict(self.from_author_url)
        d['object'] = self.to_author.get_detail_dict() if self.to_author else request_detail_dict(self.to_author_url)

        return d


class Comment(models.Model):
    CONTENT_TYPE_CHOICES = [
        ('text/plain', 'text'),
        ('text/markdown', 'markdown'),
        ('application/base64', 'application'),
        ('image/png;base64', 'png'),
        ('image/jpeg;base64', 'jpeg')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, null=True)
    author_url = models.URLField(max_length=1000, editable=False, null=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    content_type = models.CharField(max_length=18, choices=CONTENT_TYPE_CHOICES, default='text/plain')
    date_created = models.DateTimeField(default=timezone.now, editable=False)
    content = models.TextField(max_length=1000, default='')

    type = 'comment'

    def get_iso_date_created(self):
        return self.date_created.replace(microsecond=0).isoformat()

    def get_id_url(self):
        return f'{self.post.get_comments_id_url()}/{self.id}'

    def get_detail_dict(self) -> dict:
        '''
        Returns a dict that contains a comment's detail.
        '''
        d = {}
        d['type'] = self.type
        d['author'] = self.author.get_detail_dict() if self.author else request_detail_dict(self.author_url)
        d['comment'] = self.content
        d['contentType'] = self.content_type
        d['published'] = self.get_iso_date_created()
        d['id'] = self.get_id_url()
        return d


class Like(models.Model):
    OBJECT_TYPE_CHOICES = [
        ('POST', 'Post'),
        ('COMMENT', 'Comment'),
    ]
    context = "https://www.w3.org/ns/activitystreams"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Author object does not have to be given, but author url must be provided
    author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None, null=True)
    author_url = models.URLField(max_length=1000, editable=False, null=False)
    object_type = models.CharField(max_length=7, choices=OBJECT_TYPE_CHOICES, default='POST')
    # object_id = models.UUIDField(default=None, editable=False, null=True)
    object_url = models.URLField(max_length=1000, default=None, editable=False)
    date_created = models.DateTimeField(default=timezone.now, editable=False)

    type = 'Like'


    def get_iso_date_created(self):
        return self.date_created.replace(microsecond=0).isoformat()

    def get_detail_dict(self) -> dict:
        '''Returns a dict that contains a like's detail.'''
        d = {}
        d['@context'] = self.context
        d['summary'] = self.get_summary()
        d['type'] = self.type
        if self.author is None:
            d['author'] = request_detail_dict(self.author_url)
        else:
            d['author'] = self.author.get_detail_dict()
        d['object'] = self.object_url

        return d

    def get_summary(self):
        '''Returns a summary for this like object.'''
        if self.author:
            return f'{self.author.get_full_name()} Likes your {self.object_type.strip().lower()}'
        full_name = request_detail_dict(self.author_url).get('displayName', '')
        return f'{full_name} Likes your {self.object_type.strip().lower()}'


    def is_object_public(self):
        '''
        Returns True if the liked object is publicly available.
        Otherwise, returns False
        '''
        object_id = self.object_url.split('/')[-1]

        # check local server
        if self.object_type == 'POST' and Post.objects.filter(id=object_id).exists():
            return Post.objects.get(id=object_id).visibility == 'PUBLIC'
        elif self.object_type == 'COMMENT' and Comment.objects.filter(id=object_id).exists():
            return Comment.objects.get(id=object_id).post.visibility == 'PUBLIC'

        # check remote servers
        data = request_detail_dict(self.object_url)
        obj_type = data['type']
        if obj_type == 'post':
            return data['visibility'] == 'PUBLIC'
        else:
            # for a comment, must check whether its post is public
            return request_detail_dict(data['id'])['visibility'] == 'PUBLIC'



class Inbox(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    type = 'inbox'


    def get_detail_dict(self):
        '''Returns a dict that contains this inbox's detail.'''
        d = {}
        d['type'] = 'inbox'
        d['author'] = self.author.get_id_url()
        items = InboxItem.objects.filter(inbox=self).all()
        d['items'] = [item.get_detail_dict() for item in items]

        return d


class InboxItem(models.Model):
    OBJECT_TYPE_CHOICES = [
        ('POST', 'Post'),
        ('COMMENT', 'Comment'),
        ('FOLLOW', 'Follow'),
        ('LIKE', 'like')
    ]

    inbox = models.ForeignKey(Inbox, on_delete=models.CASCADE)
    object_type = models.CharField(max_length=7, choices=OBJECT_TYPE_CHOICES, default='POST')
    object_id = models.UUIDField(default=None, editable=False, null=True)
    # object url is None if the object is FollowRequest or Like
    object_url = models.URLField(max_length=1000, default=None, editable=False, null=True)
    date_created = models.DateTimeField(default=timezone.now, editable=False)


    def get_detail_dict(self) -> dict:
        '''Returns a dict that contains this object's detail.'''
        if self.object_id is not None:
            if self.object_type == 'POST':
                # TODO if Post, only send comments field, not with commentSrc
                object = Post.objects.get(id=self.object_id)
            elif self.object_type == 'COMMENT':
                object = Comment.objects.get(id=self.object_id)
            elif self.object_type == 'FOLLOW':
                object = FollowRequest.objects.get(id=self.object_id)
            else:
                object = Like.objects.get(id=self.object_id)
            return object.get_detail_dict()

        return request_detail_dict(self.object_url)


def request_detail_dict(object_url) -> dict:
    '''
    Makes a GET request to service api of object_url.
    Then, returns a parsed json data.
    '''
    o = urlparse(object_url)
    # service_url = f'{o.scheme}://{o.netloc}/service{o.path}'
    res = requests.get(object_url)
    return dict(res.json()) if res.status_code == 200 else {}



STATUS_CHOICES = (
    ('send', 'send'),
    ('accepted', 'accepted')
)
class FriendManager(models.Manager):
    def invatations_received(self, receiver):
        qs = Friends.objects.filter(receiver=receiver, status='send')
        return qs
    def invatations_accepted(self, receiver):
        qs = Friends.objects.filter(receiver=receiver, status='accepted')
        return qs

class Friends(models.Model):
    sender = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='receiver')
    status = models.CharField(max_length=8, choices=STATUS_CHOICES)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = FriendManager()

#    def __str__(self):
#        return f"{self.sender}-{self.receiver}-{self.status}"
