from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class PostsCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    def setUp(self) -> None:
        self.guest = Client()

    def test_users_create_new_user(self):
        """Тест создания нового пользователя"""
        users_count = User.objects.count()
        users_form_data = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'username': 'new_user',
            'email': 'test_user@yandex.ru',
            'password1': '123456789yandex',
            'password2': '123456789yandex'
        }
        response = self.guest.post(
            reverse('users:signup'),
            data=users_form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:index'
            )
        )
        self.assertEqual(User.objects.count(), users_count + 1)
        last_user = User.objects.all().last()
        self.assertEqual(last_user.first_name, users_form_data['first_name'])
        self.assertEqual(last_user.last_name, users_form_data['last_name'])
        self.assertEqual(last_user.username, users_form_data['username'])
        self.assertEqual(last_user.email, users_form_data['email'])
