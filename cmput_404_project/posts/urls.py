from django.urls import path
from . import views

urlpatterns = [
    path('', views.display_public_posts, name='display_public_posts'),
    path('new_post/', views.new_post, name='new_post'),
    path('own_posts/<uuid:id>/', views.edit_post, name='edit_post'),
    path('own_posts/', views.display_own_posts, name='display_own_posts'),
    path('add_comment/<uuid:id>/', views.add_comment, name='add_comment'),
    path('add_comment/', views.add_comment, name='add_comment'),
]