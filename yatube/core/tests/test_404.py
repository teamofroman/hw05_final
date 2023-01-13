from django.test import TestCase


class Test404(TestCase):
    def test_404_template(self):
        """Test404: Тестирование корректности шаблона для ошибки 404."""
        response = self.client.get('/unexisting_page/')
        self.assertTemplateUsed(response, 'core/404.html')
