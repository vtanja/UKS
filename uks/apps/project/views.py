from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.views.generic import ListView

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
