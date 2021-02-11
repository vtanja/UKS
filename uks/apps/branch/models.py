from django.db import models


# Create your models here.
from apps.repository.models import Repository


class Branch(models.Model):
    name = models.CharField(max_length=100)
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def as_dict(self):
        return {
            "name": self.name
        }
