from django.contrib.auth.models import User
from django.db import models


class Repository(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField()
    repo_url = models.CharField(max_length=100, blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner')
    collaborators = models.ManyToManyField(User, related_name='collaborators', blank=True)

    def get_absolute_url(self):
        return "/repository/" + str(self.id) + "/"