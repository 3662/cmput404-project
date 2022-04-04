import json 

from django.test import TestCase, Client

from .helper import create_dummy_authors, create_dummy_post, create_dummy_comments
from service.models import ServerNode
from social_distribution.models import Author, Post, Comment

class CommentsViewTestCase(TestCase):

    NUM_COMMENTS = 10

    def setUp(self):
        ServerNode.objects.create(host='testserver', is_local=True) 
        create_dummy_authors(2)
        post_author = Author.objects.get(username='test0')
        comment_author = Author.objects.get(username='test1')
        create_dummy_post(post_author, visibility='PUBLIC')
        post = Post.objects.get(title='Test Post')


    def test_get(self):
        comment_author = Author.objects.get(username='test1')
        post = Post.objects.get(title='Test Post')
        create_dummy_comments(self.NUM_COMMENTS, comment_author, post)

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
        self.assertEqual(len(data['comments']), self.NUM_COMMENTS)

        comments_data = data['comments']
        for c_data in comments_data:
            comment_id = c_data['id'].split('/')[-1]
            comment = Comment.objects.get(id=comment_id)
            self.assertDictEqual(c_data, comment.get_detail_dict())


    def test_post(self):
        c = Client()
        post_author = Author.objects.get(username='test0')
        comment_author = Author.objects.get(username='test1')
        post = Post.objects.get(title='Test Post')
        
        # test multiple comments
        num_comments = 5
        for i in range(num_comments):
            comment_data = {
                'type': 'comment',
                'author': comment_author.get_detail_dict(),
                'comment': f'Test comment{i}',
                'contentType': 'text/plain',
            }
            # test with valid data
            response = c.post(f'/service/authors/{post_author.id}/posts/{post.id}/comments', json.dumps(comment_data), content_type="application/json")
            self.assertEqual(response.status_code, 201, response.content)
            self.assertTrue(Comment.objects.filter(author=comment_author, post=post, content=comment_data['comment']).exists())
        self.assertEqual(len(Comment.objects.filter(author=comment_author, post=post)), num_comments)
        
        # test with invalid type
        comment_data = {
            'type': 'commentt',
            'author': comment_author.get_detail_dict(),
            'comment': 'Test comment',
            'contentType': 'text/plain',
        }
        response = c.post(f'/service/authors/{post_author.id}/posts/{post.id}/comments', json.dumps(comment_data), content_type="application/json")
        self.assertEqual(response.status_code, 400, response.content)

        # test with missing comment content
        comment_data = {
            'type': 'comment',
            'author': comment_author.get_detail_dict(),
            'contentType': 'text/plain',
        }
        response = c.post(f'/service/authors/{post_author.id}/posts/{post.id}/comments', json.dumps(comment_data), content_type="application/json")
        self.assertEqual(response.status_code, 400, response.content)


