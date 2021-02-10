from django.db import models

# Create your models here.
from apps.repository.models import Repository


class Wiki(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, null=False)
