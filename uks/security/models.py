from django.contrib.auth.models import User
from django.db import models
from apps.repository.models import Repository


# Create your models here.
class SiteUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_img = models.ImageField(default='profile_default.png')
