from django.contrib import messages
from django.shortcuts import render, redirect
from app.user.forms import ProfileImageUpdateForm
from .forms import RepositoryForm
from security.models import SiteUser


# Create your views here.
def dashboard(request):
    repositories = request.user.siteuser.repositories.all()
    context = {'repositories': repositories}
    return render(request, 'user/dashboard.html', context)


def profile(request):
    context = get_profile_form(request)

    if(context == "redirect"):
        return redirect('profile')

    return render(request, 'user/profile.html', context)

def repos(request):
    context = get_profile_form(request)

    if (context == "redirect"):
        return redirect('repos')

    repositories = request.user.siteuser.repositories.all()
    context['repos'] = repositories

    return render(request, 'user/profile_info.html', context)

def issues(request):
    context = get_profile_form(request)

    if (context == "redirect"):
        return redirect('issues')

    # issues = request.user.siteuser.issues.all()
    # context['issues'] = issues
    context['issues'] = []

    return render(request, 'user/profile_info.html', context)


def get_profile_form(request):
    if request.method == 'POST':
        p_form = ProfileImageUpdateForm(request.POST,
                                        request.FILES,
                                        instance=request.user.siteuser)
        if p_form.is_valid():
            p_form.save()
            messages.success(request, f'You have successfully updated your profile!')
            return "redirect"
    else:
        p_form = ProfileImageUpdateForm(instance=request.user.siteuser)

    context = {
        'p_form': p_form
    }

    return context


def addRepository(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        form = RepositoryForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            print('Forma je validna')
            # form.save()
            repositories = request.user.siteuser.repositories.add(form.save())
            messages.success(request, 'Successfully')
            return redirect('dashboard')
        else:
            print('Forma nije validna')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = RepositoryForm()

    return render(request, 'user/dashboard.html', {'form': form})
