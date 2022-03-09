from django.test import TestCase, Client

from .helper import create_dummy_authors, create_dummy_post, create_dummy_comments, create_dummy_likes_to_post, create_dummy_likes_to_comment
from social_distribution.models import Author, Post, Comment, Like


class PostLikesViewTestCase(TestCase):
    NUM_LIKE_AUTHORS = 5

    def setUp(self):
        create_dummy_authors(self.NUM_LIKE_AUTHORS + 1)
        author = Author.objects.get(username='test0')
        create_dummy_post(author, visibility='PUBLIC')

    def test_get(self):
        author = Author.objects.get(username='test0')
        like_authors = Author.objects.all().exclude(id=author.id)
        post = Post.objects.get(title='Test Post')
        create_dummy_likes_to_post(like_authors, post)

        c = Client()

        # test with valid ids
        response = c.get(f'/service/authors/{author.id}/posts/{post.id}/likes')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data['type'], 'liked')
        self.assertEqual(len(data['items']), self.NUM_LIKE_AUTHORS)
        for like_data in data['items']:
            self.assertEqual(like_data['@context'], 'https://www.w3.org/ns/activitystreams')
            self.assertTrue('summary' in like_data.keys())
            self.assertTrue('type' in like_data.keys())
            self.assertTrue('author' in like_data.keys())
            self.assertEqual(like_data['object'], post.get_id_url())

        # test with invalid post id
        response = c.get(f'/service/authors/{author.id}/posts/invalid_post_id/likes')
        self.assertEqual(response.status_code, 404)

        # test with invalid author id
        response = c.get(f'/service/authors/invalid_author_id/posts/{post.id}/likes')
        self.assertEqual(response.status_code, 404)
    

    def test_head(self):
        author = Author.objects.get(username='test0')
        like_authors = Author.objects.all().exclude(id=author.id)
        post = Post.objects.get(title='Test Post')
        create_dummy_likes_to_post(like_authors, post)

        c = Client()

        # test with valid ids
        response = c.head(f'/service/authors/{author.id}/posts/{post.id}/likes')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'')


class CommentLikesViewTestCase(TestCase):

    NUM_LIKE_AUTHORS = 5
    NUM_COMMENT_AUTHOR = 1
    NUM_COMMENTS = 1

    def setUp(self):
        create_dummy_authors(self.NUM_LIKE_AUTHORS + self.NUM_COMMENT_AUTHOR + 1)
        author = Author.objects.get(username='test0')
        create_dummy_post(author, visibility='PUBLIC')
        post = Post.objects.get(title='Test Post')
        comment_author = Author.objects.get(username='test1')
        create_dummy_comments(self.NUM_COMMENTS, comment_author, post)
    
    def test_get(self):
        author = Author.objects.get(username='test0')
        comment_author = Author.objects.get(username='test1')
        like_authors = Author.objects.all().exclude(id=author.id).exclude(id=comment_author.id)
        post = Post.objects.get(title='Test Post')
        comment = Comment.objects.get(content='Test Comment0', post=post, author=comment_author)
        create_dummy_likes_to_comment(like_authors, comment)

        c = Client()

        # test with valid ids
        response = c.get(f'/service/authors/{author.id}/posts/{post.id}/comments/{comment.id}/likes')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data['type'], 'liked')
        self.assertEqual(len(data['items']), self.NUM_LIKE_AUTHORS)

        for like_data in data['items']:
            self.assertEqual(like_data['@context'], 'https://www.w3.org/ns/activitystreams')
            self.assertTrue('summary' in like_data.keys())
            self.assertTrue('type' in like_data.keys())
            self.assertTrue('author' in like_data.keys())
            self.assertEqual(like_data['object'], comment.get_id_url())

        # test with invalid post id
        response = c.get(f'/service/authors/{author.id}/posts/invalid_post_id/comments/{comment.id}/likes')
        self.assertEqual(response.status_code, 404)

        # test with invalid comment id
        response = c.get(f'/service/authors/{author.id}/posts/{post.id}/comments/invalid_comment_id/likes')
        self.assertEqual(response.status_code, 404)

    def test_head(self):
        author = Author.objects.get(username='test0')
        comment_author = Author.objects.get(username='test1')
        like_authors = Author.objects.all().exclude(id=author.id).exclude(id=comment_author.id)
        post = Post.objects.get(title='Test Post')
        comment = Comment.objects.get(content='Test Comment0', post=post, author=comment_author)
        create_dummy_likes_to_comment(like_authors, comment)

        c = Client()

        # test with valid ids
        response = c.head(f'/service/authors/{author.id}/posts/{post.id}/comments/{comment.id}/likes')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'')
