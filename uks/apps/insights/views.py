# Create your views here.
import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from apps.repository.models import Repository
from apps.commit.models import Commit
from apps.branch.models import Branch
from apps.milestone.models import Milestone
from apps.issue.models import Issue
from apps.user.models import HistoryItem


def get_commits_per_user(commits):
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


def get_commits_per_day(commits):
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
        comms_pp, labels_pp = get_commits_per_user(repository_commits)
        comms_pd, labels_pd = get_commits_per_day(repository_commits)
        context['comms_pp'] = ','.join([str(i) for i in comms_pp])
        context['labels_pp'] = ','.join([str(i) for i in labels_pp])
        context['comms_pd'] = ','.join([str(i) for i in comms_pd])
        context['labels_pd'] = '*'.join([str(i) for i in labels_pd])
        master_comms_pp, master_labels_pp = get_commits_per_user(list(master_commits))
        master_comms_pd, master_labels_pd = get_commits_per_day(list(master_commits))
        context['master_comms_pp'] = ','.join([str(i) for i in master_comms_pp])
        context['master_labels_pp'] = ','.join([str(i) for i in master_labels_pp])
        context['master_comms_pd'] = ','.join([str(i) for i in master_comms_pd])
        context['master_labels_pd'] = '*'.join([str(i) for i in master_labels_pd])
        return context


class MilestoneStatisticsView(LoginRequiredMixin, TemplateView):
    template_name = 'milestone/milestone_statistics.html'

    def get_context_data(self, **kwargs):
        self.repository = get_object_or_404(Repository, id=self.kwargs['repository_id'])
        context = super(MilestoneStatisticsView, self).get_context_data(**kwargs)
        context['repository'] = self.repository
        repository_milestones = Milestone.objects.filter(repository=self.repository)
        context['closed_milestones_percent'] = get_completed_percentage(repository_milestones)
        context['closed_milestones'] = repository_milestones.filter(closed=True).count()
        context['open_milestones'] = repository_milestones.filter(closed=False).count()
        context['all_milestones'] = repository_milestones.count()
        context['average_lasting'], lens, labels, average_l = get_average_milestone_length(milestones=repository_milestones)
        context['lens'] = ','.join([str(i) for i in lens])
        context['labels'] = ','.join([str(i) for i in labels])
        context['average'] = ','.join([str(i) for i in average_l])
        return context


def get_completed_percentage(milestones):
    all_count = milestones.count()
    if all_count == 0:
        return 0
    closed_count = milestones.filter(closed=True).count()
    res = (100*closed_count)/all_count
    return round(res)


def get_average_milestone_length(milestones):
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
    i = 0
    while i < len(lens):
        average_l.append(average)
        i = i + 1
    return response, lens, labels, average_l


class IssueStatisticsView(LoginRequiredMixin, TemplateView):
    template_name = 'issue/issue_statistics.html'

    def get_context_data(self, **kwargs):
        self.repository = get_object_or_404(Repository, id=self.kwargs['repository_id'])
        context = super(IssueStatisticsView, self).get_context_data(**kwargs)
        context['repository'] = self.repository
        repository_issues = Issue.objects.filter(repository=self.repository)
        context['opened_issues'] = repository_issues.filter(closed=False).count()
        context['closed_issues'] = repository_issues.filter(closed=True).count()
        context['average_lasting'], lens_l, labels_l, average_l = get_average_issue_length(issues=repository_issues)
        context['lengths'] = ','.join([str(i) for i in lens_l])
        context['labels'] = ','.join([str(i) for i in labels_l])
        context['average'] = ','.join([str(i) for i in average_l])
        return context


def get_average_issue_length(issues):
    cnt = 0
    length = 0
    response = ''
    lens = []
    labels = []
    average_l = []
    for issue in issues:
        if issue.closed:
            hi_l = HistoryItem.objects.filter(changed_issue=issue, message__contains='closed').order_by('-date_changed')
            hi = hi_l[0]
            diff = hi.date_changed - issue.date_created
            diff = diff.days
            lens.append(diff)
            labels.append(issue.title)
            cnt = cnt + 1
            length += diff
    if cnt == 0:
        response = 'no available data', lens, labels, average_l
        return response
    average = round(length/cnt)
    if average < 30:
        response = str(average) + ' days.'
    elif 30 < average < 365:
        months = round(average/30)
        days = average - (months*30)
        response = '{} months and {} days.'.format(str(months), str(days))
    i = 0
    while i < len(lens):
        average_l.append(average)
        i = i + 1
    return response, lens, labels, average_l
