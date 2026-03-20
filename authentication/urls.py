from django.urls import path

from .views import LoginView, LogoutView, MeView, TokenRefreshView, RegisterView, ChangePasswordView

urlpatterns = [
    path('login', LoginView.as_view(), name='auth-login'),
    path('register', RegisterView.as_view(), name='auth-register'),
    path('change-password', ChangePasswordView.as_view(), name='auth-change-password'),
    path('logout', LogoutView.as_view(), name='auth-logout'),
    path('refresh', TokenRefreshView.as_view(), name='auth-token-refresh'),
    path('me', MeView.as_view(), name='auth-me'),
]
