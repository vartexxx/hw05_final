from django.forms import ModelForm

from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        fields = ('text', 'group', 'image',)
        labels = {
            'text': 'Текст поста',
            'group': 'Группа поста',
            'image': 'Картинка поста',
        }
        model = Post


class CommentForm(ModelForm):
    class Meta:
        fields = ('text',)
        lables = {
            'text': 'Текст комментария'
        }
        model = Comment
