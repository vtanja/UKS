from django.db import models


# Create your models here.
class Milestone(models.Model):
    title = models.CharField(max_length=30)
    description = models.TextField()
    dateCreated = models.DateField()
    dueDate = models.DateField()
