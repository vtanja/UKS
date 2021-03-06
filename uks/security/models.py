from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from apps.repository.models import Repository


class SiteUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_img = models.ImageField(default='profile_default.png')

    def get_absolute_url(self):
        return "/user/"+str(self.user.id) + "/profile/"
