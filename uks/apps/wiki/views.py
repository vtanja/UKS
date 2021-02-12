import logging

from django.shortcuts import  get_object_or_404

# Create your views here.
from django.views.generic import ListView, DetailView

from apps.repository.models import Repository
from apps.wiki.models import Wiki

logger = logging.getLogger('django')

class WikiListView(ListView):
    model = Wiki
    template_name = 'wiki/wiki_list.html'

    def get_queryset(self):
        logger.info('Getting current repository!')
        self.repository = get_object_or_404(Repository, id=self.kwargs['id'])

    def get_context_data(self, **kwargs):
        context = super(WikiListView, self).get_context_data(**kwargs)
        wikis = Wiki.objects.filter(repository_id=self.repository.id)
        logger.info('Initializing context!')
        context['repository'] = self.repository
        context['wikis'] = wikis
        context['show'] = False
        return context


class WikiDetailPage(DetailView):
    model = Wiki
    template_name = 'wiki/wiki_detail.html'

    def get_context_data(self, **kwargs):
        context = super(WikiDetailPage, self).get_context_data(**kwargs)
        logger.info('Retrieving wiki that belong to repository with id: %s', self.kwargs['id'])
        context['wikis'] = Wiki.objects.filter(repository_id=self.kwargs['id'])
        context['repository'] = Repository.objects.get(id=self.kwargs['id'])
        return context