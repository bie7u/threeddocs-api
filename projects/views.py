from rest_framework import generics, status, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Project, ProjectShare
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


class ProjectShareView(APIView):
    """POST /api/projects/:id/share – Generate (or return existing) share token."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            project = Project.objects.get(pk=pk, owner=request.user)
        except Project.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        share, _ = ProjectShare.objects.get_or_create(project=project)
        return Response({'shareToken': str(share.token)})


class ProjectSharedView(generics.RetrieveAPIView):
    """GET /api/projects/shared/:token – Public access via share token."""

    serializer_class = ProjectSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        token = self.kwargs['token']
        try:
            share = ProjectShare.objects.select_related('project').get(token=token)
        except ProjectShare.DoesNotExist:
            raise NotFound()
        return share.project
