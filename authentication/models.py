from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class UserM(AbstractUser):
    is_google_user = models.BooleanField(default=False)

    class Meta:
        swappable = "AUTH_USER_MODEL"


class ResetPasswordM(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    is_used = models.BooleanField(default=False)
    user = models.ForeignKey(UserM, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
