from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password1', 'password2']

    def clean(self):
        super().clean()
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already exists")

        return self.cleaned_data
