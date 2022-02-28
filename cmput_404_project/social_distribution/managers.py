import hashlib

from django.contrib.auth.base_user import BaseUserManager


class AuthorManager(BaseUserManager):

    def create_user(self, username, password, **extra_fields):
        '''
        Create and save a new author with the given username and password.
        '''
        if not username:
            raise ValueError('Username cannot be empty')

        author = self.model(username=username, **extra_fields)
        author.set_password(password)
        author.save()
        return author

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')

        return self.create_user(username, password, **extra_fields)
