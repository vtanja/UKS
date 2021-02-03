from django.utils import timezone
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from .models import Issue, IssueChange
from apps.repository.models import Repository
from security.models import SiteUser


class IssuesListView(ListView):
    model = Issue

    def get_queryset(self):
        self.repository = get_object_or_404(Repository, id=self.kwargs['id'])
        return Issue.objects.filter(repository=self.repository)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(IssuesListView, self).get_context_data(**kwargs)
        context['repository'] = self.repository
        return context


class IssueDetailView(DetailView):
    model = Issue

    def get_context_data(self, *, object_list=None, **kwargs):
        self.repository = get_object_or_404(Repository, id=self.kwargs['id'])
        self.changes = IssueChange.objects.filter(issue=self.kwargs['pk'])
        context = super(IssueDetailView, self).get_context_data(**kwargs)
        context['repository'] = self.repository
        context['changes'] = self.changes
        return context


class CreateIssueView(LoginRequiredMixin, CreateView):
    model = Issue
    fields = ['title', 'description']

    def form_valid(self, form):
        form.instance.site_user = get_object_or_404(SiteUser, user=self.request.user)
        form.instance.repository = get_object_or_404(Repository, id=self.kwargs['id'])
        form.instance.issue_status = Issue.IssueStatus.TODO
        return super(CreateIssueView, self).form_valid(form)

    def get_context_data(self, *, object_list=None, **kwargs):
        self.repository = get_object_or_404(Repository, id=self.kwargs['id'])

        context = super(CreateIssueView, self).get_context_data(**kwargs)
        context['repository'] = self.repository
        return context

    def get_success_url(self):
        return reverse_lazy('repository-issues', kwargs={'id': self.kwargs['id']})


class IssueUpdateView(LoginRequiredMixin, UpdateView):
    model = Issue
    fields = ['title', 'description']

    def form_valid(self, form):
        # Add issue change for actual changes
        original_issue = get_object_or_404(Issue, id=form.instance.id)
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
            ch.save()

        return response

    def get_context_data(self, *, object_list=None, **kwargs):
        self.repository = get_object_or_404(Repository, id=self.kwargs['id'])
        context = super(IssueUpdateView, self).get_context_data(**kwargs)
        context['repository'] = self.repository
        return context

    def get_success_url(self):
        if self.request.path.find('edit') != -1:
            return reverse_lazy('issue-details', kwargs={'id': self.kwargs['id'], 'pk': self.kwargs['pk']})
        return reverse_lazy('repository-issues', kwargs={'id': self.kwargs['id']})
