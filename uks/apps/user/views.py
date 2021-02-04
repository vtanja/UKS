import datetime

from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import ListView

from apps.repository.forms import RepositoryForm
from apps.user.forms import ProfileImageUpdateForm
from apps.repository.models import Repository
from apps.issue.models import Issue
from apps.user.models import UserHistoryItem


def dashboard(request):
    repositories = all_users_repositories(request)
    history = request.user.siteuser.userhistoryitem_set.all().order_by('-dateChanged')
    context = {'repositories': repositories, 'history': history}
    return render(request, 'user/dashboard.html', context)


def all_users_repositories(request):
    repositories = Repository.objects.filter(
        Q(owner=request.user) | Q(collaborators__username__in=[str(request.user)])
    ).distinct()
    return repositories


def profile(request):
    context = get_profile_form(request)

    if (context == "redirect"):
        return redirect('profile')

    repositories = all_users_repositories(request)
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


def addRepository(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        form = RepositoryForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            print('Forma je validna')
            # form.save()
            repositories = all_users_repositories(request)

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
    repositories = all_users_repositories()
    repository = Repository.objects.get(id=id)
    print(repository.name)
    context = {'repositories': repositories, 'repository': repository}
    return render(request, '../repository/templates/repoDetail.html', context)


class AllIssuesListView(ListView):
    model = Issue
    template_name = 'user/issue_list.html'
