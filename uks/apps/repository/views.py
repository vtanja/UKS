import datetime
import json
import logging
import os

from django.contrib.auth.models import User
import requests
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, View

from .forms import RepositoryForm, CollaboratorsForm
from .models import Repository
# Create your views here.
from ..branch.models import Branch
from ..user.models import UserHistoryItem

logger = logging.getLogger('django')
repoId = 0


class RepositoryDetailView(DetailView):
    model = Repository
    template_name = 'repository/overview.html'

    def get_context_data(self, *, object_list=None, **kwargs):
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
    parts = repository.repo_url.split('/')
    user = parts[3]
    repo_name = parts[4]
    request = 'https://api.github.com/repos/' + user + '/' + repo_name + '/branches'

    logger.info('Getting token for authorizing github api requests!')
    api_token = os.getenv("GITHUB_TOKEN")
    logger.info('Sending request for getting all branches of repository [%s]', repo_name)
    response = requests.get(request, auth=('uks', api_token)).text

    logger.info('Storing branches into db initialized!')
    branches = []
    for obj in json.loads(response):
        branch = Branch()
        branch.name = obj['name']
        branch.repository = repository
        branch.save()
        branches.append(branch)
    logger.info('Storing branches into db done!')


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

            get_branches(repository)
            # repository.branch_set.set(branches)

            change = UserHistoryItem()
            change.dateChanged = datetime.datetime.now()
            change.belongsTo = request.user
            change.message = 'added new repository'
            change.save()

            messages.success(request, 'Successfully added new repository!')
            return redirect('dashboard')
        else:
            print('Forma nije validna')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = RepositoryForm()

    return render(request, 'user/dashboard.html', {'form': form})


def RepositorySettings(request, id):
    repositories = Repository.objects.filter(
        Q(owner=request.user) | Q(collaborators__username__in=[str(request.user)])
    )
    repository = Repository.objects.get(id=id)
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
            print(users)
            global repo
            repository = Repository.objects.get(id=repo)
            print(repository.name)
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
    print(collabs)
    context = {'repository': repository, 'users': users, 'collabs': collabs}
    return render(request, 'repository/repoSettings.html', context)
