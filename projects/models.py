import uuid

from django.contrib.auth.models import User
from django.db import models


class Project(models.Model):
    PROJECT_TYPE_CHOICES = [
        ('builder', 'Builder'),
        ('upload', 'Upload'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=255)
    project_type = models.CharField(
        max_length=10,
        choices=PROJECT_TYPE_CHOICES,
        default='builder',
    )
    project_model_url = models.TextField(blank=True, null=True, default=None)
    steps = models.JSONField(default=list)
    connections = models.JSONField(default=list)
    guide = models.JSONField(default=list)
    node_positions = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.name} ({self.owner.username})'


class Created3DModelM(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created3d_models')
    name = models.CharField(max_length=255)
    text = models.CharField(max_length=255)
    color = models.CharField(max_length=12)
    description = models.CharField(max_length=1000, blank=True, null=True, default=None)
    texture_data_url = models.TextField(blank=True, null=True, default=None)


class Uploaded3DModel(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded3d_models')
    model_data_url = models.TextField()
    model_file_name = models.CharField(max_length=255)
    model_scale = models.FloatField(default=1.0)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=1000, blank=True, null=True, default=None)
    system_model = models.BooleanField(default=False) 


class ProjectShare(models.Model):
    """Holds the public share token for a project (one token per project)."""

    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='share')
    token = models.UUIDField(default=uuid.uuid4, unique=True)

    def __str__(self):
        return f'Share({self.project_id}): {self.token}'


class Suggestion(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.CharField(max_length=10000)
    added_at = models.DateTimeField(auto_now_add=True)
