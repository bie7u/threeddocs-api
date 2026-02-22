from rest_framework import serializers

from .models import Project


class ProjectDataInputSerializer(serializers.Serializer):
    """Validates the nested ``project`` object in a SavedProject request body."""

    name = serializers.CharField(max_length=255)
    projectType = serializers.ChoiceField(
        choices=['builder', 'upload'], default='builder', required=False
    )
    projectModelUrl = serializers.CharField(
        allow_null=True, allow_blank=True, required=False, default=None
    )
    steps = serializers.ListField(child=serializers.DictField(), required=False, default=list)
    connections = serializers.ListField(child=serializers.DictField(), required=False, default=list)
    guide = serializers.ListField(child=serializers.DictField(), required=False, default=list)


class SavedProjectInputSerializer(serializers.Serializer):
    """Validates the full SavedProject envelope sent by the client."""

    project = ProjectDataInputSerializer()
    nodePositions = serializers.DictField(required=False, default=dict)
    lastModified = serializers.IntegerField(required=False)


def serialize_project(project: Project) -> dict:
    """Serialize a Project instance to the SavedProject envelope expected by the frontend."""
    return {
        'project': {
            'id': str(project.id),
            'name': project.name,
            'projectType': project.project_type,
            'projectModelUrl': project.project_model_url or None,
            'steps': project.steps,
            'connections': project.connections,
            'guide': project.guide,
        },
        'nodePositions': project.node_positions,
        'lastModified': int(project.updated_at.timestamp() * 1000),
    }
