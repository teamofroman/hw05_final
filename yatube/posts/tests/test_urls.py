"""Тесты для проверки тестирования путей."""
from http import HTTPStatus

from django.core.cache import cache
from django.test import Client
from django.urls import reverse

from posts.models import Group, Post, User
from posts.tests.utils import YatubeTestBase


class TestPostsUrls(YatubeTestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_group = Group.objects.create(
            title='Test group',
            slug='test_group',
            description='This is test group',
        )
        cls.test_author = User.objects.create_user(
            username='testauthor',
        )
        cls.test_user = User.objects.create_user(
            username='testuser',
        )
        cls.test_post = Post.objects.create(
            text='This is test post text ' * 3,
            author=cls.test_author,
            group=cls.test_group,
        )

    def setUp(self):
        self.auth_client_author = Client()
        self.auth_client_author.force_login(TestPostsUrls.test_author)
        self.auth_client_user = Client()
        self.auth_client_user.force_login(TestPostsUrls.test_user)
        cache.clear()

    def test_posts_urls_unauth_user(self):
        """Тестируем пути для неавторизированного пользователя."""
        tests_urls = {
            '/': HTTPStatus.OK,
            f'/group/{TestPostsUrls.test_group.slug}/': HTTPStatus.OK,
            f'/profile/{TestPostsUrls.test_user.username}/': HTTPStatus.OK,
            f'/posts/{TestPostsUrls.test_post.id}/': HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
            '/group/unexisting_group/': HTTPStatus.NOT_FOUND,
            '/profile/unexisting_username/': HTTPStatus.NOT_FOUND,
            '/posts/2000/': HTTPStatus.NOT_FOUND,
        }

        for address, response_code in tests_urls.items():
            with self.subTest(address=address):
                response = self.get_response_get(
                    self.client,
                    address,
                )

                self.assertEqual(
                    response.status_code,
                    response_code,
                    (
                        f'Адрес {address} для неавторизированного '
                        f'пользователя работает не верно.'
                        f' Код ответа: {response.status_code}!='
                        f'{response_code}'
                    ),
                )

    def test_posts_redirect_unauth_user(self):
        """Тестируем редирект для неавторизированного пользователя."""
        tests_urls = [
            f'/posts/{TestPostsUrls.test_post.id}/edit/',
            '/create/',
            f'/posts/{TestPostsUrls.test_post.id}/comment/',
            f'/profile/{TestPostsUrls.test_user}/follow/',
            f'/profile/{TestPostsUrls.test_user}/unfollow/',
        ]

        for address in tests_urls:
            with self.subTest(address=address):
                response = self.get_response_get(
                    self.client,
                    address,
                    follow=True,
                )

                self.assertRedirects(
                    response,
                    reverse('users:login') + f'?next={address}',
                )

    def test_posts_urls_auth_user_user(self):
        """Тестируем пути для авторизированного пользователя.
        Пользователь не являеется автором тестового поста."""
        tests_urls = {
            '/': HTTPStatus.OK,
            f'/group/{TestPostsUrls.test_group.slug}/': HTTPStatus.OK,
            f'/profile/{TestPostsUrls.test_user.username}/': HTTPStatus.OK,
            f'/posts/{TestPostsUrls.test_post.id}/': HTTPStatus.OK,
            '/create/': HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
            '/group/unexisting_group/': HTTPStatus.NOT_FOUND,
            '/profile/unexisting_username/': HTTPStatus.NOT_FOUND,
            '/posts/2000/': HTTPStatus.NOT_FOUND,
            '/posts/2000/edit/': HTTPStatus.NOT_FOUND,
        }

        for address, response_code in tests_urls.items():
            with self.subTest(address=address):
                response = self.get_response_get(
                    self.auth_client_user,
                    address,
                )

                self.assertEqual(
                    response.status_code,
                    response_code,
                    (
                        f'Адрес {address} для авторизированного '
                        f'пользователя работает не верно.'
                        f' Код ответа: {response.status_code}!='
                        f'{response_code}'
                    ),
                )

    def test_posts_redirect_auth_user_user(self):
        """Тестируем редирект для авторизированного пользователя.
        Пользователь не являеется автором тестового поста."""
        address = f'/posts/{TestPostsUrls.test_post.id}/edit/'

        response = self.get_response_get(
            self.auth_client_user,
            address,
            follow=True,
        )

        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': TestPostsUrls.test_post.id},
            )
        )

    def test_posts_redirect_add_comment_auth_user(self):
        """TestComment: Переадресация авторизированного пользователя."""

        response = self.get_response_post(
            client=self.auth_client_user,
            address=f'/posts/{TestPostsUrls.test_post.id}/comment/',
            post_data={'text': 'Test comment'},
            follow=True,
        )

        self.assertRedirects(
            response,
            f'/posts/{TestPostsUrls.test_post.id}/',
        )

    def test_posts_urls_auth_user_author(self):
        """Тестируем путь для автора тестового поста."""
        address = f'/posts/{TestPostsUrls.test_post.id}/edit/'

        response = self.get_response_get(
            self.auth_client_author,
            address,
        )

        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            (
                f'Адрес /posts/{TestPostsUrls.test_post.id}/edit/ '
                'для автора поста работает не верно.'
                f' Код ответа: {response.status_code}!={HTTPStatus.OK}'
            ),
        )

    def test_posts_urls_uses_correct_template(self):
        """Тестируем корректность используемых шаблонов."""
        tests_templates = {
            '/': 'posts/index.html',
            f'/group/{TestPostsUrls.test_group.slug}/':
                'posts/group_list.html',
            f'/profile/{TestPostsUrls.test_author.username}/':
                'posts/profile.html',
            f'/posts/{TestPostsUrls.test_post.id}/':
                'posts/post_detail.html',
            f'/posts/{TestPostsUrls.test_post.id}/edit/':
                'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }

        for address, template in tests_templates.items():
            with self.subTest(address=address):
                response = self.get_response_get(
                    self.auth_client_author,
                    address,
                )

                self.assertTemplateUsed(response, template)
