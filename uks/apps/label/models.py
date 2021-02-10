from django.db import models
from colorfield.fields import ColorField
from apps.repository.models import Repository


# Create your models here.
class Label(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField()
    color = ColorField(format='hexa')
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.name
