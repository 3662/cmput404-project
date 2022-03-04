from django.test import TestCase, Client
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

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


class AuthorDetailViewTestCase(TestCase):

    def setUp(self):
        create_dummy_authors(1)

    def test_get(self):
        c = Client()

        author = Author.objects.get(username='test0')
        response = c.get(f'/service/authors/{author.id}/')

        data = response.json()
        self.assertEqual(response.status_code, 200)

        self.assertTrue('type' in data.keys())
        self.assertTrue('id' in data.keys())
        self.assertTrue('url' in data.keys())
        self.assertTrue('host' in data.keys())
        self.assertTrue('displayName' in data.keys())
        self.assertTrue('github' in data.keys())
        self.assertTrue('profileImage' in data.keys())

        self.assertEqual(data['type'], 'author')
        self.assertEqual(data['displayName'], author.get_full_name())
        self.assertEqual(data['profileImage'], author.profile_image)
        try:
            validate = URLValidator()
            validate(data['id'])
            validate(data['url'])
            validate(data['github'])
        except ValidationError as e:
            self.assertTrue(False, "This field must be a valid url")
        else:
            self.assertEqual(data['id'], f'{author.host}authors/{author.id}')
            self.assertEqual(data['url'], f'{author.host}authors/{author.id}')
            self.assertEqual(data['github'], author.github)

    def test_head(self):
        c = Client()

        author = Author.objects.get(username='test0')
        response = c.head(f'/service/authors/{author.id}/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'')

    
    def test_post(self):
        c = Client()

        author = Author.objects.get(username='test0')

        # test
        response = c.post(f'/service/authors/{author.id}/')
        self.assertEqual(response.status_code, 403)

        c.login(username=author.username, password='temporary')

        # post with invalid form
        data = {
            'github': 'invalid url',
        }
        response = c.post(f'/service/authors/{author.id}/', data, follow=True)
        self.assertEqual(response.status_code, 400)

        # post with valid form
        data = {
            'first_name': 'Updated_first_name',
            'last_name': 'Updated_last_name',
            'profile_image': 'https://avatars.githubusercontent.com/u/71972141?s=200&v=4',
            'github': 'https://github.com/updated',
        }
        response = c.post(f'/service/authors/{author.id}/', data, follow=True)
        self.assertEqual(response.status_code, 200)

        # check if the author is updated
        author = Author.objects.get(username='test0')
        self.assertEqual(author.first_name, data['first_name'])
        self.assertEqual(author.last_name, data['last_name'])
        self.assertEqual(author.profile_image, data['profile_image'])
        self.assertEqual(author.github, data['github'])
        

    


    


