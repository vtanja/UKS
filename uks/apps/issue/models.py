from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
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
    description = RichTextField(blank=True, null=True)
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

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('issue-details', args=[str(self.repository_id), str(self.id)])

    def toggle_issue_close(self):
        if self.closed:
            self.closed = False
        else:
            self.closed = True
        self.save()

    def change_status(self, status):
        issue_change = IssueChange()
        issue_change.message = 'Issue changed status from {old} to {new}'.format(old=self.issue_status, new=status)
        issue_change.issue = self
        issue_change.date = timezone.now()
        issue_change.save()
        self.issue_status = status
        if status == 'DONE':
            self.closed = True
        else:
            self.closed = False
        self.save()


class IssueChange(models.Model):
    message = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
