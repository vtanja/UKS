from django.db import models


# Create your models here.
from ..branch.models import Branch
from ..commit.models import Commit
from ..repository.models import Repository


class Tag(models.Model):
    version = models.CharField(max_length=10)
    title = models.CharField(max_length=30)
    description = models.TextField()
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)
    commit = models.ForeignKey(Commit, on_delete=models.CASCADE, null=True, blank=True)
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)