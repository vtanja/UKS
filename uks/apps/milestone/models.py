import django
from django.db import models
from datetime import date

# Create your models here.
from apps.repository.models import Repository


class Milestone(models.Model):
    title = models.CharField(max_length=30)
    description = models.TextField()
    dateCreated = models.DateField(verbose_name='Created', default=date.today, blank=True)
    dueDate = models.DateField(verbose_name='Due date')
    dateUpdated = models.DateField(verbose_name='Last updated', default=date.today, blank=True)
    closed = models.BooleanField(default=False)
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.title
