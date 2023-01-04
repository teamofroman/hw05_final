from django.urls import reverse

from posts.models import User
from posts.tests.utils import YatubeTestBase


class TestUserForms(YatubeTestBase):
    def test_users_forms_signup(self):
        address = reverse('users:signup')
        form_data = {
            'first_name': '1',
            'last_name': '2',
            'username': 'testuser',
            'email': 'new@test.ru',
            'password1': 'Qsefthuko@',
            'password2': 'Qsefthuko@',
        }

        response = self.get_response_post(self.client, address, form_data)

        self.assertRedirects(response, reverse('posts:index'))

        new_user = User.objects.filter(username='testuser')
        self.assertGreater(
            len(new_user),
            0,
            'Пользователь не создан'
        )
