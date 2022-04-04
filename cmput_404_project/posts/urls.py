from django.urls import path
from . import views

urlpatterns = [
    path('', views.display_public_posts, name='display_public_posts'),
    path('private_posts', views.display_private_posts, name='display_private_posts'),
    path('new_post/', views.new_post, name='new_post'),
    path('new_private_post/', views.new_private_post, name='new_private_post'),
    path('own_posts/<uuid:id>/', views.edit_post, name='edit_post'),
    path('own_posts/delete/<uuid:id>/', views.delete_post, name='delete_post'),
    path('own_posts/', views.display_own_posts, name='display_own_posts'),
    path('add_comment/<uuid:id>/', views.add_comment, name='add_comment'),
    path('add_comment/', views.add_comment, name='add_comment'),
    path('display_like/', views.display_like, name='display_like'),
    path('like_post1/', views.like_post1, name='like_post1'),
    path('share_post/<uuid:id>/', views.share_post, name='share_post'),
    path('share_post/', views.share_post, name='share_post'),

]