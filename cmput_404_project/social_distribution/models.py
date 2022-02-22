import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser 
from django.utils import timezone

from .managers import AuthorManager

class Author(AbstractUser):

    class Meta:
        verbose_name = 'Author'

    user_id = models.UUIDField(default=uuid.uuid4, editable=False)
    host = models.URLField()
    github = models.URLField()
    profile_image = models.URLField()

    followers = models.ManyToManyField('self')
    following = models.ManyToManyField('self')
    
    objects = AuthorManager()


    def __str__(self):
        return self.username


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    source = models.URLField(default=None)
    origin = models.URLField(default=None)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=100, default='')
    content_type = models.CharField(max_length=30, default='text/plain')
    category = models.ManyToManyField("Category")
    count = models.IntegerField(default=0)
    date_created = models.DateTimeField(default=timezone.now, editable=False)
    visibility = models.CharField(max_length=7, default='PUBLIC')
    unlisted = models.BooleanField(default=False)


    def __str__(self):
        return self.title


class Category(models.Model):
    value = models.CharField(max_length=100)


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
