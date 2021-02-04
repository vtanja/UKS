import datetime
import json
import os

import requests
from django.contrib import messages
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

    def get_branches(self):
        parts = self.repository.repo_url.split('/')
        user = parts[3]
        repo_name = parts[4]
        request = 'https://api.github.com/repos/'+user+'/'+repo_name+'/branches'

        self.api_token = os.getenv("GITHUB_TOKEN")
        response = requests.get(request, auth=('uks', self.api_token)).text

        return response

    def parse(self):
        branches = []
        for obj in json.loads(self.branches):
            branch = Branch()
            branch.name = obj['name']
            branches.append(branch)
        return branches

    def get_context_data(self, *, object_list=None, **kwargs):
        self.repository = get_object_or_404(Repository, id=self.kwargs['pk'])
        self.branches = self.get_branches()

        context = super(RepositoryDetailView, self).get_context_data(**kwargs)
        context['branches'] = self.parse()
        context["qs_json"] = self.branches
        context['first'] = self.parse()[0]
        return context


def detail(request, id):
    repositories = request.user.siteuser.repositories.all()
    repository = Repository.objects.get(id=id)
    print(repository.name)
    context = {'repositories': repositories, 'repository': repository}
    return render(request, 'repository/repoDetail.html', context)

def addRepository(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        form = RepositoryForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            print('Forma je validna')
            # form.save()
            repositories = request.user.siteuser.repositories.add(form.save())

            change = UserHistoryItem()
            change.dateChanged = datetime.datetime.now()
            change.belongsTo = request.user.siteuser
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