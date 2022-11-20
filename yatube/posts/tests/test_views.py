import shutil
import tempfile

from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from ..models import Group, Post, User

USERNAME = 'user'
TEST_USER = 'test_user'
SLUG_1 = 'slug-one'
SLUG_2 = 'slug-two'
SLUG_TEST = 'slug-test'

INDEX_URL = reverse('posts:index')
GROUP_LIST_URL_1 = reverse('posts:group_list', args=[SLUG_1])
GROUP_LIST_URL_2 = reverse('posts:group_list', args=[SLUG_2])
GROUP_LIST_URL_3 = reverse('posts:group_list', args=[SLUG_TEST])
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
FOLLOW_INDEX_URL = reverse('posts:follow_index')

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
UPLOADED = SimpleUploadedFile(
    name='small.gif',
    content=SMALL_GIF,
    content_type='image/gif'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.group = Group.objects.create(
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
            text='Тестовый пост',
            group=cls.group,
            image=UPLOADED,
        )
        cls.another = Client()
        cls.another.force_login(cls.user)
        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[cls.post.id])

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def asert_page_has_attribute(self, post):
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.id, self.post.id)
        self.assertEqual(post.image, self.post.image)

    def test_pages_show_correct_context(self):
        """
        Шаблоны страниц index, group_list, profile, post_detail
        сформированы с правильным контекстом.
        """
        cache.clear()
        urls = [
            [INDEX_URL, 'page_obj'],
            [GROUP_LIST_URL_1, 'page_obj'],
            [PROFILE_URL, 'page_obj'],
            [self.POST_DETAIL_URL, 'post'],
        ]
        for url, key in urls:
            with self.subTest(url=url, key=key):
                post = self.another.get(url)
                if key == 'page_obj':
                    self.assertEqual(len(post.context.get(key)), 1)
                    self.asert_page_has_attribute(post.context[key][0])
                elif key == 'post':
                    self.asert_page_has_attribute(post.context[key])

    def test_posts_group_context_group_list(self):
        """Группа в контексте групп-ленты без искажения атрибутов."""
        group = self.another.get(GROUP_LIST_URL_1).context.get('group')
        self.assertEqual(group, self.group)
        self.assertEqual(group.title, self.group.title)
        self.assertEqual(group.slug, self.group.slug)
        self.assertEqual(group.description, self.group.description)

    def test_post_not_in_another_group(self):
        """Пост не попал на чужую групп-ленту."""
        self.assertNotIn(
            self.post,
            self.another.get(GROUP_LIST_URL_2).context.get(
                'page_obj'
            )
        )

    def test_posts_page_author_in_context_profile(self):
        """Проверка наличия автора в контексте профиля."""
        self.assertEqual(
            self.user,
            self.another.get(PROFILE_URL).context.get('author')
        )

    def test_posts_index_page_caches(self):
        """Проверка работа кеша на главной странице шаблона index."""
        response_1 = self.another.get(INDEX_URL).content
        Post.objects.all().delete()
        response_2 = self.another.get(INDEX_URL).content
        self.assertEqual(response_1, response_2)
        cache.clear()
        response_3 = self.another.get(INDEX_URL).content
        self.assertNotEqual(response_1, response_3)

    def test_404page_use_correct_template(self):
        """Страница 404 использует соответствующий шаблон."""
        response = self.another.get('/unexisting_page/')
        self.assertTemplateUsed(response, 'core/404.html')

    def test_posts_new_post_found_in_followers_news(self):
        """
        Новая запись пользователя появляется в ленте тех,
        кто на него подписан.
        """
        urls = [
            FOLLOW_INDEX_URL,
            GROUP_LIST_URL_2
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertNotIn(
                    self.post,
                    self.another.get(url).context['page_obj']
                )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUp(self) -> None:
        self.user = User.objects.create_user(username=USERNAME)
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug=SLUG_TEST,
            description='Тестовое описание',
        )
        Post.objects.bulk_create(
            Post(
                author=self.user,
                text=f'Тестовый текст {i}-го поста',
                group=self.group
            ) for i in range(settings.LIMIT_OF_POSTS + 1)
        )
        self.another = Client()
        self.another.force_login(self.user)

    def test_correct_the_number_of_posts_on_the_pages(self):
        """Проверка количества постов на странице первой и второй."""
        cache.clear()
        NEXT_PAGE = '?page=2'
        urls = [
            [INDEX_URL, settings.LIMIT_OF_POSTS],
            [GROUP_LIST_URL_3, settings.LIMIT_OF_POSTS],
            [PROFILE_URL, settings.LIMIT_OF_POSTS],
            [INDEX_URL + NEXT_PAGE, 1],
            [GROUP_LIST_URL_3 + NEXT_PAGE, 1],
            [PROFILE_URL + NEXT_PAGE, 1],
        ]
        for url, posts_count in urls:
            with self.subTest(url=url):
                self.assertEqual(
                    len(self.another.get(url).context['page_obj']),
                    posts_count
                )
