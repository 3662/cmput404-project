import uuid
import json

from django.test import TestCase, Client
from django.core.exceptions import ObjectDoesNotExist

from social_distribution.models import Author, Post
from .helper import create_dummy_authors, create_dummy_post, create_dummy_posts


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
        response = c.get(f'/service/authors/{author.id}/posts/invalid_post_id')
        self.assertEqual(response.status_code, 404)

        # test with valid post id
        response = c.get(f'/service/authors/{author.id}/posts/{post.id}')
        self.assertEqual(response.status_code, 200)

        self.assertDictEqual(response.json(), post.get_detail_dict())


    def test_head(self):
        c = Client()
        author = Author.objects.get(username='test0')
        visibility = 'PUBLIC'
        create_dummy_post(author, visibility=visibility, content_type='text/plain')
        post = Post.objects.get(title='Test Post')

        # test with valid post id
        response = c.head(f'/service/authors/{author.id}/posts/{post.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'')


    def test_post(self):
        c = Client()

        author = Author.objects.get(username='test0')
        visibility = 'PUBLIC'
        create_dummy_post(author, visibility=visibility, content_type='text/plain')
        post = Post.objects.get(title='Test Post')

        # test without being signed in
        response = c.post(f'/service/authors/{author.id}/posts/{post.id}')
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
        response = c.post(f'/service/authors/{author.id}/posts/{post.id}', data)
        self.assertEqual(response.status_code, 200)

        post = Post.objects.get(id=post.id)     # get updated post

        # test timestamps
        self.assertTrue(before_published == post.published)
        self.assertTrue(before_modified < post.modified)

        # test updated fields 
        response = c.get(f'/service/authors/{author.id}/posts/{post.id}')
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), post.get_detail_dict())

        # post with invalid data
        data = {
            'title': 'Updated Test Post Title',
            'description': 'Updated Test Post description',
            'content_type': 'text/plain',
            'content': 'Updated test post content', 
            # missing data
        }
        response = c.post(f'/service/authors/{author.id}/posts/{post.id}', data)
        self.assertEqual(response.status_code, 400)


    def test_delete(self):
        c = Client()

        author = Author.objects.get(username='test0')
        visibility = 'PUBLIC'
        create_dummy_post(author, visibility=visibility, content_type='text/plain')
        post = Post.objects.get(title='Test Post')

        response = c.delete(f'/service/authors/{author.id}/posts/{post.id}')
        self.assertEqual(response.status_code, 204)

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
        response = c.put(f'/service/authors/{author.id}/posts/{post_id}', json.dumps(data))
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Post.objects.filter(id=post_id, author=author).exists())

        # test whether the data is saved in db
        response = c.get(f'/service/authors/{author.id}/posts/{post_id}')
        self.assertEqual(response.status_code, 200)
        post = Post.objects.get(id=post_id, author=author)
        self.assertDictEqual(response.json(), post.get_detail_dict())

        data = {
            'title': 'Updated Test Post',
            'description': 'Updated Test Post description',
            'content_type': 'text/plain',
            'content': 'Updated Test post content', 
            'categories': 'test,post,categories',
            'visibility': 'PUBLIC',
        }
        # test with non-json data
        response = c.put(f'/service/authors/{author.id}/posts/{post_id}', data)
        self.assertEqual(response.status_code, 400)
        # test update without being authenticated
        response = c.put(f'/service/authors/{author.id}/posts/{post_id}', json.dumps(data))
        self.assertEqual(response.status_code, 403)
        # test with valid json data and authenticated user
        c.login(username=author.username, password='temporary')
        response = c.put(f'/service/authors/{author.id}/posts/{post_id}', json.dumps(data))
        self.assertEqual(response.status_code, 200)
        # test with invalid data
        data.pop('title')
        response = c.put(f'/service/authors/{author.id}/posts/{post_id}', data)
        self.assertEqual(response.status_code, 400)

        # test whether the data is saved in db
        response = c.get(f'/service/authors/{author.id}/posts/{post_id}')
        self.assertEqual(response.status_code, 200)
        post = Post.objects.get(id=post_id, author=author)
        self.assertDictEqual(response.json(), post.get_detail_dict())


class PostsViewTestCase(TestCase):

    def setUp(self):
        create_dummy_authors(1)

    def test_get(self):
        c = Client()
        author = Author.objects.get(username='test0')
        num_public_posts = 10
        num_friends_posts = 5
        create_dummy_posts(num_public_posts, author, visibility='PUBLIC')
        create_dummy_posts(num_friends_posts, author, visibility='FRIENDS')

        response = c.get(f'/service/authors/{author.id}/posts?page=1&size={num_public_posts}')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['type'], 'posts')
        self.assertEqual(len(data['items']), num_public_posts)

        # test the first three posts
        posts_data = data['items'][:3]
        for post_data in posts_data:
            post_id = post_data['id'].split('/')[-1]
            post = Post.objects.get(id=post_id, author=author)
            self.assertDictEqual(post_data, post.get_detail_dict())

        # test invalid page
        response = c.get(f'/service/authors/{author.id}/posts?page=2&size={num_public_posts}')
        self.assertEqual(response.status_code, 404)


    def test_head(self):
        c = Client()
        author = Author.objects.get(username='test0')
        num_public_posts = 10
        num_friends_posts = 5
        create_dummy_posts(num_public_posts, author, visibility='PUBLIC')
        create_dummy_posts(num_friends_posts, author, visibility='FRIENDS')

        response = c.head(f'/service/authors/{author.id}/posts?page=1&size={num_public_posts}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'')


    def test_post(self):
        c = Client()
        author = Author.objects.get(username='test0')

        data = {
            'title': 'Test Post',
            'description': 'Test Post description',
            'content_type': 'text/plain',
            'content': 'Test post content', 
            'categories': 'test,post,categories',
            'visibility': 'PUBLIC',
        }
        # test with valid data
        response = c.post(f'/service/authors/{author.id}/posts', data)
        self.assertEqual(response.status_code, 201)

        # test fields of newly created post
        post = Post.objects.get(title='Test Post', author=author)
        response = c.get(f'/service/authors/{author.id}/posts/{post.id}')
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), post.get_detail_dict())

        # test with invalid data
        data['title'] = 'a' * 200
        response = c.post(f'/service/authors/{author.id}/posts', data)
        self.assertEqual(response.status_code, 400)







