from django.test import Client
from django.urls import reverse

from posts.models import User
from posts.tests.utils import YatubeTestBase


class TestUsersViewsAdditional(YatubeTestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create_user(
            username='testuser',
        )

    def setUp(self):
        self.auth_client_user = Client()
        self.auth_client_user.force_login(TestUsersViewsAdditional.test_user)

    def test_users_views_uses_correct_template(self):
        tests_templates = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
            reverse('users:password_reset'): 'users/password_reset_form.html',
            reverse(
                'users:password_reset_done'
            ): 'users/password_reset_done.html',
            # '/auth/reset/qq/66o-088d5ec67a3a5f99a30f/'
            reverse(
                'users:password_reset_confirm',
                kwargs={
                    'uidb64': 'qq',
                    'token': '66o-088d5ec67a3a5f99a30f',
                },
            ): 'users/password_reset_confirm.html',
            reverse(
                'users:password_reset_complete'
            ): 'users/password_reset_complete.html',
            reverse(
                'users:password_change'
            ): 'users/password_change_form.html',
            reverse(
                'users:password_change_done'
            ): 'users/password_change_done.html',
            reverse('users:logout'): 'users/logout.html',
        }

        for address, template in tests_templates.items():
            with self.subTest(address=address):
                response = self.get_response_get(
                    self.auth_client_user,
                    address,
                )

                self.assertTemplateUsed(response, template)
