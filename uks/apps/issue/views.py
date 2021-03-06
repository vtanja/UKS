from apps.repository.models import Repository
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from .forms import CreateIssueForm
from .models import Issue
from ..user.models import HistoryItem


class IssuesListView(UserPassesTestMixin, ListView):
    model = Issue

    def get_queryset(self):
        self.repository = get_object_or_404(Repository, id=self.kwargs['repository_id'])
        return Issue.objects.filter(repository=self.repository)

    def get_context_data(self, **kwargs):
        context = super(IssuesListView, self).get_context_data(**kwargs)
        context['repository'] = self.repository
        context['show'] = False
        return context

    def test_func(self):
        repo = get_object_or_404(Repository, id=self.kwargs['repository_id'])
        return repo.test_access(self.request.user)


class IssueDetailView(DetailView):
    model = Issue

    def get_context_data(self, **kwargs):
        self.repository = get_object_or_404(Repository, id=self.kwargs['repository_id'])
        self.changes = HistoryItem.objects.filter(changed_issue_id=self.kwargs['pk'])
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
        form.instance.date_created = timezone.now()
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


def set_message(changed_field, form, original_issue, attribute):
    if original_issue.project:
        return 'changed {} from "{}" to "{}"' \
            .format(attribute, original_issue.project.name if attribute == 'project'
                    else original_issue.milestone.title, form.cleaned_data[changed_field])
    else:
        return 'added this to "{}" {}'.format(form.cleaned_data[changed_field], attribute)


class IssueUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Issue
    form_class = CreateIssueForm

    def form_valid(self, form):
        # Add issue change for actual changes
        original_issue = get_object_or_404(Issue, id=form.instance.id)
        response = super(IssueUpdateView, self).form_valid(form)
        for changed_field in form.changed_data:
            ch = HistoryItem()
            ch.changed_issue = original_issue
            ch.date_changed = timezone.now()
            ch.belongs_to = self.request.user
            if changed_field == 'title':
                ch.message = 'changed title from "{}" to "{}"'\
                    .format(original_issue.title, form.cleaned_data[changed_field])
            elif changed_field == 'description':
                ch.message = 'changed description'
            elif changed_field == 'assignees':
                ch.message = 'changed assignees'
            elif changed_field == 'milestone':
                ch.message = set_message(changed_field, form, original_issue, 'milestone')
            elif changed_field == 'project':
                ch.message = set_message(changed_field, form, original_issue, 'project')
            elif changed_field == 'labels':
                ch.message = 'changed labels'
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
        return reverse_lazy('issue-details', kwargs={'repository_id': self.kwargs['repository_id'], 'pk': self.kwargs['pk']})

    def test_func(self):
        repo = get_object_or_404(Repository, id=self.kwargs['repository_id'])
        return repo.test_access(self.request.user)


@login_required
def close_issue(request, repository_id, pk):
    issue = get_object_or_404(Issue, pk=pk)
    get_object_or_404(Repository, pk=repository_id)
    issue.toggle_issue_close(request.user)
    return redirect(reverse_lazy('issue-details', kwargs={'repository_id': repository_id, 'pk': pk}))
