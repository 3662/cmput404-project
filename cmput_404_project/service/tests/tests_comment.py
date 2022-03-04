from django.test import TestCase, Client

from .helper import create_dummy_authors, create_dummy_post, create_dummy_comments
from social_distribution.models import Author, Post, Comment

class CommentsViewTestCase(TestCase):

    NUM_COMMENTS = 10

    def setUp(self):
        create_dummy_authors(2)
        post_author = Author.objects.get(username='test0')
        comment_author = Author.objects.get(username='test1')
        create_dummy_post(post_author, visibility='PUBLIC')
        post = Post.objects.get(title='Test Post')
        create_dummy_comments(self.NUM_COMMENTS, comment_author, post)


    def test_get(self):
        c = Client()
        author = Author.objects.get(username='test0')
        comment_author = Author.objects.get(username='test1')
        post = Post.objects.get(title='Test Post')

        # test with invalid ids
        response = c.get(f'/service/authors/invalid_author_id/posts/invalid_post_id/comments?page=1&size={self.NUM_COMMENTS}')
        self.assertEqual(response.status_code, 404)

        # test with invalid page
        response = c.get(f'/service/authors/{author.id}/posts/{post.id}/comments?page=3&size={self.NUM_COMMENTS}')
        self.assertEqual(response.status_code, 404)

        # test with valid ids
        response = c.get(f'/service/authors/{author.id}/posts/{post.id}/comments?page=1&size={self.NUM_COMMENTS}')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['type'], 'comments')
        self.assertEqual(len(data['items']), self.NUM_COMMENTS)

        comments_data = data['items']
        for c_data in comments_data:
            comment_id = c_data['id'].split('/')[-1]
            comment = Comment.objects.get(id=comment_id)
            self.assertDictEqual(c_data, comment.get_detail_dict())




