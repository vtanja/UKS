from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, DetailView, UpdateView

# Create your views here.
from django.http import HttpResponse

from apps.milestone.models import Milestone
from apps.repository.models import Repository
from apps.milestone.forms import CreateMilestoneForm
from apps.issue.models import Issue


def index(request):
    return HttpResponse("Hello, world. You're at the milestones index page.")


class MilestoneListView(ListView):
    model = Milestone
    template_name = 'milestone/milestone_list.html'

    def get_queryset(self):
        self.repository = get_object_or_404(Repository, id=self.kwargs['repo_id'])
        return Milestone.objects.filter(repository=self.repository)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(MilestoneListView, self).get_context_data(**kwargs)
        context['repository'] = self.repository
        context['show'] = False
        return context


class CreateMilestoneView(LoginRequiredMixin, CreateView):
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
        return context

    def get_success_url(self):
        return reverse_lazy('repository_milestones', kwargs={'repo_id': self.kwargs['repo_id']})


class MilestoneDetailView(DetailView):
    model = Milestone
    template_name = 'milestone/milestone_detail.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(MilestoneDetailView, self).get_context_data(**kwargs)
        self.repository = get_object_or_404(Repository, id=self.kwargs['repo_id'])
        self.milestone = get_object_or_404(Milestone, id=self.kwargs['pk'])
        context['repository'] = self.repository
        context['issues'] = Issue.objects.filter(milestone=self.milestone)
        return context


class MilestoneUpdateView(UpdateView):
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
        return context

    def get_success_url(self):
        return reverse_lazy('repository_milestones', kwargs={'repo_id': self.kwargs['repo_id']})


@login_required
def close_milestone(request, repo_id, pk):
    milestone = get_object_or_404(Milestone, pk=pk)
    repository = get_object_or_404(Repository, pk=repo_id)
    milestone.toggle_milestone_close()
    return redirect(reverse_lazy('repository_milestones', kwargs={'repo_id': repo_id}))
