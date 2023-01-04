"""Регистрация пользовательских фильтров для html."""
from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={'class': css})


@register.filter
def correct_username(value):
    if value.get_full_name() == '':
        return value.username
    else:
        return value.get_full_name()
