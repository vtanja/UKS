from django import forms

from ..branch.models import Branch
from ..tag.models import Tag


class CreateTagForm(forms.ModelForm):
    branch: forms.Select()

    def __init__(self, *args, **kwargs):
        self.repository = kwargs.pop('repository')
        super(CreateTagForm, self).__init__(*args, **kwargs)
        self.fields['branch'].choices = [(t.id, t.name) for t in
                                         Branch.objects.filter(repository=self.repository)]

    class Meta:
        model = Tag
        fields = ['version', 'title', 'description', 'branch']
