from django.db.models.query import QuerySet
from django.test import Client
from django.urls import reverse

from posts.forms import CommentForm
from posts.models import Comment, Group, Post, User
from posts.tests.utils import YatubeTestBase


class TestComment(YatubeTestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create(username='test_user')
        cls.test_group = Group.objects.create(
            title='Test group',
            slug='test_group',
        )
        cls.test_post = Post.objects.create(
            text='Test post',
            author=cls.test_user,
            group=cls.test_group,
        )
        cls.address_add_comment = reverse(
            'posts:add_comment',
            kwargs={'post_id': cls.test_post.id},
        )
        cls.address_post_detail = reverse(
            'posts:post_detail',
            kwargs={'post_id': cls.test_post.id},
        )

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(TestComment.test_user)

    def test_comment_redirect_unauth_user(self):
        """TestComment: Переадресация не авторизированного пользователя."""
        response = self.get_response_post(
            client=self.client,
            address=TestComment.address_add_comment,
            post_data={'text': 'Test comment'},
            follow=True,
        )

        self.assertRedirects(
            response,
            reverse(
                'users:login') + f'?next={TestComment.address_add_comment}',
        )

    def test_comment_redirect_auth_user(self):
        """TestComment: Переадресация авторизированного пользователя."""
        response = self.get_response_post(
            client=self.auth_client,
            address=TestComment.address_add_comment,
            post_data={'text': 'Test comment'},
            follow=True,
        )

        self.assertRedirects(
            response,
            TestComment.address_post_detail,
        )

    def test_comment_form_in_context(self):
        """TestComment: Наличие на странице формы комментария."""
        response = self.get_response_get(
            client=self.auth_client,
            address=TestComment.address_post_detail,
        )

        comment_form = self.get_field_from_context(
            response.context,
            CommentForm
        )

        self.assertIsNotNone(
            comment_form,
            f'На странице {TestComment.address_post_detail} не найдена форма '
            f'комментария'
        )

    def test_comment_comments_in_context(self):
        """TestComment: Наличие блока комментариев в контексте страницы."""
        test_comment = Comment.objects.create(
            text='Test comment',
            author=TestComment.test_user,
            post=TestComment.test_post,
        )

        response = self.get_response_get(
            client=self.auth_client,
            address=TestComment.address_post_detail,
        )

        comments = self.get_field_from_context(
            response.context,
            QuerySet,
        )

        self.assertEqual(
            len(comments),
            1,
            f'Количество комментариев на странице '
            f'{TestComment.address_post_detail} не соответствует созданным'
        )

        self.assertIsInstance(
            comments[0],
            Comment,
            f'Комментарии на странице {TestComment.address_post_detail} '
            f'имеют тип отличный от Comment'
        )

        self.assertEqual(
            comments[0],
            test_comment,
            f'Содержимое комментария на странице '
            f'{TestComment.address_post_detail} не соответствует созданному'
        )

    def test_comment_add_comment(self):
        """TestComment: Добавление комментария к посту."""
        self.get_response_post(
            client=self.auth_client,
            address=TestComment.address_add_comment,
            post_data={'text': 'Test comment'},
            follow=True,
        )

        response = self.get_response_get(
            client=self.auth_client,
            address=TestComment.address_post_detail,
        )

        comments = self.get_field_from_context(
            response.context,
            QuerySet,
        )

        self.assertEqual(
            len(comments),
            1,
            f'Количество комментариев на странице '
            f'{TestComment.address_post_detail} не соответствует созданным'
        )

        self.assertIsInstance(
            comments[0],
            Comment,
            f'Комментарии на странице {TestComment.address_post_detail} '
            f'имеют тип отличный от Comment'
        )

        self.assertTrue(
            Comment.objects.filter(
                post=TestComment.test_post,
                author=TestComment.test_user,
                text='Test comment',
            ).exists(),
            'Пост не создан'
        )
