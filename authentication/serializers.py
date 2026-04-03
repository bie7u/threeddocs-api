from authentication.models import UserM
from rest_framework import serializers
from .models import ResetPasswordM
from django.core.exceptions import ObjectDoesNotExist
from .utils import send_password_reset_email
from django.db import transaction
from rest_framework.response import Response

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    email = serializers.EmailField()
    name = serializers.SerializerMethodField()
    is_google_user = serializers.SerializerMethodField()

    def get_id(self, user):
        return str(user.id)

    def get_name(self, user):
        full = f'{user.first_name} {user.last_name}'.strip()
        return full or user.username

    def get_is_google_user(self, user):
        return user.is_google_user


class RegisterSerializer(serializers.Serializer):
    name = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)

    class Meta:
        model = ResetPasswordM
        fields = ('email',)

    def validate(self, attrs):
        email = attrs.get('email', None)
        try:
            user = UserM.objects.get(email=email)
            if user.is_google_user:
                raise serializers.ValidationError('Google user can not change password.')
            attrs['user'] = user
        except ObjectDoesNotExist:
            raise serializers.ValidationError('User with this email does not exist.')
        return super().validate(attrs)

    def create(self, validated_data):
        email = validated_data.get('email')
        user = validated_data.get('user')
        with transaction.atomic():
            reset_password_obj = ResetPasswordM.objects.create(user=user)
            send_password_reset_email(email, reset_password_obj.uuid)
            return reset_password_obj


class ResetPasswordConfSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    token = serializers.CharField()

    def validate(self, attrs):
        uuid = attrs.pop('token', None)
        try:
            pass_reset_obj = ResetPasswordM.objects.get(uuid=uuid)
            if pass_reset_obj.is_used:
                raise serializers.ValidationError('This reset token is already used.')
            attrs['reset_obj'] = pass_reset_obj
            return attrs
        except ObjectDoesNotExist:
            raise serializers.ValidationError('Bad token.')

    def create(self, validated_data):
        password = validated_data.get('password')
        reset_obj = validated_data.get('reset_obj')
        user = reset_obj.user
        with transaction.atomic():
            user.set_password(password)
            user.save()
            reset_obj.is_used = True
            reset_obj.save()