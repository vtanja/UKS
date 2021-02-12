import datetime

from django.contrib.auth.models import User
from django.db import models

from apps.repository.models import Repository
from apps.wiki.models import Wiki


class HistoryItem(models.Model):
    message = models.TextField()
    dateChanged = models.DateTimeField()
    belongsTo = models.ForeignKey(User, on_delete=models.CASCADE)
    changed_wiki_object = models.ForeignKey(Wiki, on_delete=models.CASCADE, null=True)
    changed_repo_object = models.ForeignKey(Repository, on_delete=models.CASCADE, null=True)

    def get_time_of_change(self):
        if self.dateChanged.date() == datetime.datetime.now().date():
            now = datetime.datetime.now().replace(tzinfo=None)
            diff = now - self.dateChanged.replace(tzinfo=None)

            if diff.total_seconds() < 120:
                return ' Few moments ago '
            else:
                minutes = int(diff.total_seconds() // 60)
                if minutes > 60:
                   return (minutes // 60).__str__() + ' hours ago '
                elif minutes < 60 and minutes > 1:
                   return (minutes).__str__() + ' minutes ago '
                else:
                    return ' Few moments ago '
        else:
            diff = datetime.datetime.now().date() - self.dateChanged.date()
            print(diff.days)
            if diff.days > 365:
                return repr(diff.days // 365).__str__() + ' years ago '
            elif diff.days > 30:
                return repr(diff.days // 30).__str__() + ' months ago'
            else:
                return diff.days.__str__() + ' days ago'