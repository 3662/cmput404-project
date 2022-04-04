from django.urls import path
from . import views

urlpatterns = [
    path('', views.display_authors, name='display_authors'),
    path('<uuid:id>/', views.display_author, name='display_author'),
    path('profile/', views.display_profile, name='profile'),
    path('inbox', views.display_inbox, name='inbox'),
    path('author_list/', views.author_list_view, name='author_list_view'),
    path('author_friend_view/', views.author_friend_view, name='author_friend_view'),
    path('pending_action_list_view/', views.pending_action_list_view, name='pending_action_list_view'),
    path('pending_action/', views.pending_action_view, name='pending_action_view'),
    path('<uuid:id>/follower/', views.follower_view, name='follower_view'),
    path('follower/', views.follower_view, name='follower_view'), # This is for viewing followers of foreign profiles
    path('follower_view1/', views.follower_view1, name='follower_view1'),
    path('friends/', views.friends_view, name='friend_view'),
    path('profile_follow/', views.author_profile_view, name='author_profile_view'),
    path('profile_like_post/', views.like_post2, name='like_post2'),
]
