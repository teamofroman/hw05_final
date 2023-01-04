from django.views.generic.base import TemplateView


class AuthorStaticPage(TemplateView):
    template_name = 'about/author.html'


class TechnologyStaticPage(TemplateView):
    template_name = 'about/technology.html'
