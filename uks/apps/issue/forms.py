from apps.issue.models import Issue
from apps.milestone.models import Milestone
from apps.label.models import Label
from django.forms import ModelForm


class CreateIssueForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.repository = kwargs.pop('repository')
        super(CreateIssueForm, self).__init__(*args, **kwargs)
        self.fields['assignees'].queryset = self.repository.collaborators
        self.fields['milestone'].queryset = Milestone.objects.filter(repository=self.repository)
        self.fields['labels'].queryset = Label.objects.filter(repository=self.repository)

    class Meta:
        model = Issue
        fields = ['title', 'description', 'assignees', 'labels', 'milestone']

