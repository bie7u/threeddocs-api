import uuid

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Project
from .serializers import SavedProjectInputSerializer, serialize_project


def _first_error(errors: dict) -> str:
    """Extract the first human-readable error message from a DRF errors dict."""
    for value in errors.values():
        if isinstance(value, list) and value:
            return str(value[0])
        if isinstance(value, dict):
            return _first_error(value)
        return str(value)
    return 'Validation error.'


def _project_from_input(owner, validated_data, project: Project = None) -> Project:
    """Create or fully replace a Project from validated SavedProjectInputSerializer data."""
    project_data = validated_data['project']
    node_positions = validated_data.get('nodePositions', {})

    fields = dict(
        name=project_data['name'],
        project_type=project_data.get('projectType', 'builder'),
        project_model_url=project_data.get('projectModelUrl'),
        steps=project_data.get('steps', []),
        connections=project_data.get('connections', []),
        guide=project_data.get('guide', []),
        node_positions=node_positions,
    )

    if project is None:
        project_id = project_data.get('id') or uuid.uuid4()
        project = Project.objects.create(id=project_id, owner=owner, **fields)
    else:
        for key, value in fields.items():
            setattr(project, key, value)
        project.save()

    return project


class ProjectListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        projects = Project.objects.filter(owner=request.user)
        return Response([serialize_project(p) for p in projects])

    def post(self, request):
        ser = SavedProjectInputSerializer(data=request.data)
        if not ser.is_valid():
            return Response(
                {'message': _first_error(ser.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        project_id = ser.validated_data['project'].get('id')
        if project_id and Project.objects.filter(pk=project_id).exists():
            return Response(
                {'message': 'A project with this id already exists.'},
                status=status.HTTP_409_CONFLICT,
            )

        project = _project_from_input(request.user, ser.validated_data)
        return Response(serialize_project(project), status=status.HTTP_201_CREATED)


class ProjectDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_project(self, request, pk):
        return get_object_or_404(Project, pk=pk, owner=request.user)

    def get(self, request, pk):
        project = self._get_project(request, pk)
        return Response(serialize_project(project))

    def put(self, request, pk):
        project = self._get_project(request, pk)
        ser = SavedProjectInputSerializer(data=request.data)
        if not ser.is_valid():
            return Response(
                {'message': _first_error(ser.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        project = _project_from_input(request.user, ser.validated_data, project=project)
        return Response(serialize_project(project))

    def delete(self, request, pk):
        project = self._get_project(request, pk)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectPublicView(APIView):
    """Unauthenticated read-only access to a single project (shareable link)."""

    permission_classes = [AllowAny]

    def get(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        return Response(serialize_project(project))

