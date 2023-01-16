import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models.query import QuerySet
from django.test import Client, override_settings
from django.urls import reverse

from posts.models import Comment, Group, Post, User
from posts.tests.utils import YatubeTestBase

TMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TMP_MEDIA_ROOT)
class TestFormsViews(YatubeTestBase):
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

        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

        cls.test_image = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )

        cls.test_post = Post.objects.create(
            text='This is test post',
            author=cls.test_author,
            group=cls.test_group,
            image=cls.test_image,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.__current_posts_id = None
        self.auth_client_author = Client()
        self.auth_client_author.force_login(TestFormsViews.test_author)

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

        test_image = SimpleUploadedFile(
            name='post_create_small.gif',
            content=TestFormsViews.small_gif,
            content_type='image/gif'
        )

        self.__get_current_posts_id()

        self.get_response_post(
            self.auth_client_author,
            address,
            post_data={
                'text': post_text,
                'group': TestFormsViews.test_group.id,
                'image': test_image,
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
            TestFormsViews.test_group,
            (
                'Группа поста не соответствует заданной. '
                f'{TestFormsViews.test_group} != {post.group}'
            ),
        )

        self.assertEqual(
            post.author,
            TestFormsViews.test_author,
            (
                'Группа поста не соответствует заданной. '
                f'{TestFormsViews.test_author} != {post.author}'
            ),
        )

        self.assertIn(
            test_image.name,
            post.image.name,
            (
                'Картинка поста не соответствует заданной. '
                f'{post.image} != {test_image}'
            ),
        )

    def tests_forms_post_edit_dif_text_one_group(self):
        """Редактирование поста. Меняем текст."""
        address = reverse(
            'posts:post_edit',
            kwargs={'post_id': TestFormsViews.test_post.id},
        )
        post_text = TestFormsViews.test_post.text + 'Auto created post'
        post_author = TestFormsViews.test_post.author
        post_group = TestFormsViews.test_post.group

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

        post = Post.objects.get(id=TestFormsViews.test_post.id)
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

        self.assertIn(
            TestFormsViews.test_image.name,
            post.image.name,
            (
                'Картинка поста не соответствует заданной. '
                f'{post.image} != {TestFormsViews.test_image}'
            ),
        )

    def tests_forms_post_edit_one_text_dif_group(self):
        """Редактирование поста. Меняем группу."""
        address = reverse(
            'posts:post_edit',
            kwargs={'post_id': TestFormsViews.test_post.id},
        )
        post_text = TestFormsViews.test_post.text
        post_author = TestFormsViews.test_post.author
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

        post = Post.objects.get(id=TestFormsViews.test_post.id)

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

        self.assertIn(
            TestFormsViews.test_image.name,
            post.image.name,
            (
                'Картинка поста не соответствует заданной. '
                f'{post.image} != {TestFormsViews.test_image}'
            ),
        )

    def tests_forms_post_edit_dif_text_dif_group(self):
        """Редактирование поста. Меняем текст и группу."""
        address = reverse(
            'posts:post_edit',
            kwargs={'post_id': TestFormsViews.test_post.id},
        )
        post_text = TestFormsViews.test_post.text + 'Auto create text'
        post_author = TestFormsViews.test_post.author
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

        post = Post.objects.get(id=TestFormsViews.test_post.id)
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

        self.assertIn(
            TestFormsViews.test_image.name,
            post.image.name,
            (
                'Картинка поста не соответствует заданной. '
                f'{post.image} != {TestFormsViews.test_image}'
            ),
        )

    def test_forms_post_edit_image(self):
        """Проверка изменения картинки в посте."""
        address = reverse(
            'posts:post_edit',
            kwargs={'post_id': TestFormsViews.test_post.id},
        )
        post_text = TestFormsViews.test_post.text
        post_author = TestFormsViews.test_post.author
        post_group = TestFormsViews.test_post.group
        test_image = SimpleUploadedFile(
            name='post_change_small.gif',
            content=TestFormsViews.small_gif,
            content_type='image/gif'
        )

        self.__get_current_posts_id()

        self.get_response_post(
            self.auth_client_author,
            address,
            post_data={
                'text': post_text,
                'group': post_group.id,
                'image': test_image,
            },
        )

        create_post_id = self.__get_new_posts_id()

        self.assertEqual(
            len(create_post_id),
            0,
            'Вместо редактирования создан пост',
        )

        post = Post.objects.get(id=TestFormsViews.test_post.id)
        self.assertEqual(
            post.text,
            post_text,
            f'Текст поста изменен. {post.text} != {post_text}',
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

        self.assertIn(
            test_image.name,
            post.image.name,
            (
                'Картинка поста не изменилась. '
                f'{post.image} = {test_image}'
            ),
        )

    def test_posts_views_add_comment(self):
        """TestComment: Добавление комментария к посту."""
        address_add_comment = reverse(
            'posts:add_comment',
            kwargs={'post_id': TestFormsViews.test_post.id},
        )

        address_post_detail = reverse(
            'posts:post_detail',
            kwargs={'post_id': TestFormsViews.test_post.id},
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

        comments = self.get_field_from_context_by_type(
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
                post=TestFormsViews.test_post,
                author=TestFormsViews.test_author,
                text='Test comment',
            ).exists(),
            'Комментарий не создан'
        )
