from rest_framework import serializers

from .models import Author


class AuthorSerializer(serializers.Serializer):
    type = serializers.CharField(max_length=6)
    id = serializers.SlugField(required=True, read_only=True)

    