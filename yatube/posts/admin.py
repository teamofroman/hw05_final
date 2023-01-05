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


admin.site.register(models.Group)
admin.site.register(models.Follow)
