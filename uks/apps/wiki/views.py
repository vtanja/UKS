import logging

from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.views.generic import ListView

from apps.repository.models import Repository
from apps.wiki.models import Wiki

logger = logging.getLogger('django')

class WikiListView(ListView):
    model = Wiki
    template_name = 'wiki/overview.html'

    def get_queryset(self):
        logger.info('Getting current repository!')
        self.repository = get_object_or_404(Repository, id=self.kwargs['id'])

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(WikiListView, self).get_context_data(**kwargs)
        logger.info('Initializing context!')
        context['repository'] = self.repository
        # context['p_form'] = self.p_form
        context['show'] = False
        return context