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

        # objs = [Post(
        #     text=f'Test author post #{i}',
        #     author=cls.test_author,
        # ) for i in range(3)]
        #
        # cls.test_user_posts = Post.objects.bulk_create(objs)
        #
        # objs = [Post(
        #     text=f'Test user post #{i}',
        #     author=cls.test_user,
        # ) for i in range(3)]
        #
        # cls.test_author_posts = Post.objects.bulk_create(objs)

    def setUp(self):
        self.user_client = Client()
        self.user_client.force_login(TestFollow.test_user)

        self.author_client = Client()
        self.author_client.force_login(TestFollow.test_author)

    def test_follow_redirect_unauth_user(self):
        """TestFollow: Перенаправление не авторизированного пользователя."""
        address = reverse(
            'posts:profile_follow',
            kwargs={'username': TestFollow.test_user},
        )

        response = self.get_response_post(
            client=self.client,
            address=address,
            post_data={'text': 'Test comment'},
            follow=True,
        )

        self.assertRedirects(
            response,
            reverse(
                'users:login') + f'?next={address}',
        )

    def test_follow_follow_to_author(self):
        """TestFolow: Следить за автором."""
        follow_count = Follow.objects.filter(user=TestFollow.test_user).count()
        address = reverse(
            'posts:profile_follow',
            kwargs={'username': TestFollow.test_author},
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

    def test_follow_unfollow_author(self):
        """TestFollow: Не следить за автором."""
        self.test_follow_follow_to_author()
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

    def test_follow_new_post(self):
        """TestFollow: Новая запись появляется в ленте подписантов."""
        self.test_follow_follow_to_author()
        address = reverse('posts:follow_index')
        new_post = Post.objects.create(
            text='Test post',
            author=TestFollow.test_author,
        )

        response = self.get_response_get(
            self.user_client,
            address,
        )

        page_obj = self.get_field_from_context(response.context, Page)
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

        response = self.get_response_get(
            self.author_client,
            address,
        )

        page_obj = self.get_field_from_context(response.context, Page)
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