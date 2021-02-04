from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.views.generic import DetailView

from apps.branch.models import Branch


class BranchDetailView(DetailView):
    model = Branch

    def get_context_data(self, *, object_list=None, **kwargs):
        # self.repository = get_object_or_404(Repository, id=self.kwargs['pk'])
        # self.branches = self.get_branches()

        context = super(BranchDetailView, self).get_context_data(**kwargs)
        # context['branches'] = self.branches
        # context['first'] = self.branches[0]
        return context