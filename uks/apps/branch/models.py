from apps.commit.models import Commit
from apps.repository.models import Repository
from django.db import models


class Branch(models.Model):
    name = models.CharField(max_length=100)
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)
    head = models.ForeignKey(Commit, on_delete=models.PROTECT, null=True)

    def __str__(self):
        return self.name

    def as_dict(self):
        return {
            "name": self.name
        }
