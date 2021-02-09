from django import forms

from apps.milestone.models import Milestone
from django.forms import SelectDateWidget


class CreateMilestoneForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.repository = kwargs.pop('repository')
        super(CreateMilestoneForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Milestone
        fields = ['title', 'description', 'dueDate']
        widgets = {
            'dueDate': forms.DateInput(attrs={'type': 'date'})
        }
