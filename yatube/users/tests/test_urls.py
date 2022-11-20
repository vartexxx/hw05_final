from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

User = get_user_model()


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')

    def setUp(self) -> None:
        self.guest = Client()

        self.another = Client()
        self.another.force_login(self.user)

    def test_users_urls_exist_at_desired_location_for_guests(self):
        """Страницы доступны для неавторизованных пользователей"""
        urls_collection = {
            reverse(
                'users:signup'
            ): HTTPStatus.OK,
            reverse(
                'users:logout'
            ): HTTPStatus.OK,
            reverse(
                'users:login'
            ): HTTPStatus.OK,
            reverse(
                'users:password_reset_form'
            ): HTTPStatus.OK,
            reverse(
                'users:password_reset_done'
            ): HTTPStatus.OK,
        }
        for url, http_status in urls_collection.items():
            with self.subTest(address=url):
                response = self.guest.get(url)
                self.assertEqual(response.status_code, http_status)

    def test_users_urls_exist_at_desired_location_for_authorized_user(self):
        """Страницы доступны для авторизованных пользователей"""
        urls_collection = {
            reverse(
                'users:password_change_form_done'
            ): HTTPStatus.OK,
            reverse(
                'users:password_change_form'
            ): HTTPStatus.OK,
            reverse(
                'users:password_reset_done'
            ): HTTPStatus.OK,
        }
        for url, http_status in urls_collection.items():
            with self.subTest(address=url):
                response = self.another.get(url)
                self.assertEqual(response.status_code, http_status)
