from django.contrib import messages
from django.shortcuts import render, redirect

# Create your views here.
from .forms import RegisterForm


def welcome(request):
    return render(request, 'welcome.html')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful! You are being redirected to login page.')
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'security/register.html', {'form': form})
