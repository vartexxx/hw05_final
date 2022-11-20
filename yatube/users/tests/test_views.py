from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UsersViewsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')

    def setUp(self) -> None:
        self.guest = Client()
        self.another = Client()
        self.another.force_login(self.user)

    def test_users_authorized_pages_use_correct_template(self):
        """
        URL - адрес приложения users использует соответстующий шаблон
        для авторизованнного пользователя.
        """
        templates_pages_names = {
            'users/signup.html':
            reverse(
                'users:signup'
            ),
            'users/logged_out.html':
            reverse(
                'users:logout'
            ),
            'users/login.html':
            reverse(
                'users:login'
            ),
            'users/password_reset_form.html':
            reverse(
                'users:password_reset_form'
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.another.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_users_no_authorized_pages_use_correct_template(self):
        """
        URL - адрес приложеия users использует соответствующий шаблон
        для неавторизованного пользователя-автора.
        """
        templates_pages_names = {
            'users/signup.html':
            reverse(
                'users:signup'
            ),
            'users/logged_out.html':
            reverse(
                'users:logout'
            ),
            'users/login.html':
            reverse(
                'users:login'
            ),
            'users/password_reset_form.html':
            reverse(
                'users:password_reset_form'
            ),
            'users/password_reset_done.html':
            reverse(
                'users:password_reset_done'
            )
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_signup_users_page_show_correct_context(self):
        """
        Шаблон signup при регистрации пользователя сформирован
        с правильным контекстом.
        """
        response = self.another.get(reverse('users:signup'))
        form_users_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
        }
        for value, expected in form_users_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
