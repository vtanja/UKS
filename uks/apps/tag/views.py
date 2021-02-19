from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView

from .forms import CreateTagForm
from ..commit.models import Commit
from ..repository.models import Repository
from ..tag.models import Tag


class ListTagView(UserPassesTestMixin, ListView):
    model = Tag
    template_name = 'tag/tag_list.html'

    def get_queryset(self):
        self.repository = get_object_or_404(Repository, id=self.kwargs['id'])
        return Tag.objects.filter(branch__repository=self.repository)

    def get_context_data(self, **kwargs):
        context = super(ListTagView, self).get_context_data(**kwargs)
        context['repository'] = self.repository
        context['show'] = False
        return context

    def test_func(self):
        repo = get_object_or_404(Repository, id=self.kwargs['repo_id'])
        return repo.test_access(self.request.user)


class CreateTagView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Tag
    template_name = 'tag/new_tag.html'
    form_class = CreateTagForm

    def form_valid(self, form):
        branch_name = form.cleaned_data['branch']
        commits = Commit.objects.filter(branches__id=branch_name.id)
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

    def test_func(self):
        repo = get_object_or_404(Repository, id=self.kwargs['repo_id'])
        return repo.test_user(self.request.user)


class TagUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Tag
    form_class = CreateTagForm
    template_name = 'tag/edit_tag.html'

    def form_valid(self, form):
        branch_name = form.cleaned_data['branch']
        commits = Commit.objects.filter(branches__id=branch_name.id)
        commits = commits.extra(order_by=['-date'])
        commit = commits.first()
        form.instance.commit = commit
        return super().form_valid(form)

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

    def test_func(self):
        repo = get_object_or_404(Repository, id=self.kwargs['repo_id'])
        return repo.test_user(self.request.user)
