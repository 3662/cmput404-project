from django.urls import path

from . import views

app_name = 'accounts'
urlpatterns = [
    path('signup/', views.signup_request, name='signup'),
    path('manage_profile/', views.manage_profile, name='manage_profile'),
]
