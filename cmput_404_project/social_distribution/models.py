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
    content_type = models.CharField(max_length=30, default=None)
    category = models.ManyToManyField("Category")
    count = models.IntegerField(default=0)
    published = models.DateTimeField(default=timezone.now, editable=False)
    visibility = models.CharField(max_length=7, default='PUBLIC')
    unlisted = models.BooleanField(default=False)


    def __str__(self):
        return self.title


class Category(models.Model):
    value = models.CharField(max_length=100)
