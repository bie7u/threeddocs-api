from django.urls import path

from .views import ProjectDetailView, ProjectListCreateView, ProjectPublicView

urlpatterns = [
    path('', ProjectListCreateView.as_view(), name='project-list-create'),
    path('<int:pk>', ProjectDetailView.as_view(), name='project-detail'),
    path('<int:pk>/public', ProjectPublicView.as_view(), name='project-public'),
]
