from django import forms

from security.models import SiteUser
from .models import Repository


class ProfileImageUpdateForm(forms.ModelForm):
    class Meta:
        model = SiteUser
        fields = ['profile_img']


class RepositoryForm(forms.ModelForm):
    class Meta:
        model = Repository
        fields = ['name', 'description']
