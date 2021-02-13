from apps.repository.models import Repository
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from .forms import CreateIssueForm
from .models import Issue, IssueChange


class IssuesListView(ListView):
    model = Issue

    def get_queryset(self):
        self.repository = get_object_or_404(Repository, id=self.kwargs['repository_id'])
        return Issue.objects.filter(repository=self.repository)

    def get_context_data(self, **kwargs):
        context = super(IssuesListView, self).get_context_data(**kwargs)
        context['repository'] = self.repository
        context['show'] = False
        return context


class IssueDetailView(DetailView):
    model = Issue

    def get_context_data(self, **kwargs):
        self.repository = get_object_or_404(Repository, id=self.kwargs['repository_id'])
        self.changes = IssueChange.objects.filter(issue=self.kwargs['pk'])
        context = super(IssueDetailView, self).get_context_data(**kwargs)
        context['repository'] = self.repository
        context['changes'] = self.changes
        return context


class CreateIssueView(LoginRequiredMixin, CreateView):
    model = Issue
    form_class = CreateIssueForm

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.repository = get_object_or_404(Repository, id=self.kwargs['repository_id'])
        form.instance.issue_status = Issue.IssueStatus.TODO
        form.instance.closed = False
        return super(CreateIssueView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        self.repository = get_object_or_404(Repository, id=self.kwargs['repository_id'])

        context = super(CreateIssueView, self).get_context_data(**kwargs)
        context['repository'] = self.repository
        return context

    def get_form_kwargs(self):
        kwargs = super(CreateIssueView, self).get_form_kwargs()
        kwargs['repository'] = get_object_or_404(Repository, id=self.kwargs['repository_id'])
        return kwargs

    def get_success_url(self):
        return reverse_lazy('repository-issues', kwargs={'repository_id': self.kwargs['repository_id']})


class IssueUpdateView(LoginRequiredMixin, UpdateView):
    model = Issue
    form_class = CreateIssueForm

    def form_valid(self, form):
        # Add issue change for actual changes
        original_issue = self.object
        response = super(IssueUpdateView, self).form_valid(form)
        for changed_field in form.changed_data:
            ch = IssueChange()
            ch.issue = original_issue
            ch.date = timezone.now()
            if changed_field == 'title':
                ch.message = '{} changed title from {} to {}'.format(self.request.user.username, original_issue.title,
                                                                     form.cleaned_data[changed_field])
            elif changed_field == 'description':
                ch.message = self.request.user.username + ' changed description'
            elif changed_field == 'assignees':
                ch.message = '{} changed assignees'.format(self.request.user.username)
            elif changed_field == 'milestone':
                ch.message = '{} changed milestone from {} to {}'.format(self.request.user.username, original_issue.milestone.title,
                                                                         form.cleaned_data[changed_field])
            ch.save()

        return response

    def get_context_data(self, **kwargs):
        self.repository = get_object_or_404(Repository, id=self.kwargs['repository_id'])
        context = super(IssueUpdateView, self).get_context_data(**kwargs)
        context['repository'] = self.repository
        return context

    def get_form_kwargs(self):
        kwargs = super(IssueUpdateView, self).get_form_kwargs()
        kwargs['repository'] = get_object_or_404(Repository, id=self.kwargs['repository_id'])
        return kwargs

    def get_success_url(self):
        if self.request.path.find('edit') != -1:
            return reverse_lazy('issue-details', kwargs={'repository_id': self.kwargs['repository_id'], 'pk': self.kwargs['pk']})
        return reverse_lazy('repository-issues', kwargs={'repository_id': self.kwargs['repository_id']})


@login_required
def close_issue(request, repository_id, pk):
    issue = get_object_or_404(Issue, pk=pk)
    get_object_or_404(Repository, pk=repository_id)
    issue.toggle_issue_close()
    return redirect(reverse_lazy('issue-details', kwargs={'repository_id': repository_id, 'pk': pk}))
