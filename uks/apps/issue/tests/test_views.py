from django.contrib.auth.models import User
from django.http import Http404
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from ..models import Issue
from ...label.models import Label
from ...milestone.models import Milestone
from ...project.models import Project
from ...repository.models import Repository
from ...user.models import HistoryItem

USER_USERNAME = 'testuser'
USER1_USERNAME = 'testuser1'
USER2_USERNAME = 'testuser2'
USER_PASSWORD = '1E4@DAc#a1p'
USER1_PASSWORD = '4XC%4@1LSp'
USER2_PASSWORD = '4*uxX#sd23'

ISSUE_FORM = 'issue/issue_form.html'


def fill_test_db():
    # Create users
    test_user = User.objects.create_user(username=USER_USERNAME, password=USER_PASSWORD)
    test_user1 = User.objects.create_user(username=USER1_USERNAME, password=USER1_PASSWORD)
    test_user2 = User.objects.create_user(username=USER2_USERNAME, password=USER2_PASSWORD)
    test_user.save()
    test_user1.save()
    test_user2.save()

    # Create repositories
    test_repository = Repository.objects.create(name='test_repository', description='test', owner=test_user)
    test_repository1 = Repository.objects.create(name='test_repository1', description='test2', owner=test_user)
    test_repository2 = Repository.objects.create(name='test_repository2', description='desc', owner=test_user1)
    test_repository.save()
    test_repository1.save()
    test_repository2.save()

    test_project = Project.objects.create(name='test project', description='des', repository=test_repository)
    test_project1 = Project.objects.create(name='test project1', description='des', repository=test_repository)
    test_project.save()
    test_project1.save()

    test_milestone = Milestone.objects.create(title='test milestone', description='test', repository=test_repository,
                                              closed=False, dateCreated=timezone.now(), dueDate=timezone.now())
    test_milestone.save()

    test_label = Label.objects.create(name='functional', description='asdf', color='#3375FFFF', repository=test_repository)
    test_label.save()

    # Create issues and add them to repositories
    test_issue1 = Issue.objects.create(title='test issue', description='test', repository=test_repository,
                                       created_by=test_user)
    test_issue2 = Issue.objects.create(title='test issue2', description='test desc', repository=test_repository,
                                       created_by=test_user)
    test_issue3 = Issue.objects.create(title='test issue 3', description='test', repository=test_repository1,
                                       created_by=test_user1)
    test_issue4 = Issue.objects.create(title='test issue four', description='...', repository=test_repository1,
                                       created_by=test_user1, closed=True)
    test_issue1.milestone = test_milestone
    test_issue1.project = test_project
    test_issue1.labels.add(test_label)
    test_issue1.save()
    test_issue2.save()
    test_issue3.save()
    test_issue4.save()
    test_issue1.assignees.add(test_user)
    test_issue2.assignees.add(test_user)


def get_issue_and_repository_id(issue=0, repository=0):
    if issue != -1:
        issue_id = Issue.objects.all()[issue].id
    else:
        issues = Issue.objects.all()
        issue_id = issues[len(issues) - 1].id + 1
    repository_id = get_repository_id(repository)
    return repository_id, issue_id


def get_repository_id(repository=0):
    if repository != -1:
        repository_id = Repository.objects.all()[repository].id
    else:
        repositories = Repository.objects.all()
        repository_id = repositories[len(repositories) - 1].id + 1
    return repository_id


class IssueListViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        fill_test_db()

    def get_repository_issues(self, repository_id=0):
        repository_id = get_repository_id(repository_id)
        response = self.client.get(reverse('repository-issues', kwargs={'repository_id': repository_id}))
        return response, repository_id

    def test_view_url_accessible_by_name(self):
        response, _ = self.get_repository_issues()
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response, _ = self.get_repository_issues()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'issue/issue_list.html')

    def test_repository_with_no_issues(self):
        response, _ = self.get_repository_issues(2)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['object_list']) == 0)

    def test_repository_with_issues_added_to_it(self):
        response, _ = self.get_repository_issues()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['object_list']) != 0)

    def test_HTTP404_if_repository_doesnt_exist(self):
        response, _ = self.get_repository_issues(-1)
        self.assertEqual(response.status_code, 404)
        self.assertRaisesMessage(Http404, 'No Repository matches the given query.')

    def test_only_issues_from_current_repository_in_list(self):
        response, repository = self.get_repository_issues()
        self.assertTrue(response.context['object_list'] != 0)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['object_list']) == 2)
        for issue in response.context['object_list']:
            self.assertEqual(issue.repository.id, repository)


class IssueDetailViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        fill_test_db()

    def get_repository_issue(self, repository=0, issue=0):
        repository_id, issue_id = get_issue_and_repository_id(repository, issue)
        response = self.client.get(reverse('issue-details', kwargs={'repository_id': repository_id, 'pk': issue_id}))
        return response

    def test_view_url_accessible_by_name(self):
        response = self.get_repository_issue()
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.get_repository_issue()
        self.assertTemplateUsed(response, 'issue/issue_detail.html')

    def test_HTTP404_if_repository_doesnt_exist(self):
        response = self.get_repository_issue(repository=-1)
        self.assert_404_response(response)

    def assert_404_response(self, response):
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_HTTP404_if_issue_doesnt_exist(self):
        response = self.get_repository_issue(issue=-1)
        self.assert_404_response(response)

    def test_view_for_issue_that_exists(self):
        response = self.get_repository_issue()
        self.assertTrue(response.context['issue'] is not None)


class CreateIssueViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        fill_test_db()

    def get_create_issue_response(self, repository=0):
        repository_id = get_repository_id(repository)
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        response = self.client.get(reverse('issue-add', kwargs={'repository_id': repository_id}))
        return response

    def test_redirect_if_user_not_logged_in(self):
        repository = Repository.objects.all()[0].id
        response = self.client.get('/repository/{}/issues/add/'.format(repository))
        self.assertRedirects(response, '/welcome/login/?next=/repository/{}/issues/add/'.format(repository))

    def test_logged_in_user_can_access(self):
        response = self.get_create_issue_response(0)

        self.assertEqual(str(response.wsgi_request.user), USER_USERNAME)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, ISSUE_FORM)

    def test_view_shows_correct_template(self):
        response = self.get_create_issue_response(0)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, ISSUE_FORM)

    def test_HTTP404_if_adding_to_non_existent_repository(self):
        response = self.get_create_issue_response(-1)

        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_redirects_to_repository_issues_on_success(self):
        repository = get_repository_id(0)
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        response = self.client.post(reverse('issue-add', kwargs={'repository_id': repository}),
                                    {'title': 'Test issue', 'description': 'Test description'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/repository/{}/issues/'.format(repository))


class AllIssuesListView(TestCase):

    @classmethod
    def setUpTestData(cls):
        fill_test_db()

    def test_redirect_if_user_not_logged_in(self):
        response = self.client.get('/user/issues/')
        self.assertRedirects(response, '/welcome/login/?next=/user/issues/')

    def get_all_user_issues(self, username=USER_USERNAME, password=USER_PASSWORD):
        self.client.login(username=username, password=password)
        response = self.client.get(reverse('all-user-issues'))
        self.assertEqual(response.status_code, 200)
        return response

    def test_logged_in_user_can_access(self):
        response = self.get_all_user_issues()

        self.assertEqual(str(response.context['user']), USER_USERNAME)

    def test_view_shows_correct_template(self):
        response = self.get_all_user_issues()

        self.assertTemplateUsed(response, 'user/issue_list.html')

    def test_logged_in_user_with_no_issues_on_any_repository(self):
        response = self.get_all_user_issues(USER2_USERNAME, USER2_PASSWORD)

        self.assertTrue(len(response.context['object_list']) == 0)

    def test_logged_in_user_with_assigned_issues(self):
        response = self.get_all_user_issues()

        self.assertTrue(len(response.context['object_list']) == 2)
        for issue in response.context['object_list']:
            self.assertIn(response.wsgi_request.user, issue.assignees.all())

    def test_logged_in_user_with_only_created_issues(self):
        response = self.get_all_user_issues(USER1_USERNAME, USER1_PASSWORD)

        self.assertTrue(len(response.context['object_list']) == 1)
        for issue in response.context['object_list']:
            self.assertEqual(response.wsgi_request.user, issue.created_by)


class IssueUpdateViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        fill_test_db()

    def get_edit_issue_view(self, repository_id=0, issue_id=0):
        """Get edit issue view for specified issue an repository id

        Helper function that returns response for editing existing issue view.
        If -1 is send for either repository_id or issue_id it returns id of non existent issue or repository.
        """
        repository_id, issue_id = get_issue_and_repository_id(repository=repository_id, issue=issue_id)
        response = self.client.get(reverse('issue-update', kwargs={'repository_id': repository_id, 'pk': issue_id}))
        return response, repository_id, issue_id

    def logged_in_user_get_edit_view(self, repository_id=0, issue_id=0):
        """Helper function that logs in user and calls get_edit_issue_view and returns its result"""
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        return self.get_edit_issue_view(repository_id, issue_id)

    def test_redirect_id_user_not_logged_in(self):
        response, repository_id, issue_id = self.get_edit_issue_view()
        self.assertRedirects(response,
                             '/welcome/login/?next=/repository/{}/issues/{}/edit/'.format(repository_id, issue_id))

    def test_logged_in_user_can_access(self):
        response, _, _ = self.logged_in_user_get_edit_view()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.wsgi_request.user), USER_USERNAME)
        self.assertTemplateUsed(response, ISSUE_FORM)

    def test_view_shows_correct_template(self):
        response, _, _ = self.logged_in_user_get_edit_view()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, ISSUE_FORM)

    def test_HTTP404_changing_issue_from_non_existent_repository(self):
        response, _, _ = self.logged_in_user_get_edit_view(-1)

        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_HTTP404_changing_non_existing_issue(self):
        response, _, _ = self.logged_in_user_get_edit_view(issue_id=-1)

        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_history_item_created_for_every_change_and_redirect(self):
        """Test editing existing issue. Then it checks whether correct amount of IssueChange objects were created."""
        start_of_the_test = timezone.now()
        _, repository_id, issue_id = self.logged_in_user_get_edit_view()

        response = self.client.post(reverse('issue-update', kwargs={'repository_id': repository_id, 'pk': issue_id}),
                                    {'title': 'Changed test title', 'description': 'test',
                                     'assignees': [], 'milestone': ''})

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/repository/{}/issues/{}/'.format(repository_id, issue_id))
        # Find all objects that have been changed since start of the test process
        issue_change_objects = HistoryItem.objects.filter(date_changed__gt=start_of_the_test,
                                                          belongs_to=response.wsgi_request.user)
        # Changed title and assignee list
        self.assertEqual(len(issue_change_objects), 2)


