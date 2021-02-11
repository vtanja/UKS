import datetime
import logging

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render

# Create your views here.
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from apps.repository.models import Repository
from apps.user.models import UserHistoryItem
from apps.wiki.forms import CreateWikiForm
from apps.wiki.models import Wiki, WikiHistoryItem

logger = logging.getLogger('django')


class WikiListView(ListView):
    model = Wiki
    template_name = 'wiki/wiki_list.html'

    def get(self, request, *args, **kwargs):
        repo = Repository.objects.get(id=self.kwargs['id'])
        if repo.wiki_set.count() > 0:
            return redirect(reverse('wiki-details', kwargs={'id': repo.id, 'pk': repo.wiki_set.first().id}))
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        logger.info('Getting current repository!')
        self.repository = get_object_or_404(Repository, id=self.kwargs['id'])

    def get_context_data(self, *, object_list=None, **kwargs):
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
        change = UserHistoryItem()
        change.dateChanged = datetime.datetime.now()
        change.belongsTo = self.request.user
        change.message = 'created new wiki page'
        change.save()

        logger.info('Added wiki history item!')
        wiki_change = WikiHistoryItem()
        wiki_change.dateChanged = datetime.datetime.now()
        wiki_change.belongsTo = self.request.user
        wiki_change.message = 'created new wiki page'
        wiki_change.save()

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


class WikiUpdateView(UpdateView):
    model = Wiki
    form_class = CreateWikiForm

    def form_valid(self, form):
        # Add issue change for actual changes
        logger.log('Wiki page [%s] change initializes!', self.object.title)
        response = super(WikiUpdateView, self).form_valid(form)
        logger.log('Creating wiki history item!')
        change = WikiHistoryItem()
        change.belongsTo = self.request.user
        change.message = 'changed wiki page'
        change.dateChanged = datetime.datetime.now()
        change.save()
        logger.log('Wiki page [%s] change done!', self.object.title)
        return response

    def get_context_data(self, *, object_list=None, **kwargs):
        self.repository = get_object_or_404(Repository, id=self.kwargs['id'])
        context = super(WikiUpdateView, self).get_context_data(**kwargs)
        context['repository'] = self.repository
        return context

    def get_form_kwargs(self):
        kwargs = super(WikiUpdateView, self).get_form_kwargs()
        kwargs['repository'] = get_object_or_404(Repository, id=self.kwargs['id'])
        return kwargs

    def get_success_url(self):
        return reverse_lazy('wiki-details', kwargs={'id': self.kwargs['id'], 'pk': self.kwargs['pk']})
