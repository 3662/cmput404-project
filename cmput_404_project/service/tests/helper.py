from social_distribution.models import Author, Post, Comment, Like


def create_dummy_authors(n):
    '''Creates n dummy authors.'''
    for i in range(n):
        Author.objects.create_user(username=f'test{i}', 
                                    password=f'temporary',
                                    first_name = f'Test{i}',
                                    last_name = 'Example',
                                    host='http://localhost:8000/', 
                                    github=f'https://github.com/test{i}',
                                    profile_image='https://avatars.githubusercontent.com/u/55664235?v=4')


def create_dummy_post(author, visibility='PUBLIC', content_type='text/plain'):
    '''Creates a dummy post for the given author'''

    if visibility not in map(lambda p:p[0], Post.VISIBILITY_CHOICES):
        raise ValueError('Invalid visibility')
    
    if content_type not in map(lambda p:p[0], Post.CONTENT_TYPE_CHOICES):
        raise ValueError('Invalid content type')

    Post.objects.create(author=author, 
                        visibility=visibility,
                        title='Test Post',
                        source='',
                        origin='',
                        description='Test post description',
                        content_type=content_type,
                        content='Test post content',
                        categories='test,cmput404')


def create_dummy_posts(n, author, visibility='PUBLIC', content_type='text/plain'):
    '''Creates n dummy posts for the given author'''

    if visibility not in map(lambda p:p[0], Post.VISIBILITY_CHOICES):
        raise ValueError('Invalid visibility')

    if content_type not in map(lambda p:p[0], Post.CONTENT_TYPE_CHOICES):
        raise ValueError('Invalid content type')

    for i in range(n):
        Post.objects.create(author=author, 
                            visibility=visibility,
                            title=f'Test Post{i}',
                            source='',
                            origin='',
                            description=f'Test post{i} description',
                            content_type=content_type,
                            content=f'Test post{i} content',
                            categories='test,cmput404')


def create_dummy_author_with_followers(num_followers):
    '''Creates a dummy author with num_followers followers.'''
    author = Author.objects.create_user(username='test', 
                                        password='temporary',
                                        first_name = 'Test',
                                        last_name = 'Example',
                                        host='http://localhost:8000/', 
                                        github=f'https://github.com/test',
                                        profile_image='https://avatars.githubusercontent.com/u/55664235?v=4')
                            
    for i in range(num_followers):
        follower = Author.objects.create_user(username=f'test{i}', 
                                              password=f'temporary',
                                              first_name = f'Test{i}',
                                              last_name = 'Example',
                                              host='http://localhost:8000/', 
                                              github=f'https://github.com/test{i}',
                                              profile_image='https://avatars.githubusercontent.com/u/55664235?v=4')
        author.followers.add(follower)


def create_dummy_comments(n, author, post):
    '''Creates n dummy comments to the post written by the author'''
    for i in range(n):
        Comment.objects.create(author=author, 
                               post=post,
                               content_type='text/plain',
                               content=f'Test Comment{i}')
        

def create_dummy_likes_to_post(like_authors, post):
    '''Creates likes from like_authors to the post'''
    for like_author in like_authors:
        Like.objects.create(author=like_author,
                            author_url = like_author.get_id_url(),
                            object_type='POST',
                            object_url=post.get_id_url())


def create_dummy_likes_to_comment(like_authors, comment):
    '''Creates likes from like_authors to the comment'''
    for like_author in like_authors:
        Like.objects.create(author=like_author,
                            author_url = like_author.get_id_url(),
                            object_type='COMMENT',
                            object_url=comment.get_id_url())

    

