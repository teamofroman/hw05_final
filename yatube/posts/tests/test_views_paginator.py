"""Тесты для проверки тестирования процедур формирования
и отображения данных."""
from django.core.cache import cache
from django.core.paginator import Page
from django.test import Client
from django.urls import reverse

from posts.constants import MAX_POSTS_ON_PAGE
from posts.models import Group, Post, User
from posts.tests.utils import YatubeTestBase

POSTS_ON_LAST_PAGE = 2


class TestPostsViewsPaginator(YatubeTestBase):
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

        objs = [Post(
            text=f'Test post #{i + 100}',
            author=cls.test_author,
            group=cls.test_group,
        ) for i in range(MAX_POSTS_ON_PAGE + POSTS_ON_LAST_PAGE)]

        Post.objects.bulk_create(objs)

    def setUp(self):
        self.auth_client_author = Client()
        self.auth_client_author.force_login(
            TestPostsViewsPaginator.test_author)
        cache.clear()

    def __check_paginator_context(self, context, post_count, address):
        page_obj = self.get_field_from_context_by_type(context, Page)
        self.assertIsNotNone(
            page_obj,
            f'На странице `{address}` не найден объект типа Page',
        )

        self.assertEqual(
            len(page_obj),
            post_count,
            f'Количество объектов на странице `{address}` не верное. '
            f'{len(page_obj)} != {post_count}',
        )

    def test_posts_views_paginator(self):
        test_address = {
            reverse('posts:index'): MAX_POSTS_ON_PAGE,
            reverse('posts:index') + '?page=2': POSTS_ON_LAST_PAGE,
            reverse(
                'posts:group_list',
                kwargs={'slug': TestPostsViewsPaginator.test_group.slug},
            ): MAX_POSTS_ON_PAGE,
            reverse(
                'posts:group_list',
                kwargs={'slug': TestPostsViewsPaginator.test_group.slug},
            )
            + '?page=2': POSTS_ON_LAST_PAGE,
            reverse(
                'posts:profile',
                kwargs={
                    'username': TestPostsViewsPaginator.test_author.username,
                },
            ): MAX_POSTS_ON_PAGE,
            reverse(
                'posts:profile',
                kwargs={
                    'username': TestPostsViewsPaginator.test_author.username,
                },
            )
            + '?page=2': POSTS_ON_LAST_PAGE,
        }

        for address, obj_count in test_address.items():
            with self.subTest(address=address):
                response = self.get_response_get(
                    self.auth_client_author,
                    address,
                )

                self.__check_paginator_context(
                    response.context,
                    obj_count,
                    address,
                )
