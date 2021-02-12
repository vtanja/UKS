from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from apps.repository.models import Repository


class Wiki(models.Model):
    title = models.CharField(max_length=100)
    content = RichTextField(blank=True, null=True)
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, null=False)

    def get_absolute_url(self):
        return "/repository/" + str(self.repository.id) + "/wiki/" + str(self.id) + "/"
