from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse


User = get_user_model()


class AboutURLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')

    def setUp(self) -> None:
        self.another = Client()
        self.another.force_login(self.user)

    def test_about_urls__exist_at_desired_location(self):
        """Страница доступна для авторизованного пользователя - автора"""
        urls_collection = {
            reverse(
                'about:author'
            ): HTTPStatus.OK,
            reverse(
                'about:tech'
            ): HTTPStatus.OK,
        }
        for url, http_status in urls_collection.items():
            with self.subTest(address=url):
                response = self.another.get(url)
                self.assertEqual(response.status_code, http_status)

    def test_about_pages_uses_correct_template(self):
        """URL - адрес приложения about использует соответствующий шаблон."""
        templates_pages_names = {
            'about/author.html':
            reverse(
                'about:author'
            ),
            'about/tech.html':
            reverse(
                'about:tech'
            )
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.another.get(reverse_name)
                self.assertTemplateUsed(response, template)
