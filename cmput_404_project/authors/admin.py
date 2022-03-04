from django.contrib import admin
from social_distribution.models import Author, Friends, FollowRequest

# admin.site.register(Author)
admin.site.register(Friends)
admin.site.register(FollowRequest)
