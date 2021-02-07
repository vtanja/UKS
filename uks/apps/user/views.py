import datetime

from django.db.models.functions import Coalesce
from django.shortcuts import render, redirect
from apps.repository.forms import RepositoryForm
from django.contrib import messages
from apps.repository.models import Repository
from apps.user.forms import ProfileImageUpdateForm


# Create your views here.
from apps.user.models import UserHistoryItem


def dashboard(request):
    repositories = request.user.siteuser.repositories.all()
    history = request.user.siteuser.userhistoryitem_set.all().order_by('-dateChanged')
    context = {}
    context['repositories'] = repositories
    context['history'] = history
    return render(request, 'user/dashboard.html', context)


def profile(request):
    context = get_profile_form(request)

    if(context == "redirect"):
        return redirect('profile')

    repositories = request.user.siteuser.repositories.all()
    context['repos'] = repositories
    context['issues'] = []

    return render(request, 'user/profile.html', context)


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


def add_repository(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        form = RepositoryForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            print('Forma je validna')
            # form.save()
            request.user.siteuser.repositories.add(form.save())

            change = UserHistoryItem()
            change.dateChanged = datetime.datetime.now()
            change.belongsTo = request.user.siteuser
            change.message = 'added new repository'
            change.save()

            messages.success(request, 'Successfully added new repository!')
            return redirect('dashboard')
        else:
            print('Forma nije validna')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = RepositoryForm()

    return render(request, 'user/dashboard.html', {'form': form})


def detail(request, id):
    repositories = request.user.siteuser.repositories.all()
    repository = Repository.objects.get(id=id)
    print(repository.name)
    context = {'repositories': repositories, 'repository': repository}
    return render(request, '../repository/templates/repoDetail.html', context)
