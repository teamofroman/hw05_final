import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, override_settings
from django.urls import reverse

from posts.models import Group, User
from posts.tests.utils import YatubeTestBase

TMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TMP_MEDIA_ROOT)
class TestImage(YatubeTestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create(username='testuser')

        cls.test_group = Group.objects.create(
            title='Test group',
            slug='testgroup',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(TestImage.test_user)

    def test_image_create_post_with_image(self):
        """TestImage: Создание поста с картинкой."""
        address = reverse('posts:post_create')
        post_text = 'Auto created post with image'
        post_on_group_count = TestImage.test_group.posts.count()

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        self.get_response_post(
            self.auth_client,
            address,
            post_data={
                'text': post_text,
                'group': TestImage.test_group.id,
                'image': uploaded,
            },
            follow=True,
        )

        self.assertEqual(
            TestImage.test_group.posts.count(),
            post_on_group_count + 1,
            'Ошибка создания поста',
        )
