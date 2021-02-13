from django import forms

from apps.wiki.models import Wiki


class CreateWikiForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.repository = kwargs.pop('repository')
        super(CreateWikiForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Wiki
        fields = ['title', 'content']