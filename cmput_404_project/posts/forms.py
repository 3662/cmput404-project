from django.forms import ModelForm
from social_distribution.models import Post,Like

class PostForm(ModelForm):

    class Meta:
        model = Post
        fields = ('title', 'description', 'image')

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['image'].required = False

class PostLike(ModelForm):

    class Meta:
        model = Like
        fields = ('post','author','summary')

    def __init__(self, *args, **kwargs):
        super(PostLike, self).__init__(*args, **kwargs)
        #self.fields['date_created'].required = False
