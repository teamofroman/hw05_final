"""Тесты для проверки тестирования моделей данных."""
from posts.constants import MAX_PRESENTATION_LENGTH
from posts.models import Group, Post, User
from posts.tests.utils import YatubeTestBase


class TestModels(YatubeTestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_group = Group.objects.create(
            title='Test group',
            slug='test_group',
            description='This is test group',
        )
        cls.test_author = User.objects.create_user(
            username='testuser',
        )
        cls.test_post = Post.objects.create(
            text='This is test post text ' * 3,
            author=cls.test_author,
            group=cls.test_group,
        )
        cls.test_post_short_text = Post.objects.create(
            text='Test post',
            author=cls.test_author,
            group=cls.test_group,
        )

    def test_models_post_verbose_name(self):
        """Проверяем verbose_name для модели Post"""
        field_verbose = {
            'text': 'Текст публикации',
            'pub_date': 'Дата публикации',
            'author': 'Автор публикации',
            'group': 'Сообщество',
        }

        for field, expected_value in field_verbose.items():
            with self.subTest(field=field):
                self.assertEqual(
                    TestModels.test_post._meta.get_field(field).verbose_name,
                    expected_value,
                )

    def test_models_post_help_text(self):
        """Проверяем help_text для модели Post"""
        field_help_text = {
            'text': 'Введите текст публикации.',
            'pub_date': 'Введите дату публикации.',
            'author': 'Укажите автора публикации',
            'group': 'Укажите сообщество, в котором разместить публикацию',
        }

        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    TestModels.test_post._meta.get_field(field).help_text,
                    expected_value,
                )

    def test_models_group_verbose_name(self):
        """Проверяем verbose_name для модели Group"""
        field_verbose = {
            'title': 'Название сообщества',
            'slug': 'Сетевой адрес',
            'description': 'Описание сообщества',
        }

        for field, expected_value in field_verbose.items():
            with self.subTest(field=field):
                self.assertEqual(
                    TestModels.test_group._meta.get_field(field).verbose_name,
                    expected_value,
                )

    def test_models_group_help_text(self):
        """Проверяем help_text для модели Group"""
        field_help_text = {
            'title': 'Введите название сообщества. Максимум 100 символов.',
            'slug': (
                'Введите адрес сообщества. Допускаются английские буквы, '
                'цифры, символ подчеркивания.'
            ),
            'description': 'Введите описание сообщества.',
        }

        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    TestModels.test_group._meta.get_field(field).help_text,
                    expected_value,
                )

    def test_models_post_str_long_text(self):
        """Проверяем метод __str__ для длинного текста для модели Post"""
        self.assertEqual(
            str(TestModels.test_post),
            TestModels.test_post.text[:MAX_PRESENTATION_LENGTH] + '...',
            'Проверьте работу метода __str__ модели Post.',
        )

    def test_models_post_str_short_text(self):
        """Проверяем метод __str__ для короткого текста для модели Post"""
        self.assertEqual(
            str(TestModels.test_post_short_text),
            'Test post',
            'Проверьте работу метода __str__ модели Post.',
        )

    def test_models_group_str(self):
        """Проверяем метод __str__ для модели Group"""
        self.assertEqual(
            str(TestModels.test_group),
            TestModels.test_group.title,
            'Проверьте работу метода __str__ модели Group.',
        )
