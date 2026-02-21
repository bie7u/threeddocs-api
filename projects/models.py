import uuid

from django.contrib.auth.models import User
from django.db import models


class Project(models.Model):
    PROJECT_TYPE_CHOICES = [
        ('builder', 'Builder'),
        ('upload', 'Upload'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=255)
    project_type = models.CharField(
        max_length=10,
        choices=PROJECT_TYPE_CHOICES,
        default='builder',
    )
    project_model_url = models.URLField(blank=True, default='')
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

