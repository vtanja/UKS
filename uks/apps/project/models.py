from django.db import models

# Create your models here.
from apps.repository.models import Repository
from django.urls import reverse


class Project(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField(blank=True)
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('project_details', args=[str(self.repository_id), str(self.pk)])
