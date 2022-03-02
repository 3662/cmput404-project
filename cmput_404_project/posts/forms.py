from django.forms import ModelForm
from social_distribution.models import Post
from social_distribution.models import Comment

class PostForm(ModelForm):

    class Meta:
        model = Post
        fields = ('title', 'description', 'image')

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['image'].required = False

class CommentForm(ModelForm):
    
    class Meta:
        model = Comment
        fields = ('content',)
    
    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)