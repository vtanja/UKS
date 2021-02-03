from django.db import models


# Create your models here.
from app.user.models import Repository


class Milestone(models.Model):
    title = models.CharField(max_length=30)
    description = models.TextField()
    dateCreated = models.DateField()
    dueDate = models.DateField()
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.title
