from django.test import TestCase
from django.urls import reverse

SLUG = 'slug-for-test'
USERNAME = 'user'
POST_ID = 1

urls = [
    ['/', 'index', None],
    [f'/group/{SLUG}/', 'group_list', [SLUG]],
    [f'/profile/{USERNAME}/', 'profile', [USERNAME]],
    ['/create/', 'post_create', None],
    [f'/posts/{POST_ID}/', 'post_detail', [POST_ID]],
    [f'/posts/{POST_ID}/edit/', 'post_edit', [POST_ID]],
    [f'/posts/{POST_ID}/comment/', 'add_comment', [POST_ID]],
    ['/follow/', 'follow_index', None],
    [f'/profile/{USERNAME}/follow/', 'profile_follow', [USERNAME]],
    [f'/profile/{USERNAME}/unfollow/', 'profile_unfollow', [USERNAME]],
]


class RoutesTest(TestCase):

    def test_urls_routes(self):
        """Проверка ожидаемых маршрутов URL"""
        for url, route, args in urls:
            self.assertEqual(
                url,
                reverse((f'posts:{route}'), args=args)
            )
