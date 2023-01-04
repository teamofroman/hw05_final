from django.test import Client

from posts.models import User
from posts.tests.utils import YatubeTestBase


class TestStaticPages(YatubeTestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create_user(
            username='testuser',
        )

    def setUp(self):
        self.auth_client_user = Client()
        self.auth_client_user.force_login(TestStaticPages.test_user)

    def test_static_pages_urls_unauth_user(self):
        """Тестируем пути статических страниц для не авторизированного
        пользователя."""
        tests_urls = {
            '/about/author/': 200,
            '/about/tech/': 200,
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
                        f'Адрес {address} для не авторизированного '
                        f'пользователя работает не верно.'
                        f' Код ответа: {response.status_code}!='
                        f'{response_code}'
                    ),
                )

    def test_static_pages_urls_auth_user(self):
        """Тестируем пути статических страниц для авторизированного
        пользователя."""
        tests_urls = {
            '/about/author/': 200,
            '/about/tech/': 200,
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

    def test_static_pages_uses_correct_template(self):
        """Тестируем корректность используемых шаблонов."""
        tests_templates = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/technology.html',
        }

        for address, template in tests_templates.items():
            with self.subTest(address=address):
                response = self.get_response_get(
                    self.auth_client_user,
                    address,
                )

                self.assertTemplateUsed(response, template)
