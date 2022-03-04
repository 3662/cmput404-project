from django.urls import path

from . import views

app_name = 'service'

urlpatterns = [
    path('authors/', views.AuthorsDetailView.as_view(), name='authors_detail'),
    path('authors/<uuid:author_id>/', views.AuthorDetailView.as_view(), name='author'),
    path('authors/<uuid:author_id>/posts/', views.PostsView.as_view(), name='posts'),
    path('authors/<uuid:author_id>/posts/<uuid:post_id>/', views.PostView.as_view(), name='posts'),
    path('authors/<uuid:author_id>/followers/', views.FollowersView.as_view(), name='followers_detail'),
    path('authors/<uuid:author_id>/followers/<uuid:foreign_author_id>/', views.FollowerView.as_view(), name='follower'),
]