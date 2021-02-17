from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.views.generic import ListView

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