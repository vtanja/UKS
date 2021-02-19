import json
import logging
import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView, DeleteView, UpdateView, TemplateView
from ghapi.all import GhApi

from .forms import RepositoryForm, CollaboratorsForm, RepositoryFormEdit, RepositoryFormVisibilityEdit
from .models import Repository
from ..branch.models import Branch
from ..commit.models import Commit
from ..tag.models import Tag
from ..user.models import HistoryItem

logger = logging.getLogger('django')
repo = 0
manageAccessUrl = 'repository/manageAccess.html'


def add_history_item(user, message):
    change = HistoryItem()
    change.date_changed = timezone.now()
    change.belongs_to = user
    change.message = message
    return change


class RepositoryDetailView(DetailView):
    model = Repository
    template_name = 'repository/overview.html'

    def get_context_data(self, **kwargs):
        logger.info('Getting repository with id: %s', self.kwargs['pk'])
        self.repository = get_object_or_404(Repository, id=self.kwargs['pk'])

        context = super(RepositoryDetailView, self).get_context_data(**kwargs)
        logger.info('Retrieving branches that belong to repository with id: %s', self.kwargs['pk'])
        context['branches'] = Branch.objects.filter(repository=self.repository)

        qs = Branch.objects.filter(repository=self.repository)
        context["qs_json"] = json.dumps([obj.as_dict() for obj in qs])
        context['show'] = True

        self.check_args()

        commits = Commit.objects.filter(branches__in=[self.branch]).order_by('-date')

        context['commit_num'] = commits.count()

        context['branch'] = self.branch

        paginator = Paginator(commits, 15)  # Show 25 contacts per page.

        page_number = self.request.GET.get('page')
        if page_number is None:
            page_number = 1

        page_obj = paginator.get_page(page_number)

        context['page_obj'] = page_obj

        commits = paginator.page(page_number)

        context['commits'] = commits

        context['tags'] = Tag.objects.filter(repository=self.repository)
        return context

    def check_args(self):
        if self.kwargs.keys().__contains__('branch_id'):
            if self.kwargs['branch_id'] is not None:
                self.branch = get_object_or_404(Branch, id=self.kwargs['branch_id'])
        else:
            if self.repository.branch_set.filter(name='main').count() != 0:
                self.branch = Branch.objects.filter(repository_id=self.repository.id, name='main').get()
            elif self.repository.branch_set.filter(name='master').count() != 0:
                self.branch = Branch.objects.filter(repository_id=self.repository.id, name='master').get()
            elif self.repository.branch_set.filter(name='develop').count() != 0:
                self.branch = Branch.objects.filter(repository_id=self.repository.id, name='develop').get()
            else:
                self.branch = self.repository.branch_set.first()


@login_required
def detail(request, id):
    repositories = Repository.objects.filter(
        Q(owner=request.user) | Q(collaborators__username__in=[str(request.user)])
    )
    repository = Repository.objects.get(id=id)
    print(repository.name)
    context = {'repositories': repositories, 'repository': repository}
    return render(request, 'repository/repoDetail.html', context)


def get_branches(repository):
    api = get_github_api(repository)
    if api is None:
        return
    logger.info('Sending request for getting all branches of repository')
    branches = api.repos.list_branches(per_page=100)
    for index, branch in enumerate(branches):
        logger.info('Creating new branch')
        print('Adding branch {}/{}'.format(index + 1, len(branches)))
        br = Branch()
        br.name = branch.name
        br.repository = repository
        br.save()
        logger.info('Getting all commits for current branch')
        get_commits(api, br)


def get_repository_name_and_owner(repository):
    parts = repository.repo_url.split('/')
    user = parts[3]
    repo_name = parts[4]
    return repo_name, user


