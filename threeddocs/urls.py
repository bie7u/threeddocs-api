from django.contrib import admin
from django.urls import path, include

from projects.views import ProjectViewSet

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    # Handle /api/projects (no trailing slash) – list + create
    path('api/projects', ProjectViewSet.as_view({'get': 'list', 'post': 'create'})),
    # Handle /api/projects/ (with trailing slash) plus /<int:pk> and /<int:pk>/public
    path('api/projects/', include('projects.urls')),
]
