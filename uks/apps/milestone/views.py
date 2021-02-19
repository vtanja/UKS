import logging
from apps.issue.models import Issue
from apps.milestone.forms import CreateMilestoneForm
from apps.milestone.models import Milestone
from apps.repository.models import Repository
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView


logger = logging.getLogger('django')


def get_repo(repo_id):
    repo = get_object_or_404(Repository, id=repo_id)
    return repo


class MilestoneListView(UserPassesTestMixin, ListView):
    model = Milestone
    template_name = 'milestone/milestone_list.html'

    def get_queryset(self):
        self.repository = get_object_or_404(Repository, id=self.kwargs['repo_id'])
        return Milestone.objects.filter(repository=self.repository)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(MilestoneListView, self).get_context_data(**kwargs)
        context['repository'] = self.repository
        context['show'] = False
        logger.info('Milestone list view context initialized')
        return context

    def test_func(self):
        repo = get_object_or_404(Repository, id=self.kwargs['repo_id'])
        return repo.test_access(self.request.user)


class CreateMilestoneView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Milestone
    template_name = 'milestone/milestone_create.html'
    form_class = CreateMilestoneForm

    def form_valid(self, form):
        form.instance.repository = get_object_or_404(Repository, id=self.kwargs['repo_id'])
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(CreateMilestoneView, self).get_form_kwargs()
        kwargs['repository'] = get_object_or_404(Repository, id=self.kwargs['repo_id'])
        return kwargs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CreateMilestoneView, self).get_context_data(**kwargs)
        self.repository = get_object_or_404(Repository, id=self.kwargs['repo_id'])
        context['repository'] = self.repository
        logger.info('Milestone create view context initialized')
        return context

    def get_success_url(self):
        logger.info('Milestone successfully added to repository with id {}'.format(self.kwargs['repo_id']))
        return reverse_lazy('repository_milestones', kwargs={'repo_id': self.kwargs['repo_id']})

    def test_func(self):
        repo = get_repo(self.kwargs['repo_id'])
        return repo.test_user(self.request.user)


class MilestoneDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Milestone
    template_name = 'milestone/milestone_detail.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(MilestoneDetailView, self).get_context_data(**kwargs)
        self.repository = get_object_or_404(Repository, id=self.kwargs['repo_id'])
        self.milestone = get_object_or_404(Milestone, id=self.kwargs['pk'])
        context['repository'] = self.repository
        context['issues'] = Issue.objects.filter(milestone=self.milestone)
        logger.info('Milestone detail view context initialized')
        return context

    def test_func(self):
        repo = get_object_or_404(Repository, id=self.kwargs['repo_id'])
        return repo.test_access(self.request.user)


class MilestoneUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Milestone
    form_class = CreateMilestoneForm
    template_name_suffix = '_update'

    def get_form_kwargs(self):
        kwargs = super(MilestoneUpdateView, self).get_form_kwargs()
        kwargs['repository'] = get_object_or_404(Repository, id=self.kwargs['repo_id'])
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(MilestoneUpdateView, self).get_context_data(**kwargs)
        self.repository = get_object_or_404(Repository, id=self.kwargs['repo_id'])
        self.milestone = get_object_or_404(Milestone, id=self.kwargs['pk'])
        context['repository'] = self.repository
        logger.info('Milestone update view context initialized')
        return context

    def get_success_url(self):
        logger.info('Milestone with id {} successfully updated'.format(self.kwargs['pk']))
        return reverse_lazy('repository_milestones', kwargs={'repo_id': self.kwargs['repo_id']})

    def test_func(self):
        repo = get_repo(self.kwargs['repo_id'])
        return repo.test_user(self.request.user)


@login_required
def close_milestone(request, repo_id, pk):
    repository = get_object_or_404(Repository, id=repo_id)
    if not repository.test_user(request.user):
        logger.warning('User does not have permission.')
        messages.error(request, 'User does not have permission.')
        return redirect(reverse_lazy('repository_milestones', kwargs={'repo_id': repo_id}))

    milestone = get_object_or_404(Milestone, pk=pk)
    milestone.toggle_milestone_close()
    if milestone.closed:
        logger.info('Milestone {} successfully closed'.format(milestone))
    else:
        logger.info('Milestone {} successfully reopened'.format(milestone))
    return redirect(reverse_lazy('milestone_details', kwargs={'repo_id': repo_id, 'pk': pk}))


class MilestoneDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Milestone
    template_name_suffix = '_delete'

    def get_context_data(self, **kwargs):
        context = super(MilestoneDeleteView, self).get_context_data(**kwargs)
        self.repository = get_object_or_404(Repository, id=self.kwargs['repo_id'])
        self.milestone = get_object_or_404(Milestone, id=self.kwargs['pk'])
        context['repository'] = self.repository
        logger.info('Milestone delete view context initialized')
        return context

    def get_success_url(self):
        logger.info('Milestone with id {} succesfully deleted'.format(self.kwargs['pk']))
        return reverse_lazy('repository_milestones', kwargs={'repo_id': self.kwargs['repo_id']})

    def test_func(self):
        repo = get_repo(self.kwargs['repo_id'])
        return repo.test_user(self.request.user)
