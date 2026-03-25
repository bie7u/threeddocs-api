from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import ProjectSharedView, ProjectViewSet, Created3DModelViewSet, Uploaded3DModelViewSet, \
    SuggestionViewSet, PublicUploaded3DModelViewSet

router = SimpleRouter()
router.register('elements', Created3DModelViewSet, basename='element')
router.register('models', Uploaded3DModelViewSet, basename='model')
router.register('suggestion', SuggestionViewSet, basename='suggestion')
router.register('public-models', PublicUploaded3DModelViewSet, basename='public-model')
router.register('projects', ProjectViewSet, basename='project')

urlpatterns = [
    path('', include(router.urls)),
    path('shared/<uuid:token>', ProjectSharedView.as_view(), name='project-shared'),
]
