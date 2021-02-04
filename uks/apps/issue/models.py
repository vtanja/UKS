from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.repository.models import Repository


class Issue(models.Model):

    class IssueStatus(models.TextChoices):
        TODO = 'TODO', _('To do')
        ONGOING = 'ONGOING', _('Ongoing')
        DONE = 'DONE', _('Done')
        CLOSED = 'CLOSED', _('Closed')

    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    issue_status = models.CharField(
        max_length=8,
        choices=IssueStatus.choices,
        default=IssueStatus.TODO
    )
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_by')
    assignees = models.ManyToManyField(User, related_name='assignees', blank=True)
    # labels
    # milestone
    # board list

class IssueChange(models.Model):
    message = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
