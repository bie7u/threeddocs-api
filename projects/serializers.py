from rest_framework import serializers

from .models import Project


class ProjectDataSerializer(serializers.ModelSerializer):
    """Maps the Project model fields to the inner 'project' key (camelCase)."""

    projectType = serializers.ChoiceField(
        choices=['builder', 'upload'],
        source='project_type',
        default='builder',
    )
    projectModelUrl = serializers.CharField(
        source='project_model_url',
        allow_null=True,
        allow_blank=True,
        required=False,
        default=None,
    )

    class Meta:
        model = Project
        fields = ['id', 'name', 'projectType', 'projectModelUrl', 'steps', 'connections', 'guide']
        read_only_fields = ['id']


class SavedProjectSerializer(serializers.Serializer):
    """
    Full SavedProject envelope: {project: {...}, nodePositions: {...}, lastModified: N}.

    Uses source='*' on the nested serializer so the inner project fields are read
    from / written back to the Project instance directly (no extra nesting in
    validated_data).
    """

    project = ProjectDataSerializer(source='*')
    nodePositions = serializers.JSONField(source='node_positions', default=dict)
    lastModified = serializers.SerializerMethodField()

    def get_lastModified(self, obj):
        return int(obj.updated_at.timestamp() * 1000)

    def create(self, validated_data):
        return Project.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
