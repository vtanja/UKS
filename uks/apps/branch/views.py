import json
import os

import requests
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

# Create your views here.
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, DeleteView, UpdateView

from apps.branch.forms import BranchForm
from apps.branch.models import Branch
from apps.repository.models import Repository


class BranchDetailView(DetailView):
    model = Branch

    def get_context_data(self, *, object_list=None, **kwargs):
        # self.repository = get_object_or_404(Repository, id=self.kwargs['pk'])
        # self.branches = self.get_branches()

        context = super(BranchDetailView, self).get_context_data(**kwargs)
        # context['branches'] = self.branches
        # context['first'] = self.branches[0]
        return context


class BranchListView(ListView):
    model = Branch

    def get_queryset(self):
        self.repository = get_object_or_404(Repository, id=self.kwargs['pk'])
        return Branch.objects.filter(repository=self.repository)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(BranchListView, self).get_context_data(**kwargs)
        context['repository'] = self.repository
        return context