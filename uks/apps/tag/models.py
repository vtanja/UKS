from datetime import date

from django.db import models

from ..branch.models import Branch
from ..commit.models import Commit


class Tag(models.Model):
    version = models.CharField(max_length=10)
    title = models.CharField(max_length=30)
    description = models.TextField()
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)
    commit = models.ForeignKey(Commit, on_delete=models.CASCADE, null=True, blank=True)
    dateCreated = models.DateField(verbose_name='Created', default=date.today, blank=True)
