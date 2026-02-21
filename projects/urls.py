from django.urls import path

from .views import ProjectDetailView, ProjectListCreateView, ProjectPublicView

urlpatterns = [
    path('', ProjectListCreateView.as_view(), name='project-list-create'),
    path('<uuid:pk>', ProjectDetailView.as_view(), name='project-detail'),
    path('<uuid:pk>/public', ProjectPublicView.as_view(), name='project-public'),
]
