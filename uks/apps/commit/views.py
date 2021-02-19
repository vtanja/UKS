# Create your views here.
import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from apps.repository.models import Repository
from apps.commit.models import Commit
from apps.branch.models import Branch


class CommitStatisticsView(LoginRequiredMixin, TemplateView):
    template_name = 'commit/commit_statistics.html'

    def get_context_data(self, **kwargs):
        self.repository = get_object_or_404(Repository, id=self.kwargs['repository_id'])
        context = super(CommitStatisticsView, self).get_context_data(**kwargs)
        context['repository'] = self.repository
        all_commits = Commit.objects.all().order_by('date')
        repository_commits = []
        for commit in all_commits:
            if commit.is_in_repository(self.repository):
                repository_commits.append(commit)
        branches = Branch.objects.filter(name='master', repository=self.repository)
        if branches.count() == 0:
            branches = Branch.objects.filter(name='main')
        main = branches.first()
        master_commits = Commit.objects.filter(branches__in=[main])
        comms_pp, labels_pp = self.get_commits_per_user(repository_commits)
        comms_pd, labels_pd = self.get_commits_per_day(repository_commits)
        context['comms_pp'] = ','.join([str(i) for i in comms_pp])
        context['labels_pp'] = ','.join([str(i) for i in labels_pp])
        context['comms_pd'] = ','.join([str(i) for i in comms_pd])
        context['labels_pd'] = '*'.join([str(i) for i in labels_pd])
        master_comms_pp, master_labels_pp = self.get_commits_per_user(list(master_commits))
        master_comms_pd, master_labels_pd = self.get_commits_per_day(list(master_commits))
        context['master_comms_pp'] = ','.join([str(i) for i in master_comms_pp])
        context['master_labels_pp'] = ','.join([str(i) for i in master_labels_pp])
        context['master_comms_pd'] = ','.join([str(i) for i in master_comms_pd])
        context['master_labels_pd'] = '*'.join([str(i) for i in master_labels_pd])

        return context

    def get_commits_per_user(self, commits):
        labels = []
        comms = []
        for commit in commits:
            if commit.author not in labels:
                labels.append(commit.author)
                comms.append(1)
            else:
                index = labels.index(commit.author)
                comms[index] = comms[index] + 1
        return comms, labels

    def get_commits_per_day(self, commits):
        labels = []
        comms = []
        days = 30
        date = datetime.datetime.now()
        for i in range(days):
            current_date = date - datetime.timedelta(days=i)
            count = 0
            for commit in commits:
                if commit.date.date() == current_date.date():
                    count = count + 1
            comm_num = count
            labels.append(current_date.date())
            comms.append(comm_num)
        return reversed(comms), reversed(labels)
