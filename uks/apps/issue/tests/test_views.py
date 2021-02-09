from django.contrib.auth.models import User
from django.http import Http404
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from ...repository.models import Repository
from ..models import Issue, IssueChange

USER_PASSWORD = '1E4@DAc#a1p'
USER1_PASSWORD = '4XC%4@1LSp'
USER2_PASSWORD = '4*uxX#sd23'

ISSUE_FORM = 'issue/issue_form.html'


def fill_test_db():
    # Create users
    test_user = User.objects.create_user(username='testuser', password=USER_PASSWORD)
    test_user1 = User.objects.create_user(username='testuser1', password=USER1_PASSWORD)
    test_user2 = User.objects.create_user(username='testuser2', password=USER2_PASSWORD)
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

    # Create issues and add them to repositories
    test_issue1 = Issue.objects.create(title='test issue', description='test', repository=test_repository,
                                       created_by=test_user)
    test_issue2 = Issue.objects.create(title='test issue', description='test desc', repository=test_repository,
                                       created_by=test_user)
    test_issue3 = Issue.objects.create(title='test issue 3', description='test', repository=test_repository1,
                                       created_by=test_user1)
    test_issue1.save()
    test_issue2.save()
    test_issue3.save()
    test_issue1.assignees.add(test_user)
    test_issue2.assignees.add(test_user)


class IssueListViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        fill_test_db()

    def test_view_url_exists_at_desired_location(self):
        repository = Repository.objects.all()[0]
        response = self.client.get('/repository/{}/issues/'.format(repository.id))
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        repository = Repository.objects.all()[0]
        response = self.client.get(reverse('repository-issues', kwargs={'id': repository.id}))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        repository = Repository.objects.all()[0]
        response = self.client.get(reverse('repository-issues', kwargs={'id': repository.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'issue/issue_list.html')

    def test_repository_with_no_issues(self):
        repository = Repository.objects.all()[2]
        response = self.client.get(reverse('repository-issues', kwargs={'id': repository.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['object_list']) == 0)

    def test_repository_with_issues_added_to_it(self):
        repository = Repository.objects.all()[0]
        response = self.client.get(reverse('repository-issues', kwargs={'id': repository.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['object_list']) != 0)

    def test_HTTP404_if_repository_doesnt_exist(self):
        repositories = Repository.objects.all()
        non_existent_repository = repositories[len(repositories) - 1].id + 1
        response = self.client.get(reverse('repository-issues', kwargs={'id': non_existent_repository}))
        self.assertEqual(response.status_code, 404)
        self.assertRaisesMessage(Http404, 'No Repository matches the given query.')

    def test_only_issues_from_current_repository_in_list(self):
        repository = Repository.objects.all()[0]
        response = self.client.get(reverse('repository-issues', kwargs={'id': repository.id}))
        self.assertTrue(response.context['object_list'] != 0)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['object_list']) == 2)
        for issue in response.context['object_list']:
            self.assertEqual(issue.repository, repository)


class IssueDetailViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        fill_test_db()

    def test_view_url_exists_at_desired_location(self):
        repository_id = Repository.objects.all()[0].id
        issue_id = Issue.objects.all()[0].id
        response = self.client.get('/repository/{}/issues/{}/'.format(repository_id, issue_id))
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.get_existing_issue()

    def get_existing_issue(self):
        repository_id = Repository.objects.all()[0].id
        issue_id = Issue.objects.all()[0].id
        response = self.client.get(reverse('issue-details', kwargs={'id': repository_id, 'pk': issue_id}))
        self.assertEqual(response.status_code, 200)
        return response

    def test_view_uses_correct_template(self):
        response = self.get_existing_issue()
        self.assertTemplateUsed(response, 'issue/issue_detail.html')

    def test_HTTP404_if_issue_doesnt_exist(self):
        repositories = Repository.objects.all()
        non_existing_repository_id = repositories[len(repositories) - 1].id + 1
        issues = Issue.objects.all()
        issue_id = issues[0].id
        response = self.client.get(reverse('issue-details', kwargs={'id': non_existing_repository_id, 'pk': issue_id}))
        self.assertEqual(response.status_code, 404)
        self.assertRaisesMessage(Http404, 'No Issue matches the given query.')

    def test_HTTP404_if_repository_doesnt_exist(self):
        repositories = Repository.objects.all()
        repository_id = repositories[0].id
        issues = Issue.objects.all()
        non_existing_issue_id = issues[len(issues) - 1].id + 1
        response = self.client.get(reverse('issue-details', kwargs={'id': repository_id, 'pk': non_existing_issue_id}))
        self.assertEqual(response.status_code, 404)
        self.assertRaisesMessage(Http404, 'No Repository matches the given query.')

    def test_view_for_issue_that_exists(self):
        response = self.get_existing_issue()
        self.assertTrue(response.context['issue'] is not None)


class CreateIssueViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        fill_test_db()

    def test_redirect_if_user_not_logged_in(self):
        repository = Repository.objects.all()[0].id
        response = self.client.get('/repository/{}/issues/add/'.format(repository))
        self.assertRedirects(response, '/welcome/login/?next=/repository/{}/issues/add/'.format(repository))

    def test_logged_in_user_can_access(self):
        repository = Repository.objects.all()[0].id
        self.client.login(username='testuser', password=USER_PASSWORD)
        response = self.client.get(reverse('issue-add', kwargs={'id': repository}))

        self.assertEqual(str(response.wsgi_request.user), 'testuser')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, ISSUE_FORM)

    def test_view_shows_correct_template(self):
        repository = Repository.objects.all()[0].id
        self.client.login(username='testuser', password=USER_PASSWORD)
        response = self.client.get(reverse('issue-add', kwargs={'id': repository}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, ISSUE_FORM)

    def test_HTTP404_if_adding_to_non_existent_repository(self):
        repositories = Repository.objects.all()
        non_existent_id = repositories[len(repositories) - 1].id + 1
        self.client.login(username='testuser', password=USER_PASSWORD)
        response = self.client.get(reverse('issue-add', kwargs={'id': non_existent_id}))

        self.assertEqual(response.status_code, 404)
        self.assertRaisesMessage(Http404, 'No Repository matches given query.')

    def test_redirects_to_repository_issues_on_success(self):
        repository = Repository.objects.all()[0].id
        self.client.login(username='testuser', password=USER_PASSWORD)
        response = self.client.post(reverse('issue-add', kwargs={'id': repository}),
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

    def test_logged_in_user_can_access(self):
        self.client.login(username='testuser', password=USER_PASSWORD)
        response = self.client.get(reverse('all-user-issues'))

        self.assertEqual(str(response.context['user']), 'testuser')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/issue_list.html')

    def test_view_shows_correct_template(self):
        self.client.login(username='testuser', password=USER_PASSWORD)
        response = self.client.get(reverse('all-user-issues'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/issue_list.html')

    def test_logged_in_user_with_no_issues_on_any_repository(self):
        self.client.login(username='testuser2', password=USER2_PASSWORD)
        response = self.client.get(reverse('all-user-issues'))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['object_list']) == 0)

    def test_logged_in_user_with_assigned_issues(self):
        self.client.login(username='testuser', password=USER_PASSWORD)
        response = self.client.get(reverse('all-user-issues'))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['object_list']) == 2)
        for issue in response.context['object_list']:
            self.assertIn(response.wsgi_request.user, issue.assignees.all())

    def test_logged_in_user_with_only_created_issues(self):
        self.client.login(username='testuser1', password=USER1_PASSWORD)
        response = self.client.get(reverse('all-user-issues'))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['object_list']) == 1)
        for issue in response.context['object_list']:
            self.assertEqual(response.wsgi_request.user, issue.created_by)


class IssueUpdateViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        fill_test_db()

    def get_edit_existing_issue(self, repository_id=-1, issue_id=-1):
        if repository_id == -1:
            repository_id = Repository.objects.all()[0].id
        if issue_id == -1:
            issue_id = Issue.objects.filter(repository_id=repository_id)[0].id
        response = self.client.get(reverse('issue-update', kwargs={'id': repository_id, 'pk': issue_id}))
        return response, repository_id, issue_id

    def test_redirect_id_user_not_logged_in(self):
        response, repository_id, issue_id = self.get_edit_existing_issue()
        self.assertRedirects(response,
                             '/welcome/login/?next=/repository/{}/issues/{}/edit/'.format(repository_id, issue_id))

    def test_logged_in_user_can_access(self):
        self.client.login(username='testuser', password=USER_PASSWORD)
        response, repository_id, issue_id = self.get_edit_existing_issue()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.wsgi_request.user), 'testuser')
        self.assertTemplateUsed(response, ISSUE_FORM)

    def test_view_shows_correct_template(self):
        self.client.login(username='testuser', password=USER_PASSWORD)
        response, repository_id, issue_id = self.get_edit_existing_issue()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, ISSUE_FORM)

    def test_HTTP404_changing_issue_from_non_existent_repository(self):
        self.client.login(username='testuser', password=USER_PASSWORD)
        repositories = Repository.objects.all()
        non_existant_repository = repositories[len(repositories) - 1].id + 1
        response = self.client.get(reverse('issue-update', kwargs={'id': non_existant_repository, 'pk': 1}))

        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_HTTP404_changing_non_existing_issue(self):
        self.client.login(username='testuser', password=USER_PASSWORD)
        issues = Issue.objects.all()
        non_existing_issue = issues[len(issues) - 1].id + 1
        response, repository_id, issue_id = self.get_edit_existing_issue(issue_id=non_existing_issue)

        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_redirects_to_issue_details_on_success(self):
        self.client.login(username='testuser', password=USER_PASSWORD)
        _, repository_id, issue_id = self.get_edit_existing_issue()

        response = self.client.post(reverse('issue-update', kwargs={'id': repository_id, 'pk': issue_id}),
                                    {'title': 'Changed test title', 'description': 'changed test desc',
                                     'assignees': [], 'milestone': ''})

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/repository/{}/issues/{}/'.format(repository_id, issue_id))

    def test_issue_change_created_for_every_change(self):
        start_of_test = timezone.now()
        self.client.login(username='testuser', password=USER_PASSWORD)
        _, repository_id, issue_id = self.get_edit_existing_issue()

        response = self.client.post(reverse('issue-update', kwargs={'id': repository_id, 'pk': issue_id}),
                                    {'title': 'Changed test title', 'description': 'Changed test',
                                     'assignees': [], 'milestone': ''})

        self.assertEqual(response.status_code, 302)
        # Find all objects that have been changed since start of the test process
        issue_change_objects = IssueChange.objects.filter(date__gt=start_of_test,
                                                          message__contains=response.wsgi_request.user)
        # Changed title and assignee list
        self.assertEqual(len(issue_change_objects), 3)
