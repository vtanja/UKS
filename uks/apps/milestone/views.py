import logging
from datetime import timedelta

from apps.issue.models import Issue
from apps.milestone.forms import CreateMilestoneForm
from apps.milestone.models import Milestone
from apps.repository.models import Repository
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView, TemplateView

logger = logging.getLogger('django')


class MilestoneListView(ListView):
    model = Milestone
    template_name = 'milestone/milestone_list.html'

    def get_queryset(self):
        self.repository = get_object_or_404(Repository, id=self.kwargs['repo_id'])
        return Milestone.objects.filter(repository=self.repository)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(MilestoneListView, self).get_context_data(**kwargs)
        context['repository'] = self.repository
        context['show'] = False
        logger.info('Milestone list view context initialized')
        return context


class CreateMilestoneView(LoginRequiredMixin, CreateView):
    model = Milestone
    template_name = 'milestone/milestone_create.html'
    form_class = CreateMilestoneForm

    def form_valid(self, form):
        form.instance.repository = get_object_or_404(Repository, id=self.kwargs['repo_id'])
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(CreateMilestoneView, self).get_form_kwargs()
        kwargs['repository'] = get_object_or_404(Repository, id=self.kwargs['repo_id'])
        return kwargs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CreateMilestoneView, self).get_context_data(**kwargs)
        self.repository = get_object_or_404(Repository, id=self.kwargs['repo_id'])
        context['repository'] = self.repository
        logger.info('Milestone create view context initialized')
        return context

    def get_success_url(self):
        logger.info('Milestone successfully added to repository with id {}'.format(self.kwargs['repo_id']))
        return reverse_lazy('repository_milestones', kwargs={'repo_id': self.kwargs['repo_id']})


class MilestoneDetailView(DetailView):
    model = Milestone
    template_name = 'milestone/milestone_detail.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(MilestoneDetailView, self).get_context_data(**kwargs)
        self.repository = get_object_or_404(Repository, id=self.kwargs['repo_id'])
        self.milestone = get_object_or_404(Milestone, id=self.kwargs['pk'])
        context['repository'] = self.repository
        context['issues'] = Issue.objects.filter(milestone=self.milestone)
        logger.info('Milestone detail view context initialized')
        return context


class MilestoneUpdateView(UpdateView):
    model = Milestone
    form_class = CreateMilestoneForm
    template_name_suffix = '_update'

    def get_form_kwargs(self):
        kwargs = super(MilestoneUpdateView, self).get_form_kwargs()
        kwargs['repository'] = get_object_or_404(Repository, id=self.kwargs['repo_id'])
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(MilestoneUpdateView, self).get_context_data(**kwargs)
        self.repository = get_object_or_404(Repository, id=self.kwargs['repo_id'])
        self.milestone = get_object_or_404(Milestone, id=self.kwargs['pk'])
        context['repository'] = self.repository
        logger.info('Milestone update view context initialized')
        return context

    def get_success_url(self):
        logger.info('Milestone with id {} successfully updated'.format(self.kwargs['pk']))
        milestone = get_object_or_404(Milestone, id=self.kwargs['pk'])
        milestone.set_updated()
        return reverse_lazy('repository_milestones', kwargs={'repo_id': self.kwargs['repo_id']})


@login_required
def close_milestone(request, repo_id, pk):
    milestone = get_object_or_404(Milestone, pk=pk)
    milestone.toggle_milestone_close()
    if milestone.closed:
        logger.info('Milestone {} successfully closed'.format(milestone))
    else:
        logger.info('Milestone {} successfully reopened'.format(milestone))
    return redirect(reverse_lazy('milestone_details', kwargs={'repo_id': repo_id, 'pk': pk}))


class MilestoneDeleteView(DeleteView):
    model = Milestone
    template_name_suffix = '_delete'

    def get_context_data(self, **kwargs):
        context = super(MilestoneDeleteView, self).get_context_data(**kwargs)
        self.repository = get_object_or_404(Repository, id=self.kwargs['repo_id'])
        self.milestone = get_object_or_404(Milestone, id=self.kwargs['pk'])
        context['repository'] = self.repository
        logger.info('Milestone delete view context initialized')
        return context

    def get_success_url(self):
        logger.info('Milestone with id {} succesfully deleted'.format(self.kwargs['pk']))
        return reverse_lazy('repository_milestones', kwargs={'repo_id': self.kwargs['repo_id']})


class MilestoneStatisticsView(LoginRequiredMixin, TemplateView):
    template_name = 'milestone/milestone_statistics.html'

    def get_context_data(self, **kwargs):
        self.repository = get_object_or_404(Repository, id=self.kwargs['repository_id'])
        context = super(MilestoneStatisticsView, self).get_context_data(**kwargs)
        context['repository'] = self.repository
        repository_milestones = Milestone.objects.filter(repository=self.repository)
        context['closed_milestones_percent'] = self.get_completed_percentage(repository_milestones)
        context['closed_milestones'] = repository_milestones.filter(closed=True).count()
        context['open_milestones'] = repository_milestones.filter(closed=False).count()
        context['all_milestones'] = repository_milestones.count()
        context['average_lasting'], lens, labels, average_l = self.get_average_milestone_length(milestones=repository_milestones)
        context['lens'] = ','.join([str(i) for i in lens])
        context['labels'] = ','.join([str(i) for i in labels])
        context['average'] = ','.join([str(i) for i in average_l])
        return context

    def get_completed_percentage(self, milestones):
        all_count = milestones.count()
        if all_count == 0:
            return 100
        closed_count = milestones.filter(closed=True).count()
        res = (100*closed_count)/all_count
        return round(res)

    def get_average_milestone_length(self, milestones):
        count = 0
        length = 0
        response = ''
        lens = []
        labels = []
        average_l = []
        for milestone in milestones:
            if milestone.is_finished():
                diff = milestone.dateClosed - milestone.dateCreated
                diff = diff.days
                lens.append(diff)
                labels.append(milestone.title)
                count = count + 1
                length += diff
        if count == 0:
            response = 'no data', lens, labels, average_l
            return response
        average = round(length/count)
        if average < 30:
            response = str(average) + ' days'
        elif 30 < average < 365:
            months = round(average/30)
            days = average - (months*30)
            response = '{} months and {} days'.format(str(months), str(days))
        for len in lens:
            average_l.append(average)
        return response, lens, labels, average_l
