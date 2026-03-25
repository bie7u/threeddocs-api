from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import SimpleRouter

from projects.views import UserCounterView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user_counter', UserCounterView.as_view(), name='user-counter'),
    path('api/auth/', include('authentication.urls')),
    path('api/', include('projects.urls')),
]
