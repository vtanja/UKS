from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.repository.models import Repository
from apps.milestone.models import Milestone
from apps.label.models import Label
from apps.project.models import Project


class Issue(models.Model):
    class IssueStatus(models.TextChoices):
        TODO = 'TODO', _('To do')
        ONGOING = 'ONGOING', _('Ongoing')
        DONE = 'DONE', _('Done')

    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    issue_status = models.CharField(
        max_length=8,
        choices=IssueStatus.choices,
        default=IssueStatus.TODO
    )
    closed = models.BooleanField(default=False)
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_by')
    assignees = models.ManyToManyField(User, related_name='assignees', blank=True)
    labels = models.ManyToManyField(Label, blank=True)
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE, null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title

    def change_status(self, status):
        if status != 'CLOSED':
            self.issue_status = status
            self.closed = False
            self.save()
        else:
            self.closed = True
            self.save()


class IssueChange(models.Model):
    message = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
