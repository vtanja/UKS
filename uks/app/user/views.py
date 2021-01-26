from django.contrib import messages
from django.shortcuts import render, redirect

from app.user.forms import ProfileImageUpdateForm
from security.models import SiteUser
# Create your views here.


def dashboard(request):
    repositories = request.user.siteuser.repositories.all()
    context = {'repositories': repositories}
    return render(request, 'user/dashboard.html', context)


def profile(request):
    if request.method == 'POST':
        p_form = ProfileImageUpdateForm(request.POST,
                                        request.FILES,
                                        instance=request.user.siteuser)
        if p_form.is_valid():
            p_form.save()
            messages.success(request, f'Tou have successfully updated your profile!')
            return redirect('profile')
    else:
        p_form = ProfileImageUpdateForm(instance=request.user.siteuser)

    context = {
        'p_form' : p_form
    }
    return render(request, 'user/profile.html', context)
