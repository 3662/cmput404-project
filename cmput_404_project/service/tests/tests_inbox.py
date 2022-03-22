import uuid
import json

from django.test import TestCase, Client
from django.core.exceptions import ObjectDoesNotExist

from social_distribution.models import Author, Post
from .helper import create_dummy_authors, create_dummy_post, create_dummy_posts


class InboxViewTestCase(TestCase):
    pass

