"""Описание моделей БД."""
from django.contrib.auth import get_user_model
from django.db import models
from posts.constants import MAX_PRESENTATION_LENGTH

User = get_user_model()


class Group(models.Model):
    """Модель сообщества (group)."""

    title = models.CharField(
        max_length=200,
        verbose_name='Название сообщества',
        help_text='Введите название сообщества. Максимум 100 символов.',
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Сетевой адрес',
        help_text=(
            'Введите адрес сообщества. Допускаются английские буквы, '
            'цифры, символ подчеркивания.'
        ),
    )
    description = models.TextField(
        verbose_name='Описание сообщества',
        help_text='Введите описание сообщества.',
    )

    class Meta:
        """Класс для дополнительных параметров модели."""

        verbose_name = 'Сообщество'
        verbose_name_plural = 'Сообщества'

    def __str__(self) -> str:
        """Возвращает описание модели."""
        return self.title


class Post(models.Model):
    """Класс, описывающий модель карточки публикации."""

    text = models.TextField(
        verbose_name='Текст публикации',
        help_text='Введите текст публикации.',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        help_text='Введите дату публикации.',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор публикации',
        help_text='Укажите автора публикации',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='Сообщество',
        help_text='Укажите сообщество, в котором разместить публикацию',
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True,
    )

    class Meta:
        """Класс для дополнительных параметров модели."""

        ordering = ['-pub_date']
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self) -> str:
        """Возвращает описание модели."""
        return (
            self.text[:MAX_PRESENTATION_LENGTH] + '...'
            if len(self.text) > MAX_PRESENTATION_LENGTH
            else self.text
        )


class Comment(models.Model):
    text = models.TextField(
        verbose_name='Комментарий',
        help_text='Введите комментарий к посту.',
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата комментария',
        help_text='Введите дату комментарий.',
    )
    post = models.ForeignKey(
        Post,
        related_name='comments',
        on_delete=models.CASCADE,
        verbose_name='Комментируемый пост',
        help_text='Выберите комментируемый пост.'
    )
    author = models.ForeignKey(
        User,
        related_name='comments',
        on_delete=models.CASCADE,
        verbose_name='Автор комментария',
        help_text='Выберите автора комментария.'
    )

    class Meta:
        """Класс для дополнительных параметров модели."""

        ordering = ['-created']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self) -> str:
        return (
            self.text[:MAX_PRESENTATION_LENGTH] + '...'
            if len(self.text) > MAX_PRESENTATION_LENGTH
            else self.text
        )
