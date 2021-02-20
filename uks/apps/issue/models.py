from apps.label.models import Label
from apps.milestone.models import Milestone
from apps.project.models import Project
from apps.repository.models import Repository
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django.db import models
from django.db.models import signals
from django.dispatch import receiver
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
    date_created = models.DateTimeField(verbose_name='Date of creation')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('issue-details', args=[str(self.repository_id), str(self.id)])

    def toggle_issue_close(self, user):
        self.closed = not self.closed
        self.save()
        if self.closed:
            message = 'closed'
            self.save()
            if self.milestone:
                milestone = getattr(self, 'milestone')
                if milestone.is_finished():
                    milestone.set_finish_time()
        else:
            message = 'opened'

        create_history_item(self, user, message)

    def change_status(self, status, user):
        create_history_item(self, user, 'changed issue status from {old} to {new}'
                            .format(old=self.issue_status, new=status))
        self.issue_status = status
        if status == 'DONE':
            self.closed = True
            create_history_item(self, user, 'closed')
            milestone = getattr(self, 'milestone')
            self.save()
            if milestone and milestone.is_finished():
                milestone.set_finish_time()
        else:
            self.closed = False
        self.save()


@receiver(signals.post_save, sender=Issue)
def post_save_create_history_items(sender, instance, created,  *args, **kwargs):
    if not created:
        return
    if instance.milestone:
        create_history_item(instance, instance.created_by, 'added this to "{}"'.format(instance.milestone.title))
    if instance.project:
        create_history_item(instance, instance.created_by, 'added this to "{}"'.format(instance.project.name))
    if instance.labels:
        create_history_item(instance, instance.created_by, 'added labels to this instance')
    if instance.assignees:
        create_history_item(instance, instance.created_by, 'added assignees to this instance')
