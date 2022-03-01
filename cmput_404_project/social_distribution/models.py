import uuid
import hashlib

from django.db import models
from django.contrib.auth.models import AbstractUser 
from django.utils import timezone
from django.utils.text import slugify
        
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


    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()


    def __str__(self):
        return self.username


class Post(models.Model):
    # id = models.SlugField(primary_key=True, max_length=64, unique=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None, null=True, blank=True)
    source = models.URLField(null=True, default=None)
    origin = models.URLField(null=True, default=None)
    image = models.URLField(null=True, default=None)
    title = models.CharField(max_length=100, default='')
    description = models.TextField(max_length=1000, default='')
    content_type = models.CharField(max_length=30, default='text/plain')
    # category = models.ManyToManyField("Category")
    categories = models.CharField(max_length=100, default='')
    count = models.IntegerField(default=0)
    published = models.DateTimeField(default=timezone.now, editable=False)
    visibility = models.CharField(max_length=7, default='PUBLIC')
    unlisted = models.BooleanField(default=False)
    liked = models.ManyToManyField(Author, blank=True, related_name='likes')

#    def __str__(self):
        #return self.title

# class Category(models.Model):
    # value = models.CharField(max_length=100)


class FollowRequest(models.Model):
    summary = models.CharField(max_length=100)
    from_author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='follow_request_from')
    to_author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='follow_request_to')
    date_created = models.DateTimeField(default=timezone.now, editable=False)


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    content_type = models.CharField(max_length=30, default='text/plain')
    date_created = models.DateTimeField(default=timezone.now, editable=False)


class Like(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    summary = models.CharField(max_length=100, null=True, blank=True)
    date_created = models.DateTimeField(default=timezone.now, editable=False)

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
