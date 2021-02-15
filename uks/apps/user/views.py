import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import ListView

from apps.repository.forms import RepositoryForm
from apps.user.forms import ProfileImageUpdateForm
from apps.repository.models import Repository
from apps.issue.models import Issue
from security.models import SiteUser

logger = logging.getLogger('django')

def dashboard(request):
    form = RepositoryForm()
    logger.info('User dashboard entered!')
    logger.info('Getting all repositories of user initialized!')
    repositories = all_users_repositories(request)
    logger.info('Getting user activity initialized!')
    history = request.user.historyitem_set.all().order_by('-dateChanged')
    context = {'repositories': repositories, 'history': history, 'form': form}
    return render(request, 'user/dashboard.html', context)


def all_users_repositories(request):
    repositories = Repository.objects.filter(
        Q(owner=request.user) | Q(collaborators__username__in=[str(request.user)])
    ).distinct()
    return repositories


def profile(request, pk):
    user = SiteUser.objects.get(user_id=pk)
    logger.info('User profile entered!')
    context = get_profile_form(request, user)

    if (context == "redirect"):
        return redirect('profile')

    logger.info('Getting all repositories of user initialized!')
    repositories = all_users_repositories(request)
    context['repos'] = repositories
    logger.info('Getting all issues of user initialized!')
    context['issues'] = Issue.objects.filter(created_by=request.user, closed=False)

    return render(request, 'user/profile.html', context)


def get_profile_form(request, user):
    if request.method == 'POST':
        p_form = ProfileImageUpdateForm(request.POST,
                                        request.FILES,
                                        instance=user)
        if p_form.is_valid():
            logger.info('User profile form is valid!')
            p_form.save()
            logger.info('Successfully updating profile!')
            messages.success(request, f'You have successfully updated your profile!')
            return "redirect"
    else:
        p_form = ProfileImageUpdateForm(instance=user)

    context = {
        'p_form': p_form
    }

    return context


class AllIssuesListView(LoginRequiredMixin, ListView):
    model = Issue
    template_name = 'user/issue_list.html'

    def get_queryset(self):
        return Issue.objects.filter(Q(assignees__in=[self.request.user]) | Q(created_by=self.request.user))\
            .filter(closed=False)
