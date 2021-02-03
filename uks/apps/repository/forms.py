from django import forms

from security.models import SiteUser
from .models import Repository


class RepositoryForm(forms.ModelForm):
    class Meta:
        model = Repository
        fields = ['name', 'description', 'repo_url']
