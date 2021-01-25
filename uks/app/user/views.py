from django.contrib import messages
from django.shortcuts import render, redirect

from security.models import SiteUser
# Create your views here.


def dashboard(request):
    repositories = request.user.siteuser.repositories.all()
    context = {'repositories': repositories}
    return render(request, 'user/dashboard.html', context)


def profile(request):
    return render(request, 'user/profile.html')
