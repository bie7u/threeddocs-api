from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import LoginView, LogoutView, MeView, TokenRefreshView, RegisterView, ChangePasswordView, GoogleLoginView, ResetPasswordViewSet, ResetPasswordConfViewSet

router = DefaultRouter()
router.register(r'reset-password', ResetPasswordViewSet)
router.register(r'reset-password-conf', ResetPasswordConfViewSet, basename='reset-password-conf')

urlpatterns = [
    path('login', LoginView.as_view(), name='auth-login'),
    path('register', RegisterView.as_view(), name='auth-register'),
    path('change-password', ChangePasswordView.as_view(), name='auth-change-password'),
    path('logout', LogoutView.as_view(), name='auth-logout'),
    path('refresh', TokenRefreshView.as_view(), name='auth-token-refresh'),
    path('me', MeView.as_view(), name='auth-me'),
    path('google/', GoogleLoginView.as_view(), name='google-login'),
    path('', include(router.urls)),
]
