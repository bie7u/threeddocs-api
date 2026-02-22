from rest_framework import serializers

from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
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
    nodePositions = serializers.JSONField(source='node_positions', default=dict)
    lastModified = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id',
            'name',
            'projectType',
            'projectModelUrl',
            'steps',
            'connections',
            'guide',
            'nodePositions',
            'lastModified',
        ]
        read_only_fields = ['id', 'lastModified']

    def get_lastModified(self, obj):
        return int(obj.updated_at.timestamp() * 1000)
