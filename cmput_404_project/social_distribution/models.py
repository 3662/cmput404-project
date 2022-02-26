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


    def __str__(self):
        return self.title


# class Category(models.Model):
    # value = models.CharField(max_length=100)


class FollowRequest(models.Model):
    summmary = models.CharField(max_length=100)
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
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    object = models.URLField(default=None)
    summmary = models.CharField(max_length=100)
    date_created = models.DateTimeField(default=timezone.now, editable=False)
