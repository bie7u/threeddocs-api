from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import SimpleRouter

from projects.views import ProjectViewSet, Created3DModelViewSet, Uploaded3DModelViewSet, \
    SuggestionViewSet, UserCounterView

router = SimpleRouter()
router.register('elements', Created3DModelViewSet, basename='element')
router.register('models', Uploaded3DModelViewSet, basename='model')
router.register('suggestion', SuggestionViewSet, basename='suggestion')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user_counter', UserCounterView.as_view(), name='user-counter'),
    path('api/auth/', include('authentication.urls')),
    path('api/projects', ProjectViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('api/projects/', include('projects.urls')),
    path('api/', include(router.urls)),
    path('api/models', Uploaded3DModelViewSet.as_view({'get': 'list', 'post': 'create', 'retrieve': 'get', 'delete': 'destroy'})),
    path('api/models/<int:pk>', Uploaded3DModelViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'})),
]
