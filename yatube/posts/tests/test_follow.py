from django.core.paginator import Page
from django.test import Client
from django.urls import reverse

from posts.models import Follow, Post, User
from posts.tests.utils import YatubeTestBase


class TestFollow(YatubeTestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create(username='test_user')
        cls.test_author = User.objects.create(username='test_author')

    def setUp(self):
        self.user_client = Client()
        self.user_client.force_login(TestFollow.test_user)

        self.author_client = Client()
        self.author_client.force_login(TestFollow.test_author)

    def test_follow_follow_to_author(self):
        """TestFolow: Следить за автором."""
        follow_count = Follow.objects.filter(user=TestFollow.test_user).count()
        address = reverse(
            'posts:profile_follow',
            kwargs={'username': TestFollow.test_author},
        )

        self.assertFalse(
            Follow.objects.filter(
                user=TestFollow.test_user,
                author=TestFollow.test_author,
            ).exists(),
            'Подписка на автора уже есть в базе',
        )

        self.get_response_get(
            self.user_client,
            address
        )

        self.assertEqual(
            Follow.objects.filter(user=TestFollow.test_user).count(),
            follow_count + 1,
            'Не удалось подписаться на автора',
        )

        self.assertTrue(
            Follow.objects.filter(
                user=TestFollow.test_user,
                author=TestFollow.test_author,
            ).exists(),
            'Подписка на автора отсутствует в базе',
        )

    def test_follow_unfollow_author(self):
        """TestFollow: Не следить за автором."""
        Follow.objects.create(
            user=TestFollow.test_user,
            author=TestFollow.test_author,
        )

        follow_count = Follow.objects.filter(user=TestFollow.test_user).count()
        address = reverse(
            'posts:profile_unfollow',
            kwargs={'username': TestFollow.test_author},
        )

        self.get_response_get(
            self.user_client,
            address
        )

        self.assertEqual(
            Follow.objects.filter(user=TestFollow.test_user).count(),
            follow_count - 1,
            'Не удалось отписаться от автора'
        )

        self.assertFalse(
            Follow.objects.filter(
                user=TestFollow.test_user,
                author=TestFollow.test_author,
            ).exists(),
            'Подписка на автора присутствует в базе',
        )

    def test_follow_follow_self(self):
        """TestFollow: Слежка за самим собой."""
        follow_count = Follow.objects.filter(user=TestFollow.test_user).count()
        address = reverse(
            'posts:profile_follow',
            kwargs={'username': TestFollow.test_user},
        )

        self.get_response_get(
            self.user_client,
            address
        )

        self.assertEqual(
            Follow.objects.filter(user=TestFollow.test_user).count(),
            follow_count,
            'Подписались на самого себя',
        )

    def test_follow_new_post_on_follow_user(self):
        """TestFollow: Новая запись появляется в ленте подписантов."""
        Follow.objects.create(
            user=TestFollow.test_user,
            author=TestFollow.test_author,
        )

        address = reverse('posts:follow_index')
        new_post = Post.objects.create(
            text='Test post',
            author=TestFollow.test_author,
        )

        response = self.get_response_get(
            self.user_client,
            address,
        )

        page_obj = self.get_field_from_context_by_type(response.context, Page)
        self.assertIsNotNone(
            page_obj,
            f'На странице {address} для {TestFollow.test_user} '
            'не найден список постов',
        )

        self.assertEqual(
            len(page_obj),
            1,
            f'На странице {address} для {TestFollow.test_user} '
            'больше одного поста',
        )

        self.assertEqual(
            page_obj[0],
            new_post,
            f'Пост на странице {address} для {TestFollow.test_user} '
            'не соответствует созданному',
        )

    def test_follow_new_post_on_unfollow_user(self):
        """TestFollow: Новой записи нет в ленте неподписанного пользователя."""

        Follow.objects.create(
            user=TestFollow.test_user,
            author=TestFollow.test_author,
        )

        address = reverse('posts:follow_index')
        Post.objects.create(
            text='Test post',
            author=TestFollow.test_author,
        )

        response = self.get_response_get(
            self.author_client,
            address,
        )

        page_obj = self.get_field_from_context_by_type(response.context, Page)
        self.assertIsNotNone(
            page_obj,
            f'На странице {address} для {TestFollow.test_author} '
            'не найден список постов',
        )

        self.assertEqual(
            len(page_obj),
            0,
            f'На странице {address} для {TestFollow.test_author} '
            'присутствуют посты',
        )
