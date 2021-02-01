from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView
from .models import Issue
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

        context = super(IssueDetailView, self).get_context_data(**kwargs)
        context['repository'] = self.repository
        return context


class CreateIssueView(LoginRequiredMixin, CreateView):
    model = Issue
    fields = ['title', 'description']

    def form_valid(self, form):
        form.instance.site_user = get_object_or_404(SiteUser, user=self.request.user)
        form.instance.repository = get_object_or_404(Repository, id=self.kwargs['id'])
        form.instance.issue_status = Issue.IssueStatus.TODO
        return super().form_valid(form)

    def get_context_data(self, *, object_list=None, **kwargs):
        self.repository = get_object_or_404(Repository, id=self.kwargs['id'])

        context = super(CreateIssueView, self).get_context_data(**kwargs)
        context['repository'] = self.repository
        return context

    def get_success_url(self):
        return reverse_lazy('repository_issues', kwargs={'id': self.kwargs['id']})
