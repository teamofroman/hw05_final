from django.urls import path

from about import views

app_name = 'about'

urlpatterns = [
    path('author/', views.AuthorStaticPage.as_view(), name='author'),
    path('tech/', views.TechnologyStaticPage.as_view(), name='tech'),
]
