from about import views
from django.urls import path

app_name = 'about'

urlpatterns = [
    path('author/', views.AuthorStaticPage.as_view(), name='author'),
    path('tech/', views.TechnologyStaticPage.as_view(), name='tech'),
]
