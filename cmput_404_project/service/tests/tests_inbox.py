import uuid
import json

from django.test import TestCase, Client
from django.core.exceptions import ObjectDoesNotExist

from social_distribution.models import Author, Post, Inbox, InboxItem, FollowRequest, Like, Comment
from .helper import create_dummy_authors, create_dummy_post, create_dummy_posts, create_dummy_comments


class InboxViewTestCase(TestCase):

    def setUp(self):
        create_dummy_authors(2)

    def test_send_posts(self):
        c = Client()
        sender = Author.objects.get(username='test0')
        receiver = Author.objects.get(username='test1')

        # dummy posts
        num_posts = 5
        create_dummy_posts(num_posts, sender, 'PUBLIC', 'text/plain')
        posts = Post.objects.filter(author=sender).order_by('id')
        self.assertEqual(len(posts), num_posts)

        # sender sends dummy posts to receiver's inbox
        for post in posts:
            response = c.post(f'/service/authors/{receiver.id}/inbox', 
                              json.dumps(post.get_detail_dict()), 
                              content_type='application/json')
            self.assertEqual(response.status_code, 201)
        
        # assert InboxItems are created
        receiver_inbox = Inbox.objects.get(author=receiver)
        self.assertEqual(len(InboxItem.objects.filter(inbox=receiver_inbox)), num_posts)

        # assert their api objects
        items = InboxItem.objects.filter(inbox=receiver_inbox).order_by('object_id')
        for i in range(len(items)):
            self.assertDictEqual(items[i].get_detail_dict(), posts[i].get_detail_dict())
            
        # clear inbox
        response = c.delete(f'/service/authors/{receiver.id}/inbox')
        self.assertEqual(response.status_code, 204)
        self.assertTrue(not InboxItem.objects.filter(inbox=receiver_inbox).exists())


    def test_send_follow_request(self):
        c = Client()
        sender = Author.objects.get(username='test0')
        receiver = Author.objects.get(username='test1')
        
        # valid follow object
        data = {
            'type': 'Follow',
            'summary': 'Test0 wants to follow Test1',
            'actor': sender.get_detail_dict(),
            'object': receiver.get_detail_dict(),
        }
        response = c.post(f'/service/authors/{receiver.id}/inbox', 
                            json.dumps(data), 
                            content_type='application/json')
        self.assertEqual(response.status_code, 201)
        
        self.assertTrue(FollowRequest.objects.filter(from_author=sender, to_author=receiver).exists())
        fr = FollowRequest.objects.get(from_author=sender, to_author=receiver)
        # assert InboxItem is created
        receiver_inbox = Inbox.objects.get(author=receiver)
        self.assertTrue(InboxItem.objects.filter(inbox=receiver_inbox, object_url=None, object_id=fr.id).exists())

        # send Follow object again (should fail)
        response = c.post(f'/service/authors/{receiver.id}/inbox', 
                            json.dumps(data), 
                            content_type='application/json')
        self.assertEqual(response.status_code, 400)

        # clear inbox
        response = c.delete(f'/service/authors/{receiver.id}/inbox')
        self.assertEqual(response.status_code, 204)
        self.assertTrue(not InboxItem.objects.filter(inbox=receiver_inbox).exists())


    def test_send_like(self):
        c = Client()
        sender = Author.objects.get(username='test0')
        receiver = Author.objects.get(username='test1')

        create_dummy_post(receiver)
        post = Post.objects.get(author=receiver)

        # valid like object to post
        data = {
            '@context': 'https://www.w3.org/ns/activitystreams',
            'summary': 'Test0 Likes your post',
            'type': 'Like',
            'author': sender.get_detail_dict(),
            'object': post.get_id_url()
        }
        response = c.post(f'/service/authors/{receiver.id}/inbox', 
                            json.dumps(data), 
                            content_type='application/json')
        self.assertEqual(response.status_code, 201)

        self.assertTrue(Like.objects.filter(author=sender, 
                                            author_url=sender.get_id_url(), 
                                            object_type='POST', 
                                            object_url=post.get_id_url()).exists())
        
        like = Like.objects.get(author=sender, 
                                author_url=sender.get_id_url(), 
                                object_type='POST', 
                                object_url=post.get_id_url())

        receiver_inbox = Inbox.objects.get(author=receiver)
        self.assertTrue(InboxItem.objects.filter(inbox=receiver_inbox, object_url=None, object_id=like.id).exists())

        # clear inbox
        response = c.delete(f'/service/authors/{receiver.id}/inbox')
        self.assertEqual(response.status_code, 204)
        self.assertTrue(not InboxItem.objects.filter(inbox=receiver_inbox).exists())


    def test_send_comment(self):
        c = Client()
        sender = Author.objects.get(username='test0')
        receiver = Author.objects.get(username='test1')

        create_dummy_post(receiver)
        post = Post.objects.get(author=receiver)
        create_dummy_comments(1, sender, post)
        comment = Comment.objects.get(author=sender, post=post)

        response = c.post(f'/service/authors/{receiver.id}/inbox', 
                            json.dumps(comment.get_detail_dict()), 
                            content_type='application/json')
        self.assertEqual(response.status_code, 201)

        receiver_inbox = Inbox.objects.get(author=receiver)
        self.assertTrue(InboxItem.objects.filter(inbox=receiver_inbox, object_url=comment.get_id_url(), object_id=comment.id).exists())

        # clear inbox
        response = c.delete(f'/service/authors/{receiver.id}/inbox')
        self.assertEqual(response.status_code, 204)
        self.assertTrue(not InboxItem.objects.filter(inbox=receiver_inbox).exists())



