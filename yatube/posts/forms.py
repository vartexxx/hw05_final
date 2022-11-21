from django.forms import ModelForm

from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        fields = ('text', 'group', 'image',)
        model = Post


class CommentForm(ModelForm):
    class Meta:
        fields = ('text',)
        model = Comment
