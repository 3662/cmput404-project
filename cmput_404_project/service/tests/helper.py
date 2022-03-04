from social_distribution.models import Author, Post, Comment


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

    if visibility not in ['PUBLIC', 'FRIENDS']:
        raise ValueError('Invalid visibility')
    
    if content_type not in ['text/plain', 'text/markdown', 'application/base64', 'image/png;base64', 'image/jpeg;base64']:
        raise ValueError('Invalid content type')

    Post.objects.create(author=author, 
                        visibility=visibility,
                        title='Test Post',
                        description='Test post description',
                        content_type=content_type,
                        content='Test post content',
                        categories='test,cmput404')


def create_dummy_posts(n, author, visibility='PUBLIC', content_type='text/plain'):
    '''Creates n dummy posts for the given author'''

    if visibility not in ['PUBLIC', 'FRIENDS']:
        raise ValueError('Invalid visibility')

    if content_type not in ['text/plain', 'text/markdown', 'application/base64', 'image/png;base64', 'image/jpeg;base64']:
        raise ValueError('Invalid content type')

    for i in range(n):
        Post.objects.create(author=author, 
                            visibility=visibility,
                            title=f'Test Post{i}',
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
        

    

