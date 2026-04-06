from django.conf import settings
from django.contrib.auth import authenticate
from django.db import transaction
from authentication.models import UserM
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer, UserSerializer, RegisterSerializer, ResetPasswordSerializer, \
    ResetPasswordConfSerializer
from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from .models import ResetPasswordM


ACCESS_COOKIE = getattr(settings, 'ACCESS_TOKEN_COOKIE', 'access_token')
REFRESH_COOKIE = getattr(settings, 'REFRESH_TOKEN_COOKIE', 'refresh_token')
HTTPONLY = getattr(settings, 'JWT_COOKIE_HTTPONLY', True)
SAMESITE = getattr(settings, 'JWT_COOKIE_SAMESITE', 'Lax')
SECURE = getattr(settings, 'JWT_COOKIE_SECURE', False)


def _set_token_cookies(response, refresh: RefreshToken) -> None:
    access_lifetime = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
    refresh_lifetime = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']

    response.set_cookie(
        ACCESS_COOKIE,
        str(refresh.access_token),
        max_age=int(access_lifetime.total_seconds()),
        httponly=HTTPONLY,
        samesite=SAMESITE,
        secure=SECURE,
    )
    response.set_cookie(
        REFRESH_COOKIE,
        str(refresh),
        max_age=int(refresh_lifetime.total_seconds()),
        httponly=HTTPONLY,
        samesite=SAMESITE,
        secure=SECURE,
    )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'message': 'Invalid email or password'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = UserM.objects.get(email=email)
        except UserM.DoesNotExist:
            return Response(
                {'message': 'Invalid email or password'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user = authenticate(request, username=user.username, password=password)
        if user is None:
            return Response(
                {'message': 'Invalid email or password'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)
        response = Response(UserSerializer(user).data, status=status.HTTP_200_OK)
        _set_token_cookies(response, refresh)
        return response


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'message': 'Wrong registration data.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        name = serializer.validated_data['name']
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        with transaction.atomic():
            if UserM.objects.filter(email=email).exists():
                return Response(
                    {'message': 'Email is already registered.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user = UserM.objects.create_user(
                first_name=name, username=email, email=email, password=password
            )
            user.first_name = name
            user.save()
            refresh = RefreshToken.for_user(user)
            response = Response(UserSerializer(user).data, status=status.HTTP_200_OK)
            _set_token_cookies(response, refresh)
            return response


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        current_password = request.data.get('currentPassword')
        new_password = request.data.get('newPassword')

        if not user.check_password(current_password):
            return Response(
                {'message': 'Current password is incorrect.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password changed successfully.'})
        

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie(ACCESS_COOKIE)
        response.delete_cookie(REFRESH_COOKIE)
        return response


class TokenRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        raw_refresh = request.COOKIES.get(REFRESH_COOKIE)
        if not raw_refresh:
            return Response(
                {'message': 'Refresh token not found.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            refresh = RefreshToken(raw_refresh)
        except (InvalidToken, TokenError):
            return Response(
                {'message': 'Invalid or expired refresh token.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        response = Response({'ok': True}, status=status.HTTP_200_OK)
        _set_token_cookies(response, refresh)
        return response


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class GoogleLoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        token =request.data.get('credential', None)
        if token:
            id_info = id_token.verify_oauth2_token(token, requests.Request(), settings.GOOGLE_CLIENT_ID)
            with transaction.atomic():
                email = id_info['email']
                user, _ = UserM.objects.get_or_create(email=email, username=email, is_google_user=True)
                refresh = RefreshToken.for_user(user)
                response = Response(UserSerializer(user).data, status=status.HTTP_200_OK)
                _set_token_cookies(response, refresh)
                return response
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class ResetPasswordViewSet(mixins.CreateModelMixin ,GenericViewSet):
    queryset = ResetPasswordM.objects.all()
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]


class ResetPasswordConfViewSet(mixins.CreateModelMixin, GenericViewSet):
    serializer_class = ResetPasswordConfSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.create(serializer.validated_data)
        return Response(status=status.HTTP_200_OK)