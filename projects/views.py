from authentication.models import UserM
from rest_framework import generics, status, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins

from .models import Project, ProjectShare, Created3DModelM, Uploaded3DModel, Suggestion
from .serializers import ProjectSerializer, Created3dModelSerializer, Uploaded3dModelSerializer, SuggestionSerializer


class ProjectViewSet(viewsets.ModelViewSet):

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


class Created3DModelViewSet(mixins.ListModelMixin,
                            mixins.CreateModelMixin,
                            mixins.RetrieveModelMixin,
                            mixins.DestroyModelMixin,
                            GenericViewSet):
    serializer_class = Created3dModelSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None 

    def get_queryset(self):
        return Created3DModelM.objects.filter(owner=self.request.user)
    
    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def public_element(self, request, pk=None):
        project_uuid =  request.query_params.get('project_uuid')
        share = ProjectShare.objects.select_related('project').get(token=project_uuid)
        project = share.project
        allowed_elements = [int(item.get("custom3dElementId")) for item in project.steps if item.get("custom3dElementId")]
        if int(pk) not in allowed_elements:
            raise NotFound()
        try:
            element = Created3DModelM.objects.get(pk=pk)
        except Created3DModelM.DoesNotExist:
            raise NotFound()
        serializer = self.get_serializer(element)
        return Response(serializer.data)
    

class Uploaded3DModelViewSet(mixins.ListModelMixin,
                            mixins.CreateModelMixin,
                            mixins.RetrieveModelMixin,
                            mixins.DestroyModelMixin,
                            GenericViewSet):
    serializer_class = Uploaded3dModelSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None 

    def get_queryset(self):
        return Uploaded3DModel.objects.filter(owner=self.request.user)

    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def public_model(self, request, pk=None):
        project_uuid =  request.query_params.get('project_uuid')
        share = ProjectShare.objects.select_related('project').get(token=project_uuid)
        project = share.project
        allowed_elements = [int(item.get("uploadedModelId")) for item in project.steps if item.get("uploadedModelId")]
        if int(pk) not in allowed_elements:
            raise NotFound()
        try:
            element = Uploaded3DModel.objects.get(pk=pk)
        except Uploaded3DModel.DoesNotExist:
            raise NotFound()
        serializer = self.get_serializer(element)
        return Response(serializer.data)
    

class SuggestionViewSet(mixins.CreateModelMixin, GenericViewSet):
    queryset = Suggestion.objects.all()
    serializer_class = SuggestionSerializer
    permission_classes = [IsAuthenticated]


class UserCounterView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        users = UserM.objects.all().count()
        projects_count = Project.objects.all().count()
        project_shared = ProjectShare.objects.all().count()
        return Response({
            'users_count': users,
            'projects_count': projects_count,
            'project_shared_count': project_shared,
        })