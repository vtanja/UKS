from django.db import models


class Repository(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField()
    repo_url = models.CharField(max_length=100, default='https://github.com/vtanja/UKS')
