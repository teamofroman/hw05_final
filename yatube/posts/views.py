"""В модуле определяются функции для отображения страниц."""

from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render
)
from django.views.decorators.cache import cache_page

from posts.forms import CommentForm, PostForm
from posts.models import Follow, Group, Post, User
from posts.utils import build_page_from_posts


@cache_page(20)
def index(request: WSGIRequest) -> HttpResponse:
    """Обрабатываем обращения к главной странице сайта."""
    posts = Post.objects.select_related('author')

    context = {
        'page_obj': build_page_from_posts(request, posts),
    }

    return render(request, 'posts/index.html', context)


def group_list(request: WSGIRequest, slug: str) -> HttpResponse:
    """Выводим посты группы с адресом slug."""
    group = get_object_or_404(Group, slug=slug)

    # posts = Post.objects.filter(group=group).select_related(
    #     'author',
    # )

    posts = group.posts.all()
    context = {
        'group': group,
        'page_obj': build_page_from_posts(request, posts),
    }

    return render(request, 'posts/group_list.html', context)


def profile(request: WSGIRequest, username: str):
    """Выводим все посты пользователя username."""
    user = get_object_or_404(User, username=username)
    is_follow = request.user.is_authenticated and request.user.follower.filter(
        author=user
    ).exists()

    context = {
        'author': user,
        'page_obj': build_page_from_posts(request, user.posts.all()),
        'is_following': is_follow,
    }

    return render(request, 'posts/profile.html', context)


def post_detail(request: WSGIRequest, post_id: int):
    post = get_object_or_404(Post, id=post_id)

    context = {
        'post': post,
        'comments': post.comments.all(),
        'form': CommentForm(),
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request: WSGIRequest):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )

    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()

        return redirect(
            'posts:profile',
            username=request.user.get_username(),
        )

    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request: WSGIRequest, post_id: int):
    post = get_object_or_404(Post, id=post_id)

    if request.user.get_username() != post.author.username:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form.save()

        return redirect(
            'posts:post_detail',
            post_id=post_id,
        )

    return render(
        request,
        'posts/create_post.html',
        {'form': form, 'is_edit': True},
    )


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = []
    for follower_user in request.user.follower.all():
        posts.extend(follower_user.author.posts.all())

    context = {
        'page_obj': build_page_from_posts(request, posts),
    }

    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author and not request.user.follower.filter(
            author=author
    ).exists():
        Follow.objects.create(
            user=request.user,
            author=author,
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    request.user.follower.filter(author=author).delete()
    return redirect('posts:profile', username=username)
