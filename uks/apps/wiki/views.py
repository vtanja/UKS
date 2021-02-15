import logging
from apps.repository.models import Repository
from apps.user.models import HistoryItem
from apps.wiki.forms import CreateWikiForm
from apps.wiki.models import Wiki
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

logger = logging.getLogger('django')


def add_history_item(user, message):
    change = HistoryItem()
    change.dateChanged = timezone.now()
    change.belongsTo = user
    change.message = message
    return change

class WikiListView(LoginRequiredMixin, ListView):
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

    def get_context_data(self, **kwargs):
        context = super(WikiListView, self).get_context_data(**kwargs)
        wikis = Wiki.objects.filter(repository_id=self.repository.id)
        logger.info('Initializing context!')
        context['repository'] = self.repository
        context['wikis'] = wikis
        context['show'] = False
        return context


class WikiDetailPage(LoginRequiredMixin, DetailView):
    model = Wiki
    template_name = 'wiki/wiki_detail.html'

    def get_context_data(self, **kwargs):
        context = super(WikiDetailPage, self).get_context_data(**kwargs)
        logger.info('Retrieving wiki that belong to repository with id: %s', self.kwargs['id'])
        context['wikis'] = Wiki.objects.filter(repository_id=self.kwargs['id'])
        context['repository'] = Repository.objects.get(id=self.kwargs['id'])
        context['show'] = False
        return context


class CreateWikiView(LoginRequiredMixin, CreateView):
    model = Wiki
    form_class = CreateWikiForm
    template_name = 'wiki/wiki_form.html'

    def form_valid(self, form):
        logger.info('Setting repository to wiki!')
        form.instance.repository = get_object_or_404(Repository, id=self.kwargs['id'])
        logger.info('Wiki page created!')

        logger.info('Added user history item!')
        self.change = add_history_item(self.request.user, 'created new ')
        self.change.save()

        return super(CreateWikiView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        logger.info('Initializing context')
        self.repository = get_object_or_404(Repository, id=self.kwargs['id'])
        context = super(CreateWikiView, self).get_context_data(**kwargs)
        context['repository'] = self.repository
        context['wikis'] = Wiki.objects.filter(repository=self.repository)
        context['show'] = False
        logger.info('Context initialized!')
        return context

    def get_form_kwargs(self):
        kwargs = super(CreateWikiView, self).get_form_kwargs()
        kwargs['repository'] = get_object_or_404(Repository, id=self.kwargs['id'])
        return kwargs

    def get_success_url(self):
        wiki = get_object_or_404(Wiki, id=self.object.id)
        self.change.changed_wiki_object = wiki
        self.change.save()
        return reverse_lazy('wiki-overview', kwargs={'id': self.kwargs['id']})


class WikiUpdateView(LoginRequiredMixin, UpdateView):
    model = Wiki
    form_class = CreateWikiForm

    def form_valid(self, form):
        # Add issue change for actual changes
        logger.info('Wiki page [%s] change initializes!', self.object.title)
        response = super(WikiUpdateView, self).form_valid(form)
        logger.info('Creating wiki history item!')

        logger.info('Wiki page [%s] change done!', self.object.title)
        return response

    def get_context_data(self, **kwargs):
        self.repository = get_object_or_404(Repository, id=self.kwargs['id'])
        context = super(WikiUpdateView, self).get_context_data(**kwargs)
        context['repository'] = self.repository
        context['wikis'] = Wiki.objects.filter(repository=self.repository)
        context['show'] = False
        return context

    def get_form_kwargs(self):
        kwargs = super(WikiUpdateView, self).get_form_kwargs()
        kwargs['repository'] = get_object_or_404(Repository, id=self.kwargs['id'])
        return kwargs

    def get_success_url(self):
        change = add_history_item(self.request.user, 'changed ')
        wiki = get_object_or_404(Wiki, id=self.object.id)
        change.changed_wiki_object = wiki
        change.save()
        return reverse_lazy('wiki-details', kwargs={'id': self.kwargs['id'], 'pk': self.kwargs['pk']})


class WikiDeleteView(LoginRequiredMixin, DeleteView):
    model = Wiki

    def get_success_url(self):
        change = add_history_item(self.request.user, 'deleted wiki page')
        wiki = get_object_or_404(Wiki, id=self.object.id)
        change.changed_wiki_object = wiki
        change.save()
        logger.info('Wiki [%s] has been deleted successfully!', self.kwargs['pk'])
        logger.info('Routing to all wikis after deleting wiki!')
        return reverse_lazy('wiki-overview', kwargs={'id': self.kwargs['id']})


class HistoryListView(LoginRequiredMixin, ListView):
    model = HistoryItem
    template_name = 'wiki/wiki_history.html'

    def get_queryset(self):
        logger.info('Getting current repository!')
        self.repository = get_object_or_404(Repository, id=self.kwargs['id'])
        self.wiki = get_object_or_404(Wiki, id=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super(HistoryListView, self).get_context_data(**kwargs)
        history = HistoryItem.objects.filter(changed_wiki_object_id=self.wiki.id)
        logger.info('Initializing context!')
        context['repository'] = self.repository
        context['wikis'] = Wiki.objects.filter(repository=self.repository)
        context['show'] = False
        context['history'] = history
        context['wiki'] = self.wiki
        return context
