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


