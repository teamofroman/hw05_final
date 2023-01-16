"""Тесты для проверки тестирования процедур формирования
и отображения данных."""
from django.core.cache import cache
from django.core.paginator import Page
from django.db.models import Count
from django.db.models.query import QuerySet
from django.test import Client
from django.urls import reverse

from posts.forms import CommentForm, PostForm
from posts.models import Comment, Group, Post, User
from posts.tests.utils import YatubeTestBase


class TestPostsViews(YatubeTestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.test_group = Group.objects.create(
            title='Test group',
            slug='test_group',
            description='This is test group',
        )

        # cls.test_user = User.objects.create_user(
        #     username='testuser',
        # )

        cls.test_author = User.objects.create_user(
            username='testauthor',
        )

        cls.test_post = Post.objects.create(
            text='Test post',
            author=cls.test_author,
            group=cls.test_group,
        )

    def setUp(self):
        self.auth_client_author = Client()
        self.auth_client_author.force_login(TestPostsViews.test_author)
        cache.clear()

    def __check_post_content(self, context, valid_post, page_address):
        page_obj = self.get_field_from_context(context, Page)
        self.assertIsNotNone(
            page_obj,
            f'На странице `{page_address}` не найден объект типа Page'
        )

        self.assertGreater(
            len(page_obj),
            0,
            (
                f'Количество объектов на странице `{page_address}` не верное. '
                f'{len(page_obj)} > 0',
            ),
        )

        self.assertEqual(
            page_obj[0].text,
            valid_post.text,
            (
                f'Содержание первого поста на странице `{page_address}` не '
                f'соответствует значению в БД'
            ),
        )

        self.assertEqual(
            page_obj[0].author,
            valid_post.author,
            (
                f'Автор первого поста на странице `{page_address}` не '
                'соответствует значению в БД'
            ),
        )
        self.assertEqual(
            page_obj[0].group,
            valid_post.group,
            (
                f'Группа первого поста на странице `{page_address}` не '
                'соответствует значению в БД'
            ),
        )

    def test_posts_views_uses_correct_template(self):
        """Проверяем корректность используемых шаблонов."""
        tests_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={
                    'slug': TestPostsViews.test_group.slug,
                },
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={
                    'username': TestPostsViews.test_author.username,
                },
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={
                    'post_id': TestPostsViews.test_post.id,
                },
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={
                    'post_id': TestPostsViews.test_post.id,
                },
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }

        for address, template in tests_templates.items():
            with self.subTest(address=address):
                response = self.get_response_get(
                    self.auth_client_author,
                    address,
                )

                self.assertTemplateUsed(response, template)

    def test_posts_views_index_context(self):
        """Проверяем контекст головной страницы."""
        address = reverse('posts:index')
        response = self.get_response_get(
            self.auth_client_author,
            address,
        )

        self.__check_post_content(
            response.context,
            TestPostsViews.test_post,
            address,
        )

    def test_posts_views_group_context(self):
        """Проверяем контекст страницы группы."""
        address = reverse(
            'posts:group_list', kwargs={'slug': TestPostsViews.test_group.slug}
        )
        response = self.get_response_get(
            self.auth_client_author,
            address,
        )

        group = self.get_field_from_context(response.context, Group)
        self.assertIsNotNone(
            group,
            f'На странице `{address}` не найден объект типа Group'
        )
        self.assertEqual(
            group,
            TestPostsViews.test_group,
            f'Группа на странице {address} не соответствует запрошенной',
        )

        self.__check_post_content(
            response.context,
            TestPostsViews.test_post,
            address,
        )

    def test_posts_views_profile_context(self):
        """Проверяем контекст страницы профайла."""
        address = reverse(
            'posts:profile',
            kwargs={'username': TestPostsViews.test_author.username},
        )
        response = self.get_response_get(
            self.auth_client_author,
            address,
        )

        author = self.get_field_from_context(response.context, User)
        self.assertIsNotNone(
            author,
            f'На странице `{address}` не найден объект типа User'
        )
        self.assertEqual(
            author,
            TestPostsViews.test_author,
            f'Группа на странице {address} не соответствует запрошенной',
        )

        self.__check_post_content(
            response.context,
            TestPostsViews.test_post,
            address,
        )

    def test_posts_views_post_detail_context(self):
        """Проверяем контекст страницы post_detail"""
        address = reverse(
            'posts:post_detail',
            kwargs={'post_id': TestPostsViews.test_post.id},
        )

        test_comment = Comment.objects.create(
            text='Test comment',
            author=TestPostsViews.test_author,
            post=TestPostsViews.test_post,
        )

        response = self.get_response_get(
            self.auth_client_author,
            address,
        )

        post = self.get_field_from_context(response.context, Post)
        self.assertIsNotNone(
            post,
            f'На странице `{address}` не найден объект типа Post',
        )

        self.assertEqual(
            post,
            TestPostsViews.test_post,
            (
                f'Данные поста на странице `{address}` не соответствуют '
                'данным поста в БД'
            ),
        )

        comment_form = self.get_field_from_context(
            response.context,
            CommentForm
        )

        self.assertIsNotNone(
            comment_form,
            f'На странице {address} не найдена форма комментария'
        )

        comments = self.get_field_from_context(
            response.context,
            QuerySet,
        )

        self.assertEqual(
            len(comments),
            1,
            f'Количество комментариев на странице '
            f'{address} не соответствует созданным'
        )

        self.assertIsInstance(
            comments[0],
            Comment,
            f'Комментарии на странице {address} '
            f'имеют тип отличный от Comment'
        )

        self.assertEqual(
            comments[0],
            test_comment,
            f'Содержимое комментария на странице '
            f'{address} не соответствует созданному'
        )

    def test_posts_views_post_create_context(self):
        """Проверяем контекст страницы post_create"""
        address = reverse('posts:post_create')

        response = self.get_response_get(
            self.auth_client_author,
            address,
        )

        form = self.get_field_from_context(response.context, PostForm)
        self.assertIsNotNone(
            form,
            f'На странице `{address}` не найден объект типа PostForm',
        )

    def test_posts_views_post_edit_context(self):
        """Проверяем контекст страницы post_edit"""
        address = reverse(
            'posts:post_edit',
            kwargs={'post_id': TestPostsViews.test_post.id},
        )

        response = self.get_response_get(
            self.auth_client_author,
            address,
        )

        form = self.get_field_from_context(response.context, PostForm)
        self.assertIsNotNone(
            form,
            f'На странице `{address}` не найден объект типа PostForm',
        )

    def tests_posts_views_new_post_create(self):
        """Проверка создания нового поста"""

        group = Group.objects.create(
            title='Test group 2',
            slug='test_group_2',
            description='This is test group 2',
        )

        new_post = Post.objects.create(
            text='Auto created post',
            author=TestPostsViews.test_author,
            group=group,
        )

        old_posts_count = Post.objects.filter(
            group=TestPostsViews.test_group
        ).aggregate(Count('id'))['id__count']

        self.assertEqual(
            old_posts_count,
            1,
            (
                f'Пост создан не в той группе.'
                f' {group.slug}!={TestPostsViews.test_group.slug}'
            ),
        )

        test_pages = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': group.slug}),
            reverse(
                'posts:profile',
                kwargs={'username': TestPostsViews.test_author.username},
            ),
        ]

        for address in test_pages:
            with self.subTest(address=address):
                response = self.get_response_get(
                    self.auth_client_author,
                    address,
                )

                page_obj = self.get_field_from_context(response.context, Page)
                self.assertIsNotNone(
                    page_obj,
                    f'На странице `{address}` не найден объект типа Page',
                )

                self.assertEqual(
                    page_obj[0],
                    new_post,
                    (
                        f'Содержание первого поста на странице `{address}`'
                        ' не соответствует созданному посту'
                    ),
                )

    def test_posts_views_add_comment(self):
        """TestComment: Добавление комментария к посту."""
        address_add_comment = reverse(
            'posts:add_comment',
            kwargs={'post_id': TestPostsViews.test_post.id},
        )

        address_post_detail = reverse(
            'posts:post_detail',
            kwargs={'post_id': TestPostsViews.test_post.id},
        )

        self.get_response_post(
            client=self.auth_client_author,
            address=address_add_comment,
            post_data={'text': 'Test comment'},
            follow=True,
        )

        response = self.get_response_get(
            client=self.auth_client_author,
            address=address_post_detail,
        )

        comments = self.get_field_from_context(
            response.context,
            QuerySet,
        )

        self.assertEqual(
            len(comments),
            1,
            f'Количество комментариев на странице '
            f'{address_post_detail} не соответствует созданным'
        )

        self.assertIsInstance(
            comments[0],
            Comment,
            f'Комментарии на странице {address_post_detail} '
            f'имеют тип отличный от Comment'
        )

        self.assertTrue(
            Comment.objects.filter(
                post=TestPostsViews.test_post,
                author=TestPostsViews.test_author,
                text='Test comment',
            ).exists(),
            'Комментарий не создан'
        )