@login_required
def add_repository(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        form = RepositoryForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            print('Forma je validna')
            # form.save()
            form.instance.owner = request.user

            if form.instance.repo_url is None:
                form.instance.repo_url = 'https://github.com/vtanja/UKS'

            repository = form.save()
            repository.collaborators.add(request.user)

            start = timezone.now()
            get_branches(repository)
            print('Retrieving branches and commits took: {}'.format(timezone.now() - start))
            logger.info('Retrieving branches and commits took: {}'.format(timezone.now() - start))

            change = add_history_item(request.user, 'added new')
            change.changed_repo_object = repository
            change.save()

            messages.success(request, 'Successfully added new repository!')
            return redirect('dashboard')
        else:
            print('Forma nije validna')

    return render(request, 'user/dashboard.html', {'form': form})


@login_required
def manage_access(request, key):
    repository = Repository.objects.get(id=key)
    if not request.user == repository.owner:
        return redirect('dashboard')
    else:
        global repo
        repo = repository.id
        users = User.objects.filter().exclude(id=repository.owner.id).exclude(username='admin')
        collabs = repository.collaborators.all()
        context = {'repository': repository, 'users': users, 'collabs': collabs}
        return render(request, manageAccessUrl, context)


def get_commits(api, br):
    commits = api.repos.list_commits(accept='application/vnd.github.v3+json', sha=br.name, per_page=100, page=0)
    page = 1
    commits_with_missing_parents = {}
    while commits:
        for commit in reversed(commits):
            try:
                ci = Commit.objects.get(sha=commit.sha)
                ci.branches.add(br)
                continue
            except Commit.DoesNotExist:
                ci = create_commit_from_response(commit)
                ci.save()
                ci.branches.add(br)
                add_parents_to_commit(ci, commit, commits_with_missing_parents)

        logger.info('Getting next page of commits')
        commits = api.repos.list_commits(accept='application/vnd.github.v3+json', sha=br.name, per_page=100, page=page)
        page += 1

    add_parents_that_were_missing_to_commits(commits_with_missing_parents)


def create_commit_from_response(commit):
    ci = Commit()
    ci.url = commit.html_url
    ci.sha = commit.sha
    ci.author = commit.author.login
    ci.date = commit.commit.author.date
    ci.message = commit.commit.message
    return ci


def add_parents_to_commit(ci, commit, commits_with_missing_parents):
    for parent in commit.parents:
        try:
            par = Commit.objects.get(sha=parent.sha)
            ci.parents.add(par)
        except Commit.DoesNotExist:
            commits_with_missing_parents[ci] = parent.sha


def add_parents_that_were_missing_to_commits(commits_with_missing_parents):
    logger.info('Connecting commits whose parents were not created at the time')
    for key in commits_with_missing_parents.keys():
        try:
            parent = Commit.objects.get(sha=commits_with_missing_parents[key])
            key.parents.add(parent)
            key.save()
        except Commit.DoesNotExist:
            logger.error('Could not find parent with sha hash: {}'.format(commits_with_missing_parents[key]))


def get_github_api(repository):
    if os.getenv('GIT_TOKEN'):
        repository_name, owner = get_repository_name_and_owner(repository)
        api = GhApi(owner=owner, repo=repository_name, token=os.getenv('GIT_TOKEN'))
        return api
    else:
        logger.error('GitHub api token does not exist')
        return None


@login_required
def repository_settings(request, key):
    repository = Repository.objects.get(id=key)
    if not request.user == repository.owner:
        return redirect('dashboard')
    else:
        global repo
        repo = repository.id
        users = User.objects.filter().exclude(id=repository.owner.id).exclude(username='admin')
        collabs = repository.collaborators.all()
        context = {'repository': repository, 'users': users, 'collabs': collabs}
        return render(request, manageAccessUrl, context)


@login_required
def options(request, key):
    repository = Repository.objects.get(id=key)
    if not request.user == repository.owner:
        return redirect('dashboard')
    else:
        context = {'repository': repository}
        return render(request, 'repository/options.html', context)


@login_required
def add_collaborators(request):
    if request.method == 'POST':
        form = CollaboratorsForm(request.POST)
        if form.is_valid():
            users = form.data.getlist('collaborators')
            global repo
            for u in users:
                user = User.objects.get(username=u)
                Repository.objects.get(id=repo).collaborators.add(user)

        else:
            print('Forma nije validna')

    repository = Repository.objects.get(id=repo)
    users = User.objects.filter().exclude(id=repository.owner.id).exclude(username='admin')
    collabs = repository.collaborators.all()
    context = {'repository': repository, 'users': users, 'collabs': collabs}
    return render(request, manageAccessUrl, context)


class CollaboratorsDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = "repository/deleteCollaborators.html"

    def get_context_data(self, **kwargs):
        self.repository = get_object_or_404(Repository, id=repo)
        context = super(CollaboratorsDeleteView, self).get_context_data(**kwargs)
        context['repository'] = self.repository
        print(context)
        return context

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        print(self.object)
        user = User.objects.get(username=self.object.username)
        print(user)
        repository = Repository.objects.get(id=repo)
        repository.collaborators.remove(user)
        success_url = self.get_success_url()
        return redirect(success_url)

    def get_form_kwargs(self):
        kwargs = super(CollaboratorsDeleteView, self).get_form_kwargs()
        kwargs['repository'] = get_object_or_404(Repository, id=repo)
        return kwargs

    def get_success_url(self):
        return reverse_lazy('manage_access', kwargs={'key': repo})


class RepositoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Repository
    template_name = "repository/repoUpdate.html"
    form_class = RepositoryFormEdit

    def get_context_data(self, **kwargs):
        self.repository = get_object_or_404(Repository, id=self.kwargs['pk'])
        context = super(RepositoryUpdateView, self).get_context_data(**kwargs)
        context['repository'] = self.repository
        return context

    def get_form_kwargs(self):
        kwargs = super(RepositoryUpdateView, self).get_form_kwargs()
        kwargs['repository'] = get_object_or_404(Repository, id=self.kwargs['pk'])
        return kwargs

    def get_success_url(self):
        return reverse_lazy('options', kwargs={'key': repo})


class RepositoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Repository
    template_name = "repository/repositoryDelete.html"

    def get_context_data(self, **kwargs):
        self.repository = get_object_or_404(Repository, id=self.kwargs['pk'])
        context = super(RepositoryDeleteView, self).get_context_data(**kwargs)
        context['repository'] = self.repository
        print(context)
        return context

    def get_form_kwargs(self):
        kwargs = super(RepositoryDeleteView, self).get_form_kwargs()
        kwargs['repository'] = get_object_or_404(Repository, id=self.kwargs['pk'])
        return kwargs

    def get_success_url(self):
        return reverse_lazy('dashboard')



class RepositoryUpdateVisibilityView(LoginRequiredMixin, UpdateView):
    model = Repository
    template_name = "repository/editVisibility.html"
    form_class = RepositoryFormVisibilityEdit

    def get_context_data(self, **kwargs):
        self.repository = get_object_or_404(Repository, id=self.kwargs['pk'])
        context = super(RepositoryUpdateVisibilityView, self).get_context_data(**kwargs)
        context['repository'] = self.repository
        return context

    def get_form_kwargs(self):
        kwargs = super(RepositoryUpdateVisibilityView, self).get_form_kwargs()
        kwargs['repository'] = get_object_or_404(Repository, id=self.kwargs['pk'])
        return kwargs

    def get_success_url(self):
        return reverse_lazy('manage_access', kwargs={'key': repo})



class RepositoryInsightsView(LoginRequiredMixin, TemplateView):
    template_name = 'repository/repository_insights.html'

    def get_context_data(self, **kwargs):
        self.repository = get_object_or_404(Repository, id=self.kwargs['repository_id'])
        context = super(RepositoryInsightsView, self).get_context_data(**kwargs)
        context['repository'] = self.repository
        return context

