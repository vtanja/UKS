from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView

from apps.project.models import Project
from apps.repository.models import Repository


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
