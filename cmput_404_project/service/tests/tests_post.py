import uuid
import json

from django.test import TestCase, Client
from django.core.exceptions import ObjectDoesNotExist

from social_distribution.models import Author, Post
from .helper import create_dummy_authors, create_dummy_post



class PostViewTestCase(TestCase):

    def setUp(self):
        create_dummy_authors(1)

    def test_get(self):
        c = Client()
        author = Author.objects.get(username='test0')

        # test with friends-only post
        create_dummy_post(author, visibility='FRIENDS', content_type='text/plain')
        post = Post.objects.get(title='Test Post')
        response = c.get(f'/service/authors/{author.id}/posts/{post.id}/')
        self.assertEqual(response.status_code, 404)
        post.delete()

        create_dummy_post(author, visibility='PUBLIC', content_type='text/plain')
        post = Post.objects.get(title='Test Post')

        # test with invalid post id
        response = c.get(f'/service/authors/{author.id}/posts/invalid_post_id/')
        self.assertEqual(response.status_code, 404)

        # test with valid post id
        response = c.get(f'/service/authors/{author.id}/posts/{post.id}/')
        self.assertEqual(response.status_code, 200)

        self.assert_post_data(post, author, response.json())


    def test_head(self):
        c = Client()
        author = Author.objects.get(username='test0')
        visibility = 'PUBLIC'
        create_dummy_post(author, visibility=visibility, content_type='text/plain')
        post = Post.objects.get(title='Test Post')

        # test with invalid post id
        response = c.head(f'/service/authors/{author.id}/posts/{post.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'')


    def test_post(self):
        c = Client()

        author = Author.objects.get(username='test0')
        visibility = 'PUBLIC'
        create_dummy_post(author, visibility=visibility, content_type='text/plain')
        post = Post.objects.get(title='Test Post')

        # test without being signed in
        response = c.post(f'/service/authors/{author.id}/posts/{post.id}/')
        self.assertEqual(response.status_code, 403)

        c.login(username=author.username, password='temporary')

        before_published = post.published
        before_modified = post.modified

        # post with valid data
        data = {
            'title': 'Updated Test Post Title',
            'description': 'Updated Test Post description',
            'content_type': 'text/plain',
            'content': 'Updated test post content', 
            'categories': 'updated,test,post,categories',
            'visibility': 'PUBLIC',
        }
        response = c.post(f'/service/authors/{author.id}/posts/{post.id}/', data)
        self.assertEqual(response.status_code, 200)

        post = Post.objects.get(id=post.id)     # get updated post

        # test timestamps
        self.assertTrue(before_published == post.published)
        self.assertTrue(before_modified < post.modified)

        # test updated fields 
        response = c.get(f'/service/authors/{author.id}/posts/{post.id}/')
        self.assertEqual(response.status_code, 200)
        self.assert_post_data(post, author, response.json())

        # post with invalid data
        data = {
            'title': 'Updated Test Post Title',
            'description': 'Updated Test Post description',
            'content_type': 'text/plain',
            'content': 'Updated test post content', 
            # missing data
        }
        response = c.post(f'/service/authors/{author.id}/posts/{post.id}/', data)
        self.assertEqual(response.status_code, 400)


    def test_delete(self):
        c = Client()

        author = Author.objects.get(username='test0')
        visibility = 'PUBLIC'
        create_dummy_post(author, visibility=visibility, content_type='text/plain')
        post = Post.objects.get(title='Test Post')

        response = c.delete(f'/service/authors/{author.id}/posts/{post.id}/')
        self.assertEqual(response.status_code, 200)

        # make sure the post is deleted from database
        with self.assertRaises(ObjectDoesNotExist):
            Post.objects.get(id=post.id)

        response = c.delete(f'/service/authors/{author.id}/posts/{post.id}/')
        self.assertEqual(response.status_code, 404, 'Retrieving deleted post should return 404')


    def test_put(self):
        c = Client()
        author = Author.objects.get(username='test0')
        post_id = uuid.uuid4()
        data = {
            'title': 'Test Post',
            'description': 'Test Post description',
            'content_type': 'text/plain',
            'content': 'Test post content', 
            'categories': 'test,post,categories',
            'visibility': 'PUBLIC',
        }
        response = c.put(f'/service/authors/{author.id}/posts/{post_id}/', json.dumps(data))
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Post.objects.filter(id=post_id, author=author).exists())

        # test whether the data is saved in db
        response = c.get(f'/service/authors/{author.id}/posts/{post_id}/')
        self.assertEqual(response.status_code, 200)
        self.assert_post_data(Post.objects.get(id=post_id, author=author), author, response.json())

        data = {
            'title': 'Updated Test Post',
            'description': 'Updated Test Post description',
            'content_type': 'text/plain',
            'content': 'Updated Test post content', 
            'categories': 'test,post,categories',
            'visibility': 'PUBLIC',
        }
        # test with non-json data
        response = c.put(f'/service/authors/{author.id}/posts/{post_id}/', data)
        self.assertEqual(response.status_code, 400)
        # test update without being authenticated
        response = c.put(f'/service/authors/{author.id}/posts/{post_id}/', json.dumps(data))
        self.assertEqual(response.status_code, 403)
        # test with valid json data and authenticated user
        c.login(username=author.username, password='temporary')
        response = c.put(f'/service/authors/{author.id}/posts/{post_id}/', json.dumps(data))
        self.assertEqual(response.status_code, 200)
        # test with invalid data
        data.pop('title')
        response = c.put(f'/service/authors/{author.id}/posts/{post_id}/', data)
        self.assertEqual(response.status_code, 400)

        # test whether the data is saved in db
        response = c.get(f'/service/authors/{author.id}/posts/{post_id}/')
        self.assertEqual(response.status_code, 200)
        self.assert_post_data(Post.objects.get(id=post_id, author=author), author, response.json())



    def assert_post_data(self, post, author, data):
        # TODO test source, origin, comments
        self.assertEqual(data['type'], 'post')
        self.assertEqual(data['title'], post.title)
        self.assertEqual(data['id'], post.get_id_url())
        self.assertEqual(data['description'], post.description)
        self.assertEqual(data['contentType'], post.content_type)
        self.assertEqual(data['content'], post.content)
        self.assertEqual(data['categories'], post.get_list_of_categories())
        self.assertEqual(data['count'], post.count)
        self.assertEqual(data['published'], post.get_iso_published())
        self.assertEqual(data['visibility'], post.visibility)
        self.assertEqual(data['unlisted'], False)

        # test author of the post
        self.assertEqual(data['author']['type'], 'author')
        self.assertEqual(data['author']['id'], author.get_id_url())
        self.assertEqual(data['author']['host'], author.host)
        self.assertEqual(data['author']['displayName'], author.get_full_name())
        self.assertEqual(data['author']['url'], author.get_profile_url())
        self.assertEqual(data['author']['github'], author.github)
        self.assertEqual(data['author']['profileImage'], author.profile_image)





