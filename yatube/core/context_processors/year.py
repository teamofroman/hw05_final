"""Контекстный препроцессор."""
import datetime as dt

from django.core.handlers.wsgi import WSGIRequest


def year(request: WSGIRequest):
    """Возвращает текущий год."""
    return {'year': dt.datetime.now().year}
