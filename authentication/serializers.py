from django.contrib.auth.models import User
from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    email = serializers.EmailField()
    name = serializers.SerializerMethodField()

    def get_id(self, user):
        return str(user.id)

    def get_name(self, user):
        full = f'{user.first_name} {user.last_name}'.strip()
        return full or user.username
