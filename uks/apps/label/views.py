from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView

from .forms import CreateLabelForm
from .models import Label
from apps.repository.models import Repository


class ListLabelView(ListView):
    model = Label
    template_name = 'label_list.html'

    def get_queryset(self):
        self.repository = get_object_or_404(Repository, id=self.kwargs['id'])
        return Label.objects.filter(repository=self.repository)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ListLabelView, self).get_context_data(**kwargs)
        context['repository'] = self.repository
        return context


class CreateLabel(LoginRequiredMixin, CreateView):
    model = Label
    template_name = 'create_label.html'
    form_class = CreateLabelForm

    def form_valid(self, form):
        form.instance.repository = get_object_or_404(Repository, id=self.kwargs['id'])
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(CreateLabel, self).get_form_kwargs()
        kwargs['repository'] = get_object_or_404(Repository, id=self.kwargs['id'])
        return kwargs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CreateLabel, self).get_context_data(**kwargs)
        self.repository = get_object_or_404(Repository, id=self.kwargs['id'])
        context['repository'] = self.repository
        return context

    def get_success_url(self):
        return reverse_lazy('repository_labels', kwargs={'id': self.kwargs['id']})
