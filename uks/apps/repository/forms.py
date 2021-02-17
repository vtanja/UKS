from django import forms
from django.contrib.auth.models import User

from .models import Repository


class RepositoryForm(forms.ModelForm):
    class Meta:
        model = Repository
        fields = ['name', 'description', 'repo_url']


class CollaboratorsForm(forms.Form):
    class Meta:
        model = User
        field = ['collaborators']
        widgets = {
            'collaborators': forms.MultipleChoiceField
        }
