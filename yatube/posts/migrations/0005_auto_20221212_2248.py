# Generated by Django 2.2.6 on 2022-12-12 19:48

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_auto_20221114_0100'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='description',
            field=models.TextField(
                help_text='Введите описание сообщества.',
                verbose_name='Описание сообщества',
            ),
        ),
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=models.SlugField(
                help_text='Введите адрес сообщества. Допускаются английские буквы, цифры, символ подчеркивания.',
                unique=True,
                verbose_name='Сетевой адрес',
            ),
        ),
        migrations.AlterField(
            model_name='group',
            name='title',
            field=models.CharField(
                help_text='Введите название сообщества. Максимум 100 символов.',
                max_length=200,
                verbose_name='Название сообщества',
            ),
        ),
        migrations.AlterField(
            model_name='post',
            name='author',
            field=models.ForeignKey(
                help_text='Укажите автора публикации',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='posts',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Автор публикации',
            ),
        ),
        migrations.AlterField(
            model_name='post',
            name='group',
            field=models.ForeignKey(
                blank=True,
                help_text='Укажите сообщество, в котором разместить публикацию',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='posts',
                to='posts.Group',
                verbose_name='Сообщество',
            ),
        ),
        migrations.AlterField(
            model_name='post',
            name='pub_date',
            field=models.DateTimeField(
                auto_now_add=True,
                help_text='Введите дату публикации.',
                verbose_name='Дата публикации',
            ),
        ),
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(
                help_text='Введите текст публикации.',
                verbose_name='Текст публикации',
            ),
        ),
    ]
