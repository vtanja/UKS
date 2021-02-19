import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DeleteView

from apps.branch.forms import UpdateBranchForm
from apps.branch.models import Branch
from apps.repository.models import Repository

logger = logging.getLogger('django')


class BranchListView(UserPassesTestMixin, ListView):
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
        context['collab'] = self.request.user in self.repository.collaborators.all() or self.request.user == self.repository.owner
        return context

    def test_func(self):
        logger.info('Checking if user has permission to create new wiki page!')
        repo = get_object_or_404(Repository, id=self.kwargs['pk'])
        return repo.test_access(self.request.user)


class BranchDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Branch

    def get_success_url(self):
        logger.info('Routing to all branches after deleting branch!')
        messages.success(self.request, 'Successfully deleted branch!')
        return reverse_lazy('branch_list', kwargs={'pk': self.kwargs['pk']})

    def delete(self, request, *args, **kwargs):
        branch = get_object_or_404(Branch, self.kwargs['branch_id'])
        branch.delete()

    def test_func(self):
        logger.info('Checking if user has permission to delete branch!')
        repo = get_object_or_404(Repository, id=self.kwargs['pk'])
        return repo.test_user(self.request.user)


@login_required
def update_branch(request, pk, branch_id):
    logger.info('Getting branch that should be updates!')
    branch = get_object_or_404(Branch, id=branch_id)

    is_collab = request.user in branch.repository.collaborators.all()
    if is_collab or branch.repository.owner == request.user:
        if request.method == 'POST':
            p_form = UpdateBranchForm(request.POST,
                                      instance=branch)
            if p_form.is_valid():
                logger.info('Valid form for updating branch!')
                p_form.save()
                logger.info('Successfully updating branch[id: %s]', branch_id)
                messages.success(request, 'You have successfully updated branch!')

        logger.info('Routing to all branches after updating branch!')
        return redirect('branch_list', pk=pk)
    else:
        messages.error(request, 'User has no permissions for this action!')
        return redirect('branch_list', pk=pk)
