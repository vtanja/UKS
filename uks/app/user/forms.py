from django import forms

from security.models import SiteUser


class ProfileImageUpdateForm(forms.ModelForm):
    class Meta:
        model = SiteUser
        fields = ['profile_img']