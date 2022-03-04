from django.test import TestCase, Client
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from social_distribution.models import Author
from .helper import create_dummy_author_with_followers, create_dummy_authors


class FollowersViewTestCase(TestCase):

    NUM_FOLLOWERS = 5

    def setUp(self):
        create_dummy_author_with_followers(self.NUM_FOLLOWERS)


    def test_get(self):
        c = Client()
        author = Author.objects.get(username='test')

        # test with invalid author id
        response = c.get(f'/service/authors/invalid_author_id/followers/')
        self.assertEqual(response.status_code, 404)

        # test with valid author id
        response = c.get(f'/service/authors/{author.id}/followers/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['type'], 'followers')
        self.assertEqual(len(data['items']), self.NUM_FOLLOWERS)

        for follower_data in data['items']:
            follower_id = follower_data['id'].split('/')[-1]
            follower = Author.objects.get(id=follower_id)
            self.assert_author_data(follower, follower_data)


    def test_head(self):
        c = Client()
        author = Author.objects.get(username='test')

        # test with valid author id
        response = c.head(f'/service/authors/{author.id}/followers/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'')


    def assert_author_data(self, author, data):
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
        
        
class FollowersViewTestCase(TestCase):

    NUM_FOLLOWERS = 1

    def test_get(self):
        create_dummy_author_with_followers(self.NUM_FOLLOWERS)

        c = Client()
        author = Author.objects.get(username='test')
        follower = Author.objects.get(username='test0')

        # test with valid author and follower ids
        response = c.get(f'/service/authors/{author.id}/followers/{follower.id}/')
        self.assertEqual(response.status_code, 200)

        # test with valid author id and invalid follower id
        response = c.get(f'/service/authors/{author.id}/followers/invalid_follower_id/')
        self.assertEqual(response.status_code, 404)

        # test with invalid author and follower ids
        response = c.get(f'/service/authors/invalid_author_id/followers/invalid_follower_id/')
        self.assertEqual(response.status_code, 404)


    def test_head(self):
        create_dummy_author_with_followers(self.NUM_FOLLOWERS)

        c = Client()
        author = Author.objects.get(username='test')
        follower = Author.objects.get(username='test0')

        # test with valid author and follower ids
        response = c.head(f'/service/authors/{author.id}/followers/{follower.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'')


    def test_delete(self):
        create_dummy_author_with_followers(self.NUM_FOLLOWERS)

        c = Client()
        author = Author.objects.get(username='test')
        follower = Author.objects.get(username='test0')

        # test with valid author and follower ids
        response = c.delete(f'/service/authors/{author.id}/followers/{follower.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(not author.followers.filter(id=follower.id).exists())


    def test_put(self):
        create_dummy_authors(2)

        c = Client()
        author = Author.objects.get(username='test0')
        foreign_author = Author.objects.get(username='test1')

        # test unauthenticated author
        response = c.put(f'/service/authors/{author.id}/followers/{foreign_author.id}/')
        self.assertEqual(response.status_code, 403)

        c.login(username=author.username, password='temporary')
        # test with valid author and foreign_author ids
        response = c.put(f'/service/authors/{author.id}/followers/{foreign_author.id}/')
        self.assertEqual(response.status_code, 201)

        # test with invalid author and foreign_author ids
        response = c.put(f'/service/authors/invalid_author_id/followers/invalid_foreign_author_id/')
        self.assertEqual(response.status_code, 404)
        
        # test with valid author id and invalid foreign_author id
        response = c.put(f'/service/authors/{author.id}/followers/invalid_foreign_author_id/')
        self.assertEqual(response.status_code, 404)

    

