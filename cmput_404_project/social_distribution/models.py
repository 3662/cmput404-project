import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser 
from django.utils import timezone
from django.core.paginator import Paginator
        
from .managers import AuthorManager


class Author(AbstractUser):

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

    type = 'author'

    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    def get_id_url(self):
        return f'{self.host}authors/{self.id}'

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

    COMMENTS_PAGE = 1
    COMMENTS_SIZE = 5
    

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None, null=True, blank=True)
    source = models.URLField(null=True, default=None)
    origin = models.URLField(null=True, default=None)
    image = models.URLField(null=True, default=None)
    title = models.CharField(max_length=100, default='')
    description = models.TextField(max_length=150, default='')
    content_type = models.CharField(max_length=30, default='text/plain')        
    content = models.TextField(max_length=1000, default='')
    categories = models.CharField(max_length=100, default='')
    count = models.IntegerField(default=0)
    published = models.DateTimeField(default=timezone.now, editable=False)
    modified = models.DateTimeField(default=timezone.now)
    visibility = models.CharField(max_length=7, default='PUBLIC')
    authors = Author.objects.all()
    author_choices = []
    for person in authors:
        author_choices.append((person.id, person.get_full_name()))
    recepient = models.UUIDField(null=True, choices=author_choices, default=None)
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
        return f'{self.author.get_id_url()}/posts/{self.comments_id}/comments'

    def get_list_of_categories(self):
        return [] if self.categories == '' else self.categories.strip().split(',')

    def get_iso_published(self):
        return self.published.replace(microsecond=0).isoformat()

    def get_iso_modified(self):
        return self.modified.replace(microsecond=0).isoformat()

    def get_detail_dict(self) -> dict:
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
        d['published'] = self.get_iso_published()
        d['visibility'] = self.visibility
        d['unlisted'] = self.unlisted

        # TODO comments

        return d

    def get_comments_src_dict(self, page=COMMENTS_PAGE, size=COMMENTS_SIZE) -> dict:
        '''
        Returns a dict that contains the details of the comments for the post
        '''
        q = Comment.objects.all()  
        q = q.filter(post=self)
        q = q.order_by('-date_created')
        comments = Paginator(q, size).page(page)

        data = {}
        data['type'] = 'comments'
        data['page'] = page
        data['size'] = size
        data['post'] = self.get_id_url()
        data['id'] = self.get_comments_id_url()
        data['items'] = [c.get_detail_dict() for c in comments]
        return data


class FollowRequest(models.Model):
    summary = models.CharField(max_length=100, default='')
    from_author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='follow_request_from')
    to_author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='follow_request_to')
    date_created = models.DateTimeField(default=timezone.now, editable=False)

    def get_iso_date_created(self):
        return self.date_created.replace(microsecond=0).isoformat()


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    content_type = models.CharField(max_length=30, default='text/plain')
    date_created = models.DateTimeField(default=timezone.now, editable=False)
    content = models.TextField(max_length=1000, default='')

    type = 'comment'

    def get_iso_date_created(self):
        return self.date_created.replace(microsecond=0).isoformat()

    def get_id_url(self):
        return f'{self.post.get_comments_id_url()}/comments/{self.id}'

    def get_detail_dict(self) -> dict:
        '''
        Returns a dict that contains a comment's detail.
        '''
        d = {}
        d['type'] = self.type
        d['author'] = self.author.get_detail_dict()
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

    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    object_type = models.CharField(max_length=7, choices=OBJECT_TYPE_CHOICES, default='POST')
    object_id = models.UUIDField(default=uuid.uuid4, editable=False)
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
        d['author'] = self.author.get_detail_dict()

        if self.object_type == 'POST':
            object = Post.objects.get(id=self.object_id)
        else:
            object = Comment.objects.get(id=self.object_id)
        d['object'] = object.get_id_url()

        return d
        
    def get_summary(self):
        '''Returns a summary for this like object.'''
        return f'{self.author.get_full_name()} Likes your {self.object_type.strip().lower()}'


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
    object_id = models.UUIDField(default=uuid.uuid4, editable=False)


    def get_detail_dict(self) -> dict:
        '''Returns a dict that contains this object's detail.'''
        if self.object_type == 'POST':
            object = Post.objects.get(id=self.object_id)
        elif self.object_type == 'COMMENT':
            object = Comment.objects.get(id=self.object_id)
        elif self.object_type == 'FOLLOW':
            object = FollowRequest.objects.get(id=self.object_id)
        else:
            object = Like.objects.get(id=self.object_id)
        return object.get_detail_dict()



    


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
