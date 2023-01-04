from http import HTTPStatus

from django.test import Client

from posts.models import User
from posts.tests.utils import YatubeTestBase


class TestUsersUrls(YatubeTestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create_user(
            username='testuser',
        )

    def setUp(self):
        self.auth_client_user = Client()
        self.auth_client_user.force_login(TestUsersUrls.test_user)

    def test_users_urls_unauth_user(self):
        """Тестирование путей для не авторизированного пользователя."""
        tests_urls = {
            '/auth/signup/': HTTPStatus.OK,
            '/auth/login/': HTTPStatus.OK,
            '/auth/password_reset/': HTTPStatus.OK,
            '/auth/password_reset/done/': HTTPStatus.OK,
            '/auth/reset/qq/66o-088d5ec67a3a5f99a30f/': HTTPStatus.OK,
            '/auth/reset/done/': HTTPStatus.OK,
            '/auth/logout/': HTTPStatus.OK,
        }

        for address, response_code in tests_urls.items():
            with self.subTest(address=address):
                response = self.get_response_get(self.client, address)
                self.assertEqual(
                    response.status_code,
                    response_code,
                    (
                        f'Адрес {address} для не авторизированного '
                        f'пользователя работает не верно.'
                        f' Код ответа: {response.status_code}!='
                        f'{response_code}'
                    ),
                )

    def test_users_redirect_unauth_user(self):
        """Тестируем редирект для не авторизированного пользователя."""
        tests_urls = [
            '/auth/password_change/',
            '/auth/password_change/done/',
        ]

        for address in tests_urls:
            with self.subTest(address=address):
                response = self.get_response_get(
                    self.client,
                    address,
                    follow=True,
                )
                self.assertRedirects(response, f'/auth/login/?next={address}')

    def test_users_urls_auth_user(self):
        """Тестирование путей для авторизированного пользователя."""
        tests_urls = {
            '/auth/signup/': HTTPStatus.OK,
            '/auth/login/': HTTPStatus.OK,
            '/auth/password_reset/': HTTPStatus.OK,
            '/auth/password_reset/done/': HTTPStatus.OK,
            '/auth/reset/qq/66o-088d5ec67a3a5f99a30f/': HTTPStatus.OK,
            '/auth/reset/done/': HTTPStatus.OK,
            '/auth/password_change/': HTTPStatus.OK,
            '/auth/password_change/done/': HTTPStatus.OK,
            '/auth/logout/': HTTPStatus.OK,
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
