from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.
class Issue(models.Model):

    class IssueStatus(models.TextChoices):
        TODO = 'TODO', _('To do')
        ONGOING = 'ONGOING', _('Ongoing')
        DONE =  'DONE', _('Done')

    title = models.CharField(max_length=30)
    description = models.CharField(max_length=100)
    issue_status = models.CharField(
        max_length=8,
        choices=IssueStatus.choices,
        default=IssueStatus.TODO
    )
