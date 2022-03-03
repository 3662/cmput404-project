from social_distribution.models import Author


def create_dummy_authors(n):
    '''Creates n dummy authors in db.'''
    for i in range(n):
        Author.objects.create_user(username=f'test{i}', 
                                    password=f'test{i}_password',
                                    host='http://localhost:8000/', 
                                    github=f'https://github.com/test{i}',
                                    profile_image='https://avatars.githubusercontent.com/u/55664235?v=4')