from rest_framework import serializers
from .models import Project, Created3DModelM, Uploaded3DModel, Suggestion
import base64


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

    def validate(self, attrs):
        user = self.context['request'].user
        projects_count = Project.objects.filter(owner=user).count()
        if self.instance is None and projects_count >= 30:
            raise serializers.ValidationError('You have reached the limit of 30 projects.')
        return super().validate(attrs)

    def get_lastModified(self, obj):
        return int(obj.updated_at.timestamp() * 1000)


class Created3dModelSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Created3DModelM
        fields = ['id', 'name', 'text', 'color', 'texture_data_url', 'description']

    def validate(self, attrs):
        user = self.context['request'].user
        created_models = Created3DModelM.objects.filter(owner=user).count()
        if created_models >= 20:
            raise serializers.ValidationError('You have reached the limit of 20 created 3D models.')
        return super().validate(attrs)
    
    def create(self, validated_data):
        user = self.context['request'].user
        return Created3DModelM.objects.create(owner=user, **validated_data)


class Uploaded3dModelSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Uploaded3DModel
        fields = ['id', 'name', 'model_file_name', 'model_scale', 'model_data_url', 'description', 'system_model']
        extra_kwargs = {
            'system_model': {'read_only': True},}
        
    def validate_model_data_url(self, value):
        # Zakładamy, że to base64 string: "data:...;base64,...."
        if value and ';base64,' in value:
            base64_data = value.split(';base64,')[1]
            decoded = base64.b64decode(base64_data)
            if len(decoded) > 10 * 1024 * 1024:  # 10 MB
                raise serializers.ValidationError("Plik nie może być większy niż 10MB.")
        return value
    
    def validate(self, attrs):
        user = self.context['request'].user
        uploaded_models = Uploaded3DModel.objects.filter(owner=user).count()
        if uploaded_models >= 10:
            raise serializers.ValidationError('You have reached the limit of 10 uploaded 3D models.')
        return super().validate(attrs)

    def create(self, validated_data):
        user = self.context['request'].user
        return Uploaded3DModel.objects.create(owner=user, **validated_data)
    

class SuggestionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Suggestion
        fields = ['id', 'content']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)
