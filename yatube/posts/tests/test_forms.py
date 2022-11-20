import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Post, Group, Comment, User

USERNAME = 'user'
SLUG_1 = 'slug-one'
SLUG_2 = 'slug-two'
IMAGE_NAME_1 = 'small.gif'
IMAGE_CONTENT_TYPE_1 = 'image/gif'
IMAGE_CONTENT_1 = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3A'
)
IMAGE_NAME_2 = 'small-two.gif'
IMAGE_CONTENT_TYPE_2 = 'image-two/gif'
IMAGE_CONTENT_2 = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x30\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x04\x00\x2C\x00\x02\x00\x00'
    b'\x07\x00\x31\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3A'
)

POST_CREATE_URL = reverse('posts:post_create')
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
LOGIN = reverse('users:login')

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.group_1 = Group.objects.create(
            title='Тестовая группа 1',
            slug=SLUG_1,
            description='Тестовое описание 1',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug=SLUG_2,
            description='Тестовое описание 2',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост 1',
            group=cls.group_1,
        )
        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[cls.post.id])
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[cls.post.id])
        cls.COMMENT = reverse('posts:add_comment', args=[cls.post.id])
        cls.COMMENT_REDIRECT = f'{LOGIN}?next={cls.COMMENT}'
        cls.posts_initially = Post.objects.count()
        cls.comments_initially = Comment.objects.count()
        cls.guest = Client()
        cls.another = Client()
        cls.another.force_login(cls.user)
        cls.image_1 = SimpleUploadedFile(
            name=IMAGE_NAME_1,
            content=IMAGE_CONTENT_1,
            content_type=IMAGE_CONTENT_TYPE_1,
        )
        cls.image_2 = SimpleUploadedFile(
            name=IMAGE_NAME_2,
            content=IMAGE_CONTENT_2,
            content_type=IMAGE_CONTENT_TYPE_2,
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_create_post(self):
        """Проверка создания новой записи"""
        posts_before_create_new = set(Post.objects.all())
        form_data = {
            'text': 'Тестовый пост',
            'group': self.group_1.id,
            'image': self.image_1
        }
        response = self.another.post(
            POST_CREATE_URL,
            data=form_data,
            follow=True
        )
        self.assertEqual(
            Post.objects.count(),
            self.posts_initially + 1
        )
        created_posts = set(Post.objects.all()) - posts_before_create_new
        self.assertEqual(len(created_posts), 1)
        post = created_posts.pop()
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.author, self.user)
        self.assertRedirects(response, PROFILE_URL)
        self.assertEqual(
            post.image.name,
            f'posts/{form_data["image"].name}'
        )

    def test_edit_post(self):
        """Проверка редактирования записи"""
        form_data = {
            'text': 'Изменённый текст 123',
            'group': self.group_2.id,
            'image': self.image_2,
        }
        response = self.another.post(
            self.POST_EDIT_URL,
            data=form_data,
            follow=True
        )
        post = response.context['post']
        self.assertRedirects(response, self.POST_DETAIL_URL)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(
            post.image.name,
            f'posts/{form_data["image"].name}'
        )

    def test_create_post_page_show_correct_context(self):
        """
        Шаблон create_post при создании поста сформирован
        с правильным контекстом.
        """
        response = self.another.get(POST_CREATE_URL)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_posts_comment_form(self):
        """Проверка формы добавления комментария"""
        comments_before_create_new = set(Comment.objects.all())
        form_data = {
            'text': 'Тестовый комментарий к посту'
        }
        response = self.another.post(
            self.COMMENT,
            data=form_data,
            follow=True
        )
        self.assertEqual(
            Comment.objects.count(),
            self.comments_initially + 1
        )
        created_com = set(Comment.objects.all()) - comments_before_create_new
        self.assertEqual(len(created_com), 1)
        comment = created_com.pop()
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.post, self.post)
        self.assertRedirects(response, self.POST_DETAIL_URL)

    def test_posts_comments_show_correct_context(self):
        """
        Шаблон добавления комментария сформирован
        с правильным контекстом
        """
        response = self.another.get(self.POST_DETAIL_URL)
        form_fields = {
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_posts_comments_guest_cant_create(self):
        """Проверка, что гость не может создать комментарий"""
        form_data = {
            'text': 'Новый комментарий от гостя'
        }
        response = self.guest.post(
            self.COMMENT,
            data=form_data
        )
        self.assertEqual(Comment.objects.count(), 0)
        self.assertRedirects(
            response,
            self.COMMENT_REDIRECT
        )
