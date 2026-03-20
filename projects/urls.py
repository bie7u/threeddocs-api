from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import ProjectPublicView, ProjectShareView, ProjectSharedView, ProjectViewSet, Created3DModelViewSet

router = SimpleRouter(trailing_slash=False)
router.register('', ProjectViewSet, basename='project')
# router.register('created3dmodels', Created3DModelViewSet, basename='created3dmodel')

urlpatterns = [
    path('shared/<uuid:token>', ProjectSharedView.as_view(), name='project-shared'),
] + router.urls + [
    path('<int:pk>/public', ProjectPublicView.as_view(), name='project-public'),
    path('<int:pk>/share', ProjectShareView.as_view(), name='project-share'),
]
