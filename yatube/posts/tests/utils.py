from django.test import TestCase
from django.template.context import RequestContext


class YatubeTestBase(TestCase):
    def get_field_from_context_by_type(self, context, field_type):
        if isinstance(context, RequestContext):
            context = context.flatten()
        for field in context.keys():
            if field not in ('user', 'request') and isinstance(
                    context[field], field_type
            ):
                return context[field]
        return None

    def get_field_from_context_by_name(self, context, field_name):
        if isinstance(context, RequestContext):
            context = context.flatten()
        for field in context.keys():
            if field == field_name:
                return context[field]
        return None

    def get_response_get(self, client, address, follow=False):
        response = None
        try:
            response = client.get(address, follow=follow)
        except Exception as error:
            self.assertIsNotNone(
                response,
                (
                    f'Страница `{address}` работает не правильно. '
                    f'Ошибка: `{error}`'
                ),
            )

        return response

    def get_response_post(self, client, address, post_data, follow=False):
        response = None
        try:
            response = client.post(address, data=post_data, follow=follow)
        except Exception as error:
            self.assertIsNotNone(
                response,
                (
                    f'Страница `{address}` работает не правильно. '
                    f'Ошибка: `{error}`'
                ),
            )

        return response
