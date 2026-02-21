from rest_framework import serializers

from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Project
        fields = [
            'id',
            'name',
            'project_type',
            'project_model_url',
            'steps',
            'connections',
            'guide',
            'node_positions',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProjectListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing projects (without heavy JSON fields)."""

    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'project_type', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
