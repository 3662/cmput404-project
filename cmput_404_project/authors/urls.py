from django.urls import path
from . import views

urlpatterns = [
    path('', views.display_authors, name='display_authors'),
    path('<uuid:id>/', views.display_author, name='display_author'),
    path('author_list/', views.author_list_view, name='author_list_view'),
    path('author_friend_view/', views.author_friend_view, name='author_friend_view'),
    path('pending_action_list_view/', views.pending_action_list_view, name='pending_action_list_view'),
    path('pending_action_view/', views.pending_action_view, name='pending_action_view'),
]
