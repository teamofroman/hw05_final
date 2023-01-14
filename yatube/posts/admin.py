"""Модуль для регистрации моделей в панели администрирования."""

from django.contrib import admin

from posts import models


@admin.register(models.Post)
class PostAdmin(admin.ModelAdmin):
    """Настройка административной панели для модели Post."""

    list_display = ('pk', 'text', 'pub_date', 'author', 'group', 'image')
    search_fields = ('text',)
    list_filter = ('pub_date',)
    list_editable = ('group',)
    empty_value_display = '-пусто-'


@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'post', 'created', 'author')
    search_fields = ('text', 'author',)
    list_filter = ('created', 'author',)
    list_editable = ('author', 'post',)
    empty_value_display = '-пусто-'


@admin.register(models.Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')
    search_fields = ('user', 'author',)
    list_filter = ('user', 'author',)
    list_editable = ('user', 'author',)
    empty_value_display = '-пусто-'


@admin.register(models.Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'slug', 'description',)
    search_fields = ('slug',)
    empty_value_display = '-пусто-'
