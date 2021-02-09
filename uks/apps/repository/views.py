import datetime
import json
import os
from django.db.models import Q
from django.shortcuts import render

import requests
from django.contrib import messages
from django.core import serializers
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView

from .forms import RepositoryForm
from .models import Repository
# Create your views here.
from ..branch.models import Branch
from ..user.models import UserHistoryItem


class RepositoryDetailView(DetailView):
    model = Repository
    template_name = 'repository/overview.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        self.repository = get_object_or_404(Repository, id=self.kwargs['pk'])

        context = super(RepositoryDetailView, self).get_context_data(**kwargs)
        context['branches'] = Branch.objects.filter(repository=self.repository)

        qs = Branch.objects.filter(repository=self.repository)
        context["qs_json"] = json.dumps([obj.as_dict() for obj in qs])
        context['first'] = Branch.objects.filter(Q(repository_id=self.repository.id)).first()
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

    api_token = os.getenv("GITHUB_TOKEN")
    response = requests.get(request, auth=('uks', api_token)).text

    branches = []
    for obj in json.loads(response):
        branch = Branch()
        branch.name = obj['name']
        branch.repository = repository
        branch.save()
        branches.append(branch)


def addRepository(request):
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
