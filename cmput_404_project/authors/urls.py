from django.urls import path
from . import views

urlpatterns = [
    # path('', views.index, name='index'),
    path('', views.display_authors),
    path('<slug:slug>/', views.display_author, name='display_author'),
]