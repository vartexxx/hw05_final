from django.conf import settings
from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=User.objects.create_user(username='auth'),
            text='Тестовый пост длинною больше 15 символов',
            group=cls.group,
        )

    def test_models_have_correct_object_names(self):
        """Корректно работает метод __str__ моделей Group, Post."""
        self.assertEqual(str(self.group), self.group.title)
        self.assertEqual(str(self.post), self.post.text[:settings.CROP_TEXT])

    def test_verbose_name(self):
        """Корректно прописаны verbose_name."""
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор поста',
            'group': 'Группа'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Post._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_help_text(self):
        """Корректно прописаны help_text"""
        field_help_texts = {
            'text': "Введите текст поста",
            'pub_date': "Укажите дату публикации",
            'author': "Укажите автора поста",
            'group': "Выбор группы",
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Post._meta.get_field(field).help_text,
                    expected_value
                )
