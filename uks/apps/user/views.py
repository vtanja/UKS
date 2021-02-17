import logging

from apps.issue.models import Issue
from apps.repository.forms import RepositoryForm
from apps.repository.models import Repository
from apps.user.forms import ProfileImageUpdateForm
from apps.user.models import HistoryItem
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views.generic import ListView
from security.models import SiteUser

logger = logging.getLogger('django')

@login_required
def dashboard(request):
    form = RepositoryForm()
    logger.info('User dashboard entered!')
    logger.info('Getting all repositories of user initialized!')
    repositories = all_users_repositories(request)
    logger.info('Getting user activity initialized!')
    history = HistoryItem.objects.filter(belongs_to=request.user, changed_issue__isnull=True).order_by('-date_changed')
    context = {'repositories': repositories, 'history': history, 'form': form}
    return render(request, 'user/dashboard.html', context)


@login_required
def all_users_repositories(request):
    repositories = Repository.objects.filter(
        Q(owner=request.user) | Q(collaborators__username__in=[str(request.user)])
    ).distinct()
    return repositories


@login_required
def profile(request, pk):
    user = SiteUser.objects.get(user_id=pk)
    logger.info('User profile entered!')
    ret_val = get_profile_form(request, user)

    context = {}

    logger.info('Getting all repositories of user initialized!')
    repositories = all_users_repositories(request)
    context['repos'] = repositories
    logger.info('Getting all issues of user initialized!')
    context['issues'] = Issue.objects.filter(created_by=request.user, closed=False)

    if ret_val == "redirect":
        return redirect('profile', pk)
    else:
        context['p_form'] = ret_val

    return render(request, 'user/profile.html', context)


@login_required
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

    return p_form


class AllIssuesListView(LoginRequiredMixin, ListView):
    model = Issue
    template_name = 'user/issue_list.html'

    def get_queryset(self):
        return Issue.objects.filter(Q(assignees__in=[self.request.user]) | Q(created_by=self.request.user)) \
            .filter(closed=False)


class MyPasswordResetView(LoginRequiredMixin, PasswordResetView):
    template_name = 'user/password_reset.html'


class MyPasswordResetDoneView(LoginRequiredMixin, PasswordResetDoneView):
    template_name = 'user/password_reset_done.html'


class MyPasswordResetConfirmView(LoginRequiredMixin, PasswordResetConfirmView):
    template_name = 'user/password_reset_confirm.html'


class MyPasswordResetCompleteView(LoginRequiredMixin, PasswordResetCompleteView):
    template_name = 'user/password_reset_complete.html'
