from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.views.generic import ListView

from apps.label.models import Label
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
        context['show'] = False
        return context
