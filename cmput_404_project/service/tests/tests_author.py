import json

from django.test import TestCase, Client

from social_distribution.models import Author
from .helper import create_dummy_authors

class AuthorsDetailViewTestCase(TestCase):

    NUM_AUTHORS = 5

    def setUp(self):
        create_dummy_authors(self.NUM_AUTHORS)

    def test_get(self):
        c = Client()

        num_authors = len(Author.objects.all())
        response = c.get(f'/service/authors/?page=1&size={num_authors}')
        data = response.json()
        self.assertEqual(data['type'], 'authors')
        self.assertEqual(len(data['items']), num_authors)

        first = data['items'][0]
        self.assertTrue('type' in first.keys())
        self.assertTrue('id' in first.keys())
        self.assertTrue('url' in first.keys())
        self.assertTrue('host' in first.keys())
        self.assertTrue('displayName' in first.keys())
        self.assertTrue('github' in first.keys())
        self.assertTrue('profileImage' in first.keys())

        response = c.get(f'/service/authors/?page=2&size={num_authors}')
        self.assertEqual(response.status_code, 404)

    def test_head(self):
        c = Client()

        num_authors = len(Author.objects.all())
        response = c.head(f'/service/authors/?page=1&size={num_authors}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'')




    


    


