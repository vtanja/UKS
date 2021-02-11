from django import forms

from .models import Label
from colorfield.widgets import ColorWidget


class CreateLabelForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.repository = kwargs.pop('repository')
        super(CreateLabelForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Label
        fields = ['name', 'description', 'color']
        widgets = {
            'color': ColorWidget
        }
