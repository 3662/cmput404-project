from django.urls import path

from . import views

app_name = 'service'

urlpatterns = [
    path('authors', views.AuthorsDetailView.as_view(), name='authors'),
    # path('authors/', views.AuthorsDetailView.as_view(), name='authors'),
    path('authors/<uuid:author_id>', views.AuthorDetailView.as_view(), name='author'),
    path('authors/<uuid:author_id>/posts', views.PostsView.as_view(), name='posts'),
    # path('authors/<uuid:author_id>/posts/', views.PostsView.as_view(), name='posts'),
    path('authors/<uuid:author_id>/posts/<uuid:post_id>', views.PostView.as_view(), name='post'),
    path('authors/<uuid:author_id>/posts/<uuid:post_id>/likes', views.PostLikesView.as_view(), name='post_likes'),
    path('authors/<uuid:author_id>/followers', views.FollowersView.as_view(), name='followers'),
    path('authors/<uuid:author_id>/followers/<uuid:foreign_author_id>', views.FollowerView.as_view(), name='follower'),
    path('authors/<uuid:author_id>/posts/<uuid:post_id>/comments', views.CommentsView.as_view(), name='comments'),
    # path('authors/<uuid:author_id>/posts/<uuid:post_id>/comments/', views.CommentsView.as_view(), name='comments'),
    path('authors/<uuid:author_id>/posts/<uuid:post_id>/comments/<uuid:comment_id>/likes', views.CommentLikesView.as_view(), name='comment_likes'),
    path('authors/<uuid:author_id>/inbox', views.InboxView.as_view(), name='inbox'),
    # path('authors/<uuid:author_id>/inbox/', views.InboxView.as_view(), name='inbox'),
]