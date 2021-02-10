import json
import os

import requests
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy

from django.views.generic import DetailView, ListView, DeleteView

from apps.branch.forms import UpdateBranchForm
from apps.branch.models import Branch
from apps.repository.models import Repository


class BranchDetailView(DetailView):
    model = Branch

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(BranchDetailView, self).get_context_data(**kwargs)
        return context


class BranchListView(ListView):
    model = Branch

    def get_queryset(self):
        self.repository = get_object_or_404(Repository, id=self.kwargs['id'])
        self.p_form = UpdateBranchForm()
        return Branch.objects.filter(repository=self.repository).order_by('id')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(BranchListView, self).get_context_data(**kwargs)
        context['repository'] = self.repository
        context['p_form'] = self.p_form
        return context


class BranchDeleteView(DeleteView):
    model = Branch

    def get_success_url(self):
        return reverse_lazy('branch_list', kwargs={'id': self.kwargs['id']})


def update_branch(request, id, pk):
    branch = get_object_or_404(Branch, id=pk)
    if request.method == 'POST':
        p_form = UpdateBranchForm(request.POST,
                                        instance=branch)
        if p_form.is_valid():
            p_form.save()
            messages.success(request, f'You have successfully updated branch!')

    return redirect('branch_list', id=id)