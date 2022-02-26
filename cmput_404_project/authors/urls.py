from django.urls import path
from . import views

urlpatterns = [
    path('', views.display_authors, name='display_authors'),
    path('<uuid:id>/', views.display_author, name='display_author'),
]