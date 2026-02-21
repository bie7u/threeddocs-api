from django.contrib import admin
from django.urls import path, include

from projects.views import ProjectListCreateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    # Handle /api/projects (no trailing slash) – POST and GET list
    path('api/projects', ProjectListCreateView.as_view()),
    # Handle /api/projects/ (with trailing slash) plus /<uuid> and /<uuid>/public
    path('api/projects/', include('projects.urls')),
]
