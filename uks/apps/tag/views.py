from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404

# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView

from .forms import CreateTagForm
from ..branch.models import Branch
from ..commit.models import Commit
from ..repository.models import Repository
from ..tag.models import Tag


class ListTagView(ListView):
    model = Tag
    template_name = 'tag/tag_list.html'

    def get_queryset(self):
        self.repository = get_object_or_404(Repository, id=self.kwargs['id'])
        return Tag.objects.filter(repository=self.repository)

    def get_context_data(self, **kwargs):
        context = super(ListTagView, self).get_context_data(**kwargs)
        context['repository'] = self.repository
        context['show'] = False
        return context


class CreateTagView(LoginRequiredMixin, CreateView):
    model = Tag
    template_name = 'tag/new_tag.html'
    form_class = CreateTagForm

    def form_valid(self, form):
        form.instance.repository = get_object_or_404(Repository, id=self.kwargs['id'])
        branchName = form.cleaned_data['branch']
        branches = Branch.objects.filter(name=branchName)
        branch = branches.get(repository=form.instance.repository)
        commits = Commit.objects.filter(branches__id=branch.id)
        commits = commits.extra(order_by=['-date'])
        commit = commits.first()
        form.instance.commit = commit
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(CreateTagView, self).get_form_kwargs()
        kwargs['repository'] = get_object_or_404(Repository, id=self.kwargs['id'])
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(CreateTagView, self).get_context_data(**kwargs)
        self.repository = get_object_or_404(Repository, id=self.kwargs['id'])
        context['repository'] = self.repository
        return context

    def get_success_url(self):
        return reverse_lazy('repository_tags', kwargs={'id': self.kwargs['id']})


class TagUpdateView(LoginRequiredMixin, UpdateView):
    model = Tag
    form_class = CreateTagForm
    template_name = 'tag/edit_tag.html'

    def get_form_kwargs(self):
        kwargs = super(TagUpdateView, self).get_form_kwargs()
        kwargs['repository'] = get_object_or_404(Repository, id=self.kwargs['id'])
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(TagUpdateView, self).get_context_data(**kwargs)
        self.repository = get_object_or_404(Repository, id=self.kwargs['id'])
        self.tag = get_object_or_404(Tag, id=self.kwargs['pk'])
        context['repository'] = self.repository
        return context

    def get_success_url(self):
        return reverse_lazy('repository_tags', kwargs={'id': self.kwargs['id']})
