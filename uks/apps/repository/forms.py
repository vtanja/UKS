from django import forms
from django.contrib.auth.models import User

from .models import Repository


class RepositoryForm(forms.ModelForm):

    class Meta:
        model = Repository
        fields = ['name', 'description', 'repo_url']


class RepositoryFormEdit(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.repository = kwargs.pop('repository')
        super(RepositoryFormEdit, self).__init__(*args, **kwargs)

    class Meta:
        model = Repository
        fields = ['name']


class CollaboratorsForm(forms.Form):
    class Meta:
        model = User
        field = ['collaborators']
        widgets = {
            'collaborators': forms.MultipleChoiceField
        }
