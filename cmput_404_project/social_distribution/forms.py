from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import Author


class AuthorCreationForm(UserCreationForm):

    class Meta:
        model = Author
        fields = ('username',)


class AuthorChangeForm(UserChangeForm):

    class Meta:
        model = Author
        fields = ('username',)

