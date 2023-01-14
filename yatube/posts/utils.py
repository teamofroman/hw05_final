from django.core.paginator import Paginator

from posts.constants import MAX_POSTS_ON_PAGE


def build_page_from_posts(request, posts):
    page_number = request.GET.get('page', 1)
    return Paginator(posts, MAX_POSTS_ON_PAGE).get_page(page_number)
