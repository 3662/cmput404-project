from social_distribution.models import Author, Post


def create_dummy_authors(n):
    '''Creates n dummy authors in db.'''
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
