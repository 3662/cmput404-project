from django.forms import ModelForm
from social_distribution.models import Post

class PostForm(ModelForm):

    class Meta:
        model = Post
        fields = ('title', 'description')