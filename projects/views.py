from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Project
from .serializers import SavedProjectSerializer


class ProjectListCreateView(generics.ListCreateAPIView):
    serializer_class = SavedProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ProjectDetailView(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView,
):
    serializer_class = SavedProjectSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'put', 'delete', 'head', 'options']

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ProjectPublicView(generics.RetrieveAPIView):
    """Unauthenticated read-only access to a single project (shareable link)."""

    serializer_class = SavedProjectSerializer
    permission_classes = [AllowAny]
    queryset = Project.objects.all()

