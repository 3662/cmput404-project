from django.urls import path

from . import views


urlpatterns = [
    # ex: /service/authors/
    path('authors/', views.authors_json, name='authors_json'),

]