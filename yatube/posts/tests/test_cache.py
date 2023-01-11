from django.core.cache import cache
from django.shortcuts import reverse

from posts.models import Post, User
from posts.tests.utils import YatubeTestBase


class TestCache(YatubeTestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create(username='testuser')

    def setUp(self):
        cache.clear()

    def test_cache(self):
        address = reverse('posts:index')

        resp_orign = self.get_response_get(
            client=self.client,
            address=address,
        )

        new_post = Post.objects.create(
            text='Auto created post',
            author=TestCache.test_user
        )

        resp_after_createpost_from_cache = self.get_response_get(
            client=self.client,
            address=address,
        )

        self.assertEqual(
            resp_orign.content,
            resp_after_createpost_from_cache.content,
            f'Stage1. Страницы разные',
        )

        cache.clear()

        resp_after_createpost_cache_clear = self.get_response_get(
            client=self.client,
            address=address,
        )

        self.assertNotEqual(
            resp_orign.content,
            resp_after_createpost_cache_clear.content,
            f'Stage2. Страницы одинаковые',
        )
        

