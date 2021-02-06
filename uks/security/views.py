from django.contrib import messages
from django.shortcuts import render, redirect

# Create your views here.
from .forms import RegisterForm
from .models import SiteUser


def welcome(request):
    return render(request, 'welcome.html')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            site_user = SiteUser()
            site_user.user = user
            site_user.save()

            messages.success(request, 'Registration successful! You are being redirected to login page.')
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'security/register.html', {'form': form})
