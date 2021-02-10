from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView

from apps.project.models import Project
from apps.repository.models import Repository
from apps.issue.models import Issue


class ProjectListView(ListView):
    model = Project
    template_name = 'project/project_list.html'

    def get_queryset(self):
        self.repository = get_object_or_404(Repository, id=self.kwargs['id'])
        return Project.objects.filter(repository=self.repository)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ProjectListView, self).get_context_data(**kwargs)
        context['repository'] = self.repository
        return context


class CreateProjectView(LoginRequiredMixin, CreateView):
    model = Project
    template_name = 'project/project_create.html'
    fields = ['name', 'description']

    def form_valid(self, form):
        form.instance.repository = get_object_or_404(Repository, id=self.kwargs['id'])
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(CreateProjectView, self).get_form_kwargs()
        return kwargs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CreateProjectView, self).get_context_data(**kwargs)
        self.repository = get_object_or_404(Repository, id=self.kwargs['id'])
        context['repository'] = self.repository
        return context

    def get_success_url(self):
        return reverse_lazy('repository_projects', kwargs={'id': self.kwargs['id']})


class ProjectDetailView(DetailView):
    model = Project
    template_name = 'project/project_details.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ProjectDetailView, self).get_context_data(**kwargs)
        self.repository = get_object_or_404(Repository, id=self.kwargs['id'])
        self.project = get_object_or_404(Project, id=self.kwargs['pk'])
        context['repository'] = self.repository
        context['issues'] = Issue.objects.filter(project=self.project)
        return context


def update_issue(self, id):
    issue_id = self.GET.get('id')
    list_id = self.GET.get('list_id')
    issue = Issue.objects.filter(id=issue_id).first()
    issue.change_status(list_id)
    return HttpResponse()


class ProjectUpdateView(UpdateView):
    model = Project
    fields = ['name', 'description']
    template_name_suffix = '_update'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ProjectUpdateView, self).get_context_data(**kwargs)
        self.repository = get_object_or_404(Repository, id=self.kwargs['id'])
        self.project = get_object_or_404(Project, id=self.kwargs['pk'])
        context['repository'] = self.repository
        return context

    def get_success_url(self):
        return reverse_lazy('repository_projects', kwargs={'id': self.kwargs['id']})
