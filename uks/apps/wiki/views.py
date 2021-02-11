import datetime
import logging

from django.shortcuts import get_object_or_404
# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView

from apps.repository.models import Repository
from apps.user.models import HistoryItem
from apps.wiki.forms import CreateWikiForm
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

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(WikiDetailPage, self).get_context_data(**kwargs)
        logger.info('Retrieving wiki that belong to repository with id: %s', self.kwargs['id'])
        context['wikis'] = Wiki.objects.filter(repository_id=self.kwargs['id'])
        context['repository'] = Repository.objects.get(id=self.kwargs['id'])
        return context


class CreateWikiView(CreateView):
    model = Wiki
    form_class = CreateWikiForm
    template_name = 'wiki/wiki_add.html'

    def form_valid(self, form):
        logger.info('Setting repository to wiki!')
        form.instance.repository = get_object_or_404(Repository, id=self.kwargs['id'])
        logger.info('Wiki page created!')

        logger.info('Added user history item!')
        change = HistoryItem()
        change.dateChanged = datetime.datetime.now()
        change.belongsTo = self.request.user
        change.message = 'created new wiki page'
        change.save()

        return super(CreateWikiView, self).form_valid(form)

    def get_context_data(self, *, object_list=None, **kwargs):
        logger.info('Initializing context')
        self.repository = get_object_or_404(Repository, id=self.kwargs['id'])
        context = super(CreateWikiView, self).get_context_data(**kwargs)
        context['repository'] = self.repository
        logger.info('Context initialized!')
        return context

    def get_form_kwargs(self):
        kwargs = super(CreateWikiView, self).get_form_kwargs()
        kwargs['repository'] = get_object_or_404(Repository, id=self.kwargs['id'])
        return kwargs

    def get_success_url(self):
        return reverse_lazy('wiki-overview', kwargs={'id': self.kwargs['id']})