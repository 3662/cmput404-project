from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from social_distribution.models import Author


class AuthorCreationForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = Author
        fields = ('username', 'first_name', 'last_name', 'profile_image', 'github')


class AuthorChangeForm(UserChangeForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = Author
        fields = ('first_name', 'last_name', 'profile_image', 'github')

