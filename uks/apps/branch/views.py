import json
import logging

from django.contrib import messages
from django.db.models import Q

from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy

from django.views.generic import DetailView, ListView, DeleteView

from apps.branch.forms import UpdateBranchForm
from apps.branch.models import Branch
from apps.repository.models import Repository
from apps.repository.views import RepositoryDetailView

logger = logging.getLogger('django')


class BranchListView(ListView):
    model = Branch

    def get_queryset(self):
        logger.info('Getting current repository!')
        self.repository = get_object_or_404(Repository, id=self.kwargs['pk'])
        logger.info('Creating form for updating branch!')
        self.p_form = UpdateBranchForm()
        logger.info('Getting all branches that belong to repository [name: %s]!', self.repository.name)
        return Branch.objects.filter(repository=self.repository).order_by('id')

    def get_context_data(self, **kwargs):
        context = super(BranchListView, self).get_context_data(**kwargs)
        logger.info('Initializing context!')
        context['repository'] = self.repository
        context['p_form'] = self.p_form
        context['show'] = True
        return context


class BranchDeleteView(DeleteView):
    model = Branch

    def get_success_url(self):
        logger.info('Routing to all branches after deleting branch!')
        return reverse_lazy('branch_list', kwargs={'repo_id': self.kwargs['repo_id']})


def update_branch(request, pk, branch_id):
    logger.info('Getting branch that should be updates!')
    branch = get_object_or_404(Branch, id=branch_id)
    if request.method == 'POST':
        p_form = UpdateBranchForm(request.POST,
                                        instance=branch)
        if p_form.is_valid():
            logger.info('Valid form for updating branch!')
            p_form.save()
            logger.info('Successfully updating branch[id: %s]', branch_id)
            messages.success(request, 'You have successfully updated branch!')

    logger.info('Routing to all branches after updating branch!')
    return redirect('branch_list', id=pk)