class CloseIssueTet(TestCase):

    @classmethod
    def setUpTestData(cls):
        fill_test_db()

    def test_redirect_user_if_not_logged_in(self):
        repository_id, issue_id = get_issue_and_repository_id()
        response = self.client.get('/repository/{}/issues/{}/close/'.format(repository_id, issue_id))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response,
                             '/welcome/login/?next=/repository/{}/issues/{}/close/'.format(repository_id, issue_id))

    def get_response_for_close_issue(self, repository_id=0, issue_id=0):
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        repository_id, issue_id = get_issue_and_repository_id(repository=repository_id, issue=issue_id)
        response = self.client.get(reverse('issue-close', kwargs={'repository_id': repository_id, 'pk': issue_id}))
        return response, repository_id, issue_id

    def test_close_issue_accessible_by_name(self):
        response, repository_id, issue_id = self.get_response_for_close_issue()
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('issue-details', kwargs={'repository_id': repository_id, 'pk': issue_id}))

    def test_HTTP404_if_repository_doesnt_exist(self):
        response, _, _ = self.get_response_for_close_issue(repository_id=-1)
        self.assert_404(response)

    def test_HTTP404_if_issue_doesnt_exist(self):
        response, _, _ = self.get_response_for_close_issue(issue_id=-1)
        self.assert_404(response)

    def assert_404(self, response):
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_close_opened_issue(self):
        issue = self.get_close_issue_by_closed_attribute(False)
        self.assertTrue(issue.closed)

    def test_open_closed_issue(self):
        issue = self.get_close_issue_by_closed_attribute(True)
        self.assertTrue(issue.closed is False)

    def get_close_issue_by_closed_attribute(self, closed):
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        issue = Issue.objects.filter(closed=closed)[0]
        self.client.get(reverse('issue-close', kwargs={'repository_id': issue.repository.id, 'pk': issue.pk}))
        issue.refresh_from_db()
        return issue
