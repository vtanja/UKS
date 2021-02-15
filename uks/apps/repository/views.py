import json
import logging
import os

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView, DeleteView
from ghapi.all import GhApi

from .forms import RepositoryForm, CollaboratorsForm
from .models import Repository
# Create your views here.
from ..branch.models import Branch
from ..commit.models import Commit
from ..user.models import HistoryItem

logger = logging.getLogger('django')
repo = 0



def add_history_item(user, message):
    change = HistoryItem()
    change.dateChanged = timezone.now()
    change.belongsTo = user
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
        context['first'] = Branch.objects.filter(Q(repository_id=self.repository.id)).first()
        context['show'] = True
        return context


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
    logger.info('Sending request for getting all branches of repository')
    branches = api.repos.list_branches(per_page=100)
    for branch in branches:
        logger.info('Creating new branch')
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


def add_repository(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        form = RepositoryForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            print('Forma je validna')
            # form.save()
            form.instance.owner = request.user
            repository = form.save()

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

    # if a GET (or any other method) we'll create a blank form
    else:
        form = RepositoryForm()

    return render(request, 'user/dashboard.html', {'form': form})


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
    repository_name, owner = get_repository_name_and_owner(repository)
    api = GhApi(owner=owner, repo=repository_name, token=os.getenv('GITHUB_TOKEN'))
    return api


def RepositorySettings(request, key):

    repository = Repository.objects.get(id=key)
    global repo
    repo = repository.id
    users = User.objects.filter().exclude(id=repository.owner.id).exclude(username='admin')
    collabs = repository.collaborators.all()
    context = {'repository': repository, 'users': users, 'collabs': collabs}
    return render(request, 'repository/repoSettings.html', context)


def addCollaborators(request):
    if request.method == 'POST':
        form = CollaboratorsForm(request.POST)
        if form.is_valid():
            users = form.data.getlist('collaborators')
            global repo
            repository = Repository.objects.get(id=repo)
            for u in users:
                user = User.objects.get(username=u)
                Repository.objects.get(id=repo).collaborators.add(user)

        else:
            print('Forma nije validna')

    else:
        form = CollaboratorsForm()

    repository = Repository.objects.get(id=repo)
    users = User.objects.filter().exclude(id=repository.owner.id).exclude(username='admin')
    collabs = repository.collaborators.all()
    context = {'repository': repository, 'users': users, 'collabs': collabs}
    return render(request, 'repository/repoSettings.html', context)


class CollaboratorsDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = "repository/deleteCollaborators.html"

    def get_context_data(self, **kwargs):
        print('abc')
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
        print('dfg')
        kwargs = super(CollaboratorsDeleteView, self).get_form_kwargs()
        kwargs['repository'] = get_object_or_404(Repository, id=repo)
        return kwargs

    def get_success_url(self):
        return reverse_lazy('repository_settings', kwargs={'key': repo})
