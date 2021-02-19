from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404

# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .forms import CreateLabelForm
from .models import Label
from ..repository.models import Repository


class ListLabelView(UserPassesTestMixin, ListView):
    model = Label
    template_name = 'label/label_list.html'

    def get_queryset(self):
        self.repository = get_object_or_404(Repository, id=self.kwargs['id'])
        return Label.objects.filter(repository=self.repository)

    def get_context_data(self, **kwargs):
        context = super(ListLabelView, self).get_context_data(**kwargs)
        context['repository'] = self.repository
        context['show'] = False
        return context

    def test_func(self):
        repo = get_object_or_404(Repository, id=self.kwargs['id'])
        return repo.test_access(self.request.user)


class CreateLabel(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Label
    template_name = 'label/create_label.html'
    form_class = CreateLabelForm

    def form_valid(self, form):
        form.instance.repository = get_object_or_404(Repository, id=self.kwargs['id'])
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(CreateLabel, self).get_form_kwargs()
        kwargs['repository'] = get_object_or_404(Repository, id=self.kwargs['id'])
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(CreateLabel, self).get_context_data(**kwargs)
        self.repository = get_object_or_404(Repository, id=self.kwargs['id'])
        context['repository'] = self.repository
        return context

    def get_success_url(self):
        return reverse_lazy('repository_labels', kwargs={'id': self.kwargs['id']})

    def test_func(self):
        repo = get_object_or_404(Repository, id=self.kwargs['id'])
        return repo.test_user(self.request.user)


class LabelEdit(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Label
    template_name = 'label/create_label.html'
    form_class = CreateLabelForm

    def form_valid(self, form):
        original_label = self.object
        response = super(LabelEdit, self).form_valid(form)
        for changed_field in form.changed_data:
            label = original_label
            if changed_field == 'name':
                label.name = form.cleaned_data[changed_field]
            elif changed_field == 'description':
                label.description = form.cleaned_data[changed_field]
            elif changed_field == 'color':
                label.color = form.cleaned_data[changed_field]

            label.save()

        return response

    def get_context_data(self, **kwargs):
        self.repository = get_object_or_404(Repository, id=self.kwargs['id'])
        context = super(LabelEdit, self).get_context_data(**kwargs)
        context['repository'] = self.repository
        return context

    def get_form_kwargs(self):
        kwargs = super(LabelEdit, self).get_form_kwargs()
        kwargs['repository'] = get_object_or_404(Repository, id=self.kwargs['id'])
        return kwargs

    def get_success_url(self):
        return reverse_lazy('repository_labels', kwargs={'id': self.kwargs['id']})

    def test_func(self):
        repo = get_object_or_404(Repository, id=self.kwargs['id'])
        return repo.test_user(self.request.user)


class LabelDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Label
    template_name = 'label/delete_label.html'

    def form_valid(self):
        label = get_object_or_404(Label, id=self.kwargs['pk'])
        Label.objects.filter(id=label.id).delete()

    def get_context_data(self, **kwargs):
        self.repository = get_object_or_404(Repository, id=self.kwargs['id'])
        context = super(LabelDeleteView, self).get_context_data(**kwargs)
        context['repository'] = self.repository
        return context

    def get_form_kwargs(self):
        kwargs = super(LabelDeleteView, self).get_form_kwargs()
        kwargs['repository'] = get_object_or_404(Repository, id=self.kwargs['id'])
        return kwargs

    def get_success_url(self):
        return reverse_lazy('repository_labels', kwargs={'id': self.kwargs['id']})

    def test_func(self):
        repo = get_object_or_404(Repository, id=self.kwargs['id'])
        return repo.test_user(self.request.user)
