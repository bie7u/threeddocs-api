from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import ProjectPublicView, ProjectViewSet

router = SimpleRouter(trailing_slash=False)
router.register('', ProjectViewSet, basename='project')

urlpatterns = router.urls + [
    path('<int:pk>/public', ProjectPublicView.as_view(), name='project-public'),
]
