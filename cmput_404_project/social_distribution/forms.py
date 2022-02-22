from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import Author


class AuthorCreationForm(UserCreationForm):

    class Meta:
        model = Author
        fields = ('username', 'first_name', 'last_name', 'profile_image', 'host', 'github')


class AuthorChangeForm(UserChangeForm):

    class Meta:
        model = Author
        fields = ('username', 'first_name', 'last_name', 'profile_image', 'host', 'github')

