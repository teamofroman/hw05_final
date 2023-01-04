from django.test import Client
from django.urls import reverse

from posts.models import Group, Post, User
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

        cls.test_author = User.objects.create_user(
            username='testauthor',
        )

        cls.test_post = Post.objects.create(
            text='This is test post',
            author=cls.test_author,
            group=cls.test_group,
        )

    def setUp(self):
        self.__current_posts_id = None
        self.auth_client_author = Client()
        self.auth_client_author.force_login(TestPostsViews.test_author)

    def __get_current_posts_id(self):
        self.__current_posts_id = set([post.id for post in Post.objects.all()])

    def __get_new_posts_id(self):
        if self.__current_posts_id is None:
            raise ValueError(
                'Получение новых постов выполнено без получения текущих'
            )
        return set(
            [post.id for post in Post.objects.all()]
        ) - self.__current_posts_id

    def tests_forms_post_create(self):
        """Проверка создания нового поста"""
        address = reverse('posts:post_create')
        post_text = 'Auto created post'

        self.__get_current_posts_id()
        self.get_response_post(
            self.auth_client_author,
            address,
            post_data={
                'text': post_text,
                'group': TestPostsViews.test_group.id,
            },
        )

        create_post_id = self.__get_new_posts_id()

        self.assertEqual(
            len(create_post_id),
            1,
            'Пост не создан или создано несколько постов',
        )

        post = Post.objects.get(id=create_post_id.pop())
        self.assertEqual(
            post.text,
            post_text,
            (
                'Текст поста не соответствует заданному. '
                f'{post_text} != {post.text}'
            ),
        )

        self.assertEqual(
            post.group,
            TestPostsViews.test_group,
            (
                'Группа поста не соответствует заданной. '
                f'{TestPostsViews.test_group} != {post.group}'
            ),
        )

        self.assertEqual(
            post.author,
            TestPostsViews.test_author,
            (
                'Группа поста не соответствует заданной. '
                f'{TestPostsViews.test_author} != {post.author}'
            ),
        )

    def tests_forms_post_edit_dif_text_one_group(self):
        """Редактирование поста. Меняем текст."""
        address = reverse(
            'posts:post_edit',
            kwargs={'post_id': TestPostsViews.test_post.id},
        )
        post_text = TestPostsViews.test_post.text + 'Auto created post'
        post_author = TestPostsViews.test_post.author
        post_group = TestPostsViews.test_post.group

        self.__get_current_posts_id()
        self.get_response_post(
            self.auth_client_author,
            address,
            post_data={
                'text': post_text,
                'group': post_group.id,
            },
        )

        create_post_id = self.__get_new_posts_id()

        self.assertEqual(
            len(create_post_id),
            0,
            'Вместо редактирования создан пост',
        )

        post = Post.objects.get(id=TestPostsViews.test_post.id)
        self.assertEqual(
            post.text,
            post_text,
            f'Текст поста не изменен. {post.text} != {post_text}',
        )
        self.assertEqual(
            post.group,
            post_group,
            f'Изменилась группа поста. {post.group} != {post_group}',
        )
        self.assertEqual(
            post.author,
            post_author,
            f'Изменился автор поста. {post.author} != {post_author}',
        )

    def tests_forms_post_edit_one_text_dif_group(self):
        """Редактирование поста. Меняем группу."""
        address = reverse(
            'posts:post_edit',
            kwargs={'post_id': TestPostsViews.test_post.id},
        )
        post_text = TestPostsViews.test_post.text
        post_author = TestPostsViews.test_post.author
        post_group = Group.objects.create(
            title='Test group 2',
            slug='test_group_2',
            description='This is test group 2',
        )

        self.__get_current_posts_id()
        self.get_response_post(
            self.auth_client_author,
            address,
            post_data={
                'text': post_text,
                'group': post_group.id,
            },
        )

        create_post_id = self.__get_new_posts_id()

        self.assertEqual(
            len(create_post_id),
            0,
            'Вместо редактирования создан пост',
        )

        post = Post.objects.get(id=TestPostsViews.test_post.id)

        self.assertEqual(
            post.text,
            post_text,
            f'Текст поста изменен. {post.text} != {post_text}',
        )

        self.assertEqual(
            post.group,
            post_group,
            f'Группа поста не изменена. {post.group} != {post_group}',
        )

        self.assertEqual(
            post.author,
            post_author,
            f'Изменился автор поста. {post.author} != {post_author}',
        )

    def tests_forms_post_edit_dif_text_dif_group(self):
        """Редактирование поста. Меняем текст и группу."""
        address = reverse(
            'posts:post_edit',
            kwargs={'post_id': TestPostsViews.test_post.id},
        )
        post_text = TestPostsViews.test_post.text + 'Auto create text'
        post_author = TestPostsViews.test_post.author
        post_group = Group.objects.create(
            title='Test group 2',
            slug='test_group_2',
            description='This is test group 2',
        )

        self.__get_current_posts_id()

        self.get_response_post(
            self.auth_client_author,
            address,
            post_data={
                'text': post_text,
                'group': post_group.id,
            },
        )

        create_post_id = self.__get_new_posts_id()

        self.assertEqual(
            len(create_post_id),
            0,
            'Вместо редактирования создан пост',
        )

        post = Post.objects.get(id=TestPostsViews.test_post.id)
        self.assertEqual(
            post.text,
            post_text,
            f'Текст поста не изменен. {post.text} != {post_text}',
        )

        self.assertEqual(
            post.group,
            post_group,
            f'Группа поста не изменена. {post.group} != {post_group}',
        )

        self.assertEqual(
            post.author,
            post_author,
            f'Изменился автор поста. {post.author} != {post_author}',
        )
