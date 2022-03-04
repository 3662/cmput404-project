from tkinter import W
from venv import create
from django.test import TestCase, Client

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
        # self.assertEqual(response.status_code, 403)

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





