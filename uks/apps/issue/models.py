from apps.label.models import Label
from apps.milestone.models import Milestone
from apps.project.models import Project
from apps.repository.models import Repository
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def create_history_item(issue, user, message):
    from apps.user.models import HistoryItem
    history_item = HistoryItem()
    history_item.message = message
    history_item.changed_issue = issue
    history_item.date_changed = timezone.now()
    history_item.belongs_to = user
    history_item.save()


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

    def toggle_issue_close(self, user):
        if self.closed:
            message = 'opened'
        else:
            message = 'closed'
        create_history_item(self, user, message)
        self.closed = not self.closed
        self.save()

    def change_status(self, status, user):
        create_history_item(self, user, 'changed issue status from {old} to {new}'
                            .format(old=self.issue_status, new=status))
        self.issue_status = status
        if status == 'DONE':
            self.closed = True
        else:
            self.closed = False
        self.save()
