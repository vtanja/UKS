from django.contrib import messages
from django.shortcuts import render, redirect

# Create your views here.


def dashboard(request):
    return render(request, 'dashboard.html')

def profile(request):
    return render(request, 'dashboard/profile.html')
