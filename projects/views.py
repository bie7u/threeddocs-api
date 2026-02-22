from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Project
from .serializers import ProjectSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    """
    Single view for all authenticated project operations.

    list    → GET  /api/projects
    create  → POST /api/projects
    retrieve → GET  /api/projects/{id}
    update  → PUT  /api/projects/{id}
    destroy → DELETE /api/projects/{id}

    PATCH is intentionally disabled – use PUT for full replacement.
    """

    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'delete', 'head', 'options']

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ProjectPublicView(generics.RetrieveAPIView):
    """Unauthenticated read-only access to a single project (shareable link)."""

    serializer_class = ProjectSerializer
    permission_classes = [AllowAny]
    queryset = Project.objects.all()
