from django.contrib.auth.models import User
from django.db.models import Q
from django.forms import ModelForm, ModelMultipleChoiceField, CheckboxSelectMultiple

from apps.issue.models import Issue


class CreateIssueForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.repository = kwargs.pop('repository')
        super(CreateIssueForm, self).__init__(*args, **kwargs)
        self.fields['assignees'].queryset = self.repository.collaborators

    class Meta:
        model = Issue
        fields = ['title', 'description', 'assignees']

