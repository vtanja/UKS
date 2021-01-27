from django.contrib.auth.models import User
from django.db import models
from app.user.models import Repository


# Create your models here.
class SiteUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    repositories = models.ManyToManyField(Repository)
