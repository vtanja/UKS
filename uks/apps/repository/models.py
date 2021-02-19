import logging

from django.contrib.auth.models import User
from django.db import models

logger = logging.getLogger('django')


class Repository(models.Model):
    name = models.CharField(max_length=30, unique=True, blank=False)
    description = models.TextField(blank=True)
    repo_url = models.CharField(max_length=100, blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner')
    collaborators = models.ManyToManyField(User, related_name='collaborators', blank=True)
    public = models.BooleanField(blank=False, default=True)

    def get_absolute_url(self):
        return "/repository/" + str(self.id) + "/"

    def test_user(self, user):
        logger.info('Checking if user has permission for action!')
        is_collab = user in self.collaborators.all()
        return is_collab or self.owner == user

    def test_access(self, user):
        logger.info('Checking if user has access!')
        if self.public:
            return True
        else:
            return self.test_user(user)
