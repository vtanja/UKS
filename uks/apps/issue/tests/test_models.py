from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .test_views import fill_test_db
from ..models import Issue


class IssueModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        fill_test_db()

    def test_title_label(self):
        issue = Issue.objects.get(pk=4)
        verbose_name = issue._meta.get_field('title').verbose_name
        self.assertEquals(verbose_name, 'title')

    def test_created_by_label(self):
        issue = Issue.objects.get(pk=4)
        verbose_name = issue._meta.get_field('created_by').verbose_name
        self.assertEquals(verbose_name, 'created by')

    def test_title_max_length(self):
        issue = Issue.objects.get(pk=4)
        max_length = issue._meta.get_field('title').max_length
        self.assertEquals(max_length, 100)

    def test_milestone_null(self):
        issue = Issue.objects.get(pk=4)
        is_null = issue._meta.get_field('milestone').null
        self.assertTrue(is_null)

    def test_object_name_is_title(self):
        issue = Issue.objects.get(pk=4)
        self.assertEqual(str(issue), issue.title)

    def test_get_absolute_url(self):
        issue = Issue.objects.get(pk=4)
        self.assertEqual(issue.get_absolute_url(),
                         reverse('issue-details', args=[str(issue.repository.id), str(issue.id)]))

    def test_toggle_issue_close_with_opened_issue(self):
        issue = Issue.objects.filter(closed=False)[0]
        issue.toggle_issue_close(User.objects.all()[0])
        issue.refresh_from_db()
        self.assertTrue(issue.closed is True)

    def test_toggle_issue_close_with_closed_issue(self):
        issue = Issue.objects.filter(closed=True)[0]
        issue.toggle_issue_close(User.objects.all()[0])
        issue.refresh_from_db()
        self.assertTrue(issue.closed is False)

    def test_change_status_to_todo(self):
        self.change_issue_status('TODO', False)

    def test_change_status_to_ongoing(self):
        self.change_issue_status('ONGOING', False)

    def test_change_status_to_done_closes_issue(self):
        self.change_issue_status('DONE', True)

    def change_issue_status(self, status, closed):
        issue = Issue.objects.get(pk=4)
        issue.change_status(status, User.objects.all()[0])
        self.assertEqual(issue.issue_status, status)
        self.assertTrue(issue.closed is closed)
