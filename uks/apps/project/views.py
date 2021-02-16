import json

from apps.issue.models import Issue
from apps.project.models import Project
from apps.repository.models import Repository
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
# Create your views here.
from django.urls import reverse_lazy
from django.views.decorators.cache import never_cache
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name_suffix = '_list'

    def get_queryset(self):
        self.repository = get_object_or_404(Repository, id=self.kwargs['repo_id'])
        return Project.objects.filter(repository=self.repository)

    def get_context_data(self, **kwargs):
        context = super(ProjectListView, self).get_context_data(**kwargs)
        context['repository'] = self.repository
        return context


class CreateProjectView(LoginRequiredMixin, CreateView):
    model = Project
    template_name_suffix = '_create'
    fields = ['name', 'description']

    def form_valid(self, form):
        form.instance.repository = get_object_or_404(Repository, id=self.kwargs['repo_id'])
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(CreateProjectView, self).get_form_kwargs()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(CreateProjectView, self).get_context_data(**kwargs)
        self.repository = get_object_or_404(Repository, id=self.kwargs['repo_id'])
        context['repository'] = self.repository
        return context

    def get_success_url(self):
        return reverse_lazy('repository_projects', kwargs={'repo_id': self.kwargs['repo_id']})


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name_suffix = '_details'

    def get_context_data(self, **kwargs):
        context = super(ProjectDetailView, self).get_context_data(**kwargs)
        self.repository = get_object_or_404(Repository, id=self.kwargs['repo_id'])
        self.project = get_object_or_404(Project, id=self.kwargs['pk'])
        context['repository'] = self.repository
        context['issues'] = Issue.objects.filter(project=self.project)
        issue_dict = {
            "TODO": context['issues'].filter(issue_status='TODO'),
            "ONGOING": context['issues'].filter(issue_status='ONGOING'),
            "DONE": context['issues'].filter(issue_status='DONE')
        }
        context['issue_dict'] = issue_dict
        return context

    @never_cache
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


def update_issue(self, repo_id):
    issue_id = self.GET.get('i_id')
    list_id = self.GET.get('list_id')
    issue = Issue.objects.filter(id=issue_id).first()
    issue.change_status(list_id, self.user)
    payload = {'success': True}
    return HttpResponse(json.dumps(payload), content_type='application/json')


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    fields = ['name', 'description']
    template_name_suffix = '_update'

    def get_context_data(self, **kwargs):
        context = super(ProjectUpdateView, self).get_context_data(**kwargs)
        self.repository = get_object_or_404(Repository, id=self.kwargs['repo_id'])
        self.project = get_object_or_404(Project, id=self.kwargs['pk'])
        context['repository'] = self.repository
        return context

    def get_success_url(self):
        return reverse_lazy('repository_projects', kwargs={'repo_id': self.kwargs['repo_id']})


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name_suffix = '_delete'

    def get_context_data(self, **kwargs):
        context = super(ProjectDeleteView, self).get_context_data(**kwargs)
        self.repository = get_object_or_404(Repository, id=self.kwargs['repo_id'])
        self.project = get_object_or_404(Project, id=self.kwargs['pk'])
        context['repository'] = self.repository
        context['project'] = self.project
        return context

    def get_success_url(self):
        return reverse_lazy('repository_projects', kwargs={'repo_id': self.kwargs['repo_id']})
