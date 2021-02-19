import django
from django.db import models
from datetime import date, datetime

# Create your models here.
from apps.repository.models import Repository
from django.urls import reverse


class Milestone(models.Model):
    title = models.CharField(max_length=30)
    description = models.TextField()
    dateCreated = models.DateField(verbose_name='Created', default=date.today, blank=True)
    dueDate = models.DateField(verbose_name='Due date')
    dateUpdated = models.DateField(verbose_name='Last updated', default=date.today, blank=True)
    closed = models.BooleanField(default=False)
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.title

    def get_completed_percentage(self):
        all_count = self.issue_set.count()
        if all_count == 0:
            return 100
        closed_count = self.issue_set.filter(closed=True).count()
        res = (100*closed_count)/all_count
        return round(res)

    def get_issue_count(self):
        return self.issue_set.count()

    def get_closed_issues_count(self):
        return self.issue_set.filter(closed=True).count()

    def toggle_milestone_close(self):
        self.closed = not self.closed
        self.dateUpdated = datetime.now()
        self.save()

    def set_updated(self):
        self.dateUpdated = datetime.now()
        self.save()

    def get_absolute_url(self):
        return reverse('milestone_details', args=[str(self.repository_id), str(self.pk)])
