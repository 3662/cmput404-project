from django.urls import path

from . import views


urlpatterns = [
    # ex: /servce/authors/
    path('authors/', views.authors, name='authors'),

]