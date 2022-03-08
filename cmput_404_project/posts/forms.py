from django.forms import ModelForm
from social_distribution.models import Post, Comment, Like

class PostForm(ModelForm):

    class Meta:
        model = Post
        fields = ('title', 'description', 'content_type', 'content', 'image', 'categories', 'visibility')

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['image'].required = False

class PrivatePostForm(ModelForm):

    class Meta:
        model = Post
        fields = ('title', 'description', 'image', 'recepient')

    def __init__(self, *args, **kwargs):
        super(PrivatePostForm, self).__init__(*args, **kwargs)
        self.fields['image'].required = False

class CommentForm(ModelForm):
    
    class Meta:
        model = Comment
        fields = ('content_type', 'content',)
    
    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
class PostLike(ModelForm):

    class Meta:
        model = Like
        # fields = ('post', 'author', 'summary')
        fields = ('author',)    # TODO update fields

    def __init__(self, *args, **kwargs):
        super(PostLike, self).__init__(*args, **kwargs)
        #self.fields['date_created'].required = False
