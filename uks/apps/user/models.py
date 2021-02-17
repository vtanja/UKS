import datetime

from apps.issue.models import Issue
from apps.repository.models import Repository
from apps.wiki.models import Wiki
from django.contrib.auth.models import User
from django.db import models


class HistoryItem(models.Model):
    message = models.TextField()
    date_changed = models.DateTimeField()
    belongs_to = models.ForeignKey(User, on_delete=models.CASCADE)
    changed_wiki_object = models.ForeignKey(Wiki, on_delete=models.CASCADE, null=True)
    changed_repo_object = models.ForeignKey(Repository, on_delete=models.CASCADE, null=True)
    changed_issue = models.ForeignKey(Issue, on_delete=models.CASCADE, null=True)

    def get_time_of_change(self):
        if self.date_changed.date() == datetime.datetime.now().date():
            now = datetime.datetime.now().replace(tzinfo=None)
            diff = now - self.date_changed.replace(tzinfo=None)

            if diff.total_seconds() < 120:
                return ' Few moments ago '
            else:
                minutes = int(diff.total_seconds() // 60)
                if minutes > 60:
                    return (minutes // 60).__str__() + ' hours ago '
                elif 60 > minutes > 1:
                    return minutes.__str__() + ' minutes ago '
                else:
                    return ' Few moments ago '
        else:
            diff = datetime.datetime.now().date() - self.date_changed.date()
            if diff.days > 365:
                return repr(diff.days // 365).__str__() + ' years ago '
            elif diff.days > 30:
                return repr(diff.days // 30).__str__() + ' months ago'
            else:
                return diff.days.__str__() + ' days ago'
