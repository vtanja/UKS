from django.test import TestCase
from django.urls import reverse
from .test_models import fill_test_data
from apps.repository.models import Repository
from apps.project.models import Project
from apps.issue.models import Issue


USER1_USERNAME = 'user1'
USER2_USERNAME = 'user2'
USER1_PASSWORD = 'aBcDeF1234'
USER2_PASSWORD = 'GhIjKl1234'


def get_repository_id(repo_id=0):
    if repo_id < len(Repository.objects.all()):
        repo_id = Repository.objects.all()[repo_id].id
    else:
        repo_id = Repository.objects.all()[len(Repository.objects.all()) - 1].id + 1
    return repo_id


def get_issue_id(issue_id=0):
    if issue_id < len(Issue.objects.all()):
        issue_id = Issue.objects.all()[issue_id].id
    else:
        issue_id = Issue.objects.all()[len(Issue.objects.all()) - 1].id + 1
    return issue_id


def get_repository_and_project_id(repo_id=0, pk=0):
    if repo_id < len(Repository.objects.all()):
        repo_id = Repository.objects.all()[repo_id].id
    else:
        repo_id = Repository.objects.all()[len(Repository.objects.all()) - 1].id + 1
    if pk < len(Project.objects.all()):
        pk = Project.objects.all()[pk].id
    else:
        pk = Project.objects.all()[len(Project.objects.all()) - 1].id + 1
    return repo_id, pk


def get_all_projects_url(repo_id=0):
    repo_id = get_repository_id(repo_id)
    return '/repository/{}/projects/'.format(repo_id)


class ProjectListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        fill_test_data()

    def get_repository_projects_response(self, repo_id=0):
        repo_id = get_repository_id(repo_id)
        self.client.login(username=USER1_USERNAME, password=USER1_PASSWORD)
        response = self.client.get(reverse('repository_projects', kwargs={'repo_id': repo_id}))
        return response

    def test_view_url_exists_at_desired_location(self):
        self.client.login(username=USER1_USERNAME, password=USER1_PASSWORD)
        response = self.client.get(get_all_projects_url(0))
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.get_repository_projects_response()
        self.assertEqual(response.status_code, 200)

    def test_user_not_logged_in(self):
        repo_id = get_repository_id(0)
        response = self.client.get(reverse('repository_projects', kwargs={'repo_id': repo_id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/welcome/login/?next=/repository/{}/projects/'.format(repo_id))

    def test_view_uses_correct_template(self):
        response = self.get_repository_projects_response()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'project/project_list.html')

    def test_repository_in_context(self):
        response = self.get_repository_projects_response()
        self.assertEqual(response.context['repository'], Repository.objects.all()[0])

    def test_repository_not_found(self):
        response = self.get_repository_projects_response(len(Repository.objects.all()) + 1)
        self.assertEqual(response.status_code, 404)

    def test_project_count_in_repository(self):
        response = self.get_repository_projects_response()
        self.assertEqual(len(response.context['project_list']), 3)

    def test_project_count_in_repository_with_no_projects(self):
        response = self.get_repository_projects_response(1)
        self.assertEqual(len(response.context['project_list']), 0)

    def test_correct_projects_loaded(self):
        response = self.get_repository_projects_response(0)
        repository = Repository.objects.filter(id=get_repository_id(0)).first()
        for proj in response.context['project_list']:
            self.assertEqual(proj.repository, repository)


class ProjectCreateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        fill_test_data()

    def get_create_project_response(self, repo_id=0):
        repo_id = get_repository_id(repo_id)
        self.client.login(username=USER1_USERNAME, password=USER1_PASSWORD)
        response = self.client.get(reverse('create_project', kwargs={'repo_id': repo_id}))
        return response

    def test_view_url_exists_at_desired_location(self):
        repo_id = get_repository_id(0)
        self.client.login(username=USER1_USERNAME, password=USER1_PASSWORD)
        response = self.client.get('/repository/{}/projects/add/'.format(repo_id))
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.get_create_project_response()
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.get_create_project_response()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'project/project_create.html')

    def test_user_not_logged_in(self):
        repo_id = get_repository_id(0)
        response = self.client.get(reverse('create_project', kwargs={'repo_id': repo_id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/welcome/login/?next=/repository/{}/projects/add/'.format(repo_id))

    def test_unauthenticated_user_adds_project(self):
        repo_id = get_repository_id(0)
        response = self.client.post(reverse('create_project', kwargs={'repo_id': repo_id}),
                                    {'name': 'test project', 'description': 'test description'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/welcome/login/?next=/repository/{}/projects/add/'.format(repo_id))

    def test_successfully_added(self):
        repo_id = get_repository_id(0)
        self.client.login(username=USER1_USERNAME, password=USER1_PASSWORD)
        response = self.client.post(reverse('create_project', kwargs={'repo_id': repo_id}),
                                    {'name': 'test project', 'description': 'test description'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, get_all_projects_url(0))

    def test_add_to_non_existent_repository(self):
        repo_id = get_repository_id(10)
        self.client.login(username=USER1_USERNAME, password=USER1_PASSWORD)
        response = self.client.post(reverse('create_project', kwargs={'repo_id': repo_id}),
                                    {'name': 'test project', 'description': 'test description'})
        self.assertEqual(response.status_code, 404)

    def test_correct_repository_loaded(self):
        response = self.get_create_project_response(0)
        repository = Repository.objects.filter(id=get_repository_id(0)).first()
        self.assertEqual(response.context['repository'], repository)


class ProjectDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        fill_test_data()

    def get_project_details_response(self, repo_id=0, pk=0):
        repo_id, pk = get_repository_and_project_id(repo_id, pk)
        self.client.login(username=USER1_USERNAME, password=USER1_PASSWORD)
        response = self.client.get(reverse('project_details', kwargs={'repo_id': repo_id, 'pk': pk}))
        return response

    def test_view_url_exists_at_desired_location(self):
        repo_id, proj_id = get_repository_and_project_id()
        self.client.login(username=USER1_USERNAME, password=USER1_PASSWORD)
        response = self.client.get('/repository/{}/projects/{}/'.format(repo_id, proj_id))
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.get_project_details_response()
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.get_project_details_response()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'project/project_details.html')

    def test_user_not_logged_in(self):
        repo_id, proj_id = get_repository_and_project_id()
        response = self.client.get(reverse('project_details', kwargs={'repo_id': repo_id, 'pk': proj_id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/welcome/login/?next=/repository/{}/projects/{}/'.format(repo_id, proj_id))

    def test_non_existent_repository(self):
        response = self.get_project_details_response(50, 0)
        self.assertEqual(response.status_code, 404)

    def test_non_existent_project(self):
        response = self.get_project_details_response(0, 10)
        self.assertEqual(response.status_code, 404)

    def test_correct_project_details_loaded(self):
        response = self.get_project_details_response(0, 0)
        self.assertEqual(response.context['repository'], Repository.objects.all()[0])
        self.assertEqual(response.context['project'], Project.objects.all()[0])
        self.assertEqual(response.context['repository'], response.context['project'].repository)

    def test_correct_issues_loaded(self):
        response = self.get_project_details_response(0, 0)
        issues = Issue.objects.filter(repository=Repository.objects.all()[0])
        self.assertEqual(len(response.context['issues']), len(issues))
        for i in issues:
            self.assertIn(i, response.context['issues'])
        for i in response.context['issues']:
            self.assertEqual(i.repository, Repository.objects.all()[0])
            self.assertEqual(i.project, Project.objects.all()[0])

    def test_issue_dictionary(self):
        response = self.get_project_details_response(0, 0)
        issues = Issue.objects.filter(repository=Repository.objects.all()[0])
        for i in issues:
            self.assertIn(i, response.context['issue_dict'][i.issue_status])


class ProjectDeleteViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        fill_test_data()

    def get_project_delete_response(self, repo_id=0, pk=0):
        repo_id, pk = get_repository_and_project_id(repo_id, pk)
        self.client.login(username=USER1_USERNAME, password=USER1_PASSWORD)
        response = self.client.get(reverse('project_delete', kwargs={'repo_id': repo_id, 'pk': pk}))
        return response

    def post_response(self, repo_id=0, pk=0):
        repo_id, pk = get_repository_and_project_id(repo_id, pk)
        self.client.login(username=USER1_USERNAME, password=USER1_PASSWORD)
        response = self.client.delete(reverse('project_delete', kwargs={'repo_id': repo_id, 'pk': pk}))
        return response

    def test_view_url_exists_at_desired_location(self):
        repo_id, proj_id = get_repository_and_project_id()
        self.client.login(username=USER1_USERNAME, password=USER1_PASSWORD)
        response = self.client.get('/repository/{}/projects/{}/delete'.format(repo_id, proj_id))
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.get_project_delete_response()
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.get_project_delete_response()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'project/project_delete.html')

    def test_user_not_logged_in(self):
        repo_id, proj_id = get_repository_and_project_id()
        response = self.client.get(reverse('project_delete', kwargs={'repo_id': repo_id, 'pk': proj_id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response,
                             '/welcome/login/?next=/repository/{}/projects/{}/delete'.format(repo_id, proj_id))

    def test_unauthenticated_user_deletes_project(self):
        repo_id, proj_id = get_repository_and_project_id()
        response = self.client.delete(reverse('project_delete', kwargs={'repo_id': repo_id, 'pk': proj_id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response,
                             '/welcome/login/?next=/repository/{}/projects/{}/delete'.format(repo_id, proj_id))

    def test_correct_repository_and_project_loaded(self):
        response = self.get_project_delete_response(0, 0)
        self.assertEqual(response.context['repository'], Repository.objects.all()[0])
        self.assertEqual(response.context['project'], Project.objects.all()[0])
        self.assertEqual(response.context['repository'], response.context['project'].repository)

    def test_non_existent_repository(self):
        response = self.get_project_delete_response(10, 0)
        self.assertEqual(response.status_code, 404)

    def test_non_existent_project(self):
        response = self.get_project_delete_response(0, 50)
        self.assertEqual(response.status_code, 404)

    def test_successfully_deleted(self):
        response = self.post_response(0, 0)
        repo_id = get_repository_id(0)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, get_all_projects_url(0))

    def test_deleting_non_existent(self):
        response = self.post_response(0, 50)
        self.assertEqual(response.status_code, 404)


class ProjectUpdateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        fill_test_data()

    def get_project_update_response(self, repo_id=0, pk=0):
        repo_id, pk = get_repository_and_project_id(repo_id, pk)
        self.client.login(username=USER1_USERNAME, password=USER1_PASSWORD)
        response = self.client.get(reverse('project_update', kwargs={'repo_id': repo_id, 'pk': pk}))
        return response

    def post_response(self, repo_id=0, pk=0):
        repo_id, pk = get_repository_and_project_id(repo_id, pk)
        self.client.login(username=USER1_USERNAME, password=USER1_PASSWORD)
        response = self.client.post(reverse('project_update', kwargs={'repo_id': repo_id, 'pk': pk}),
                                    {'name': 'edited test name', 'description': 'edited test description'})
        return response

    def test_view_url_exists_at_desired_location(self):
        repo_id, proj_id = get_repository_and_project_id()
        self.client.login(username=USER1_USERNAME, password=USER1_PASSWORD)
        response = self.client.get('/repository/{}/projects/{}/update'.format(repo_id, proj_id))
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.get_project_update_response()
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.get_project_update_response()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'project/project_update.html')

    def test_user_not_logged_in(self):
        repo_id, proj_id = get_repository_and_project_id()
        response = self.client.get(reverse('project_update', kwargs={'repo_id': repo_id, 'pk': proj_id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response,
                             '/welcome/login/?next=/repository/{}/projects/{}/update'.format(repo_id, proj_id))

    def test_unauthenticated_user_updates_project(self):
        repo_id, proj_id = get_repository_and_project_id()
        response = self.client.post(reverse('project_update', kwargs={'repo_id': repo_id, 'pk': proj_id}),
                                    {'name': 'edited test name', 'description': 'edited test description'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response,
                             '/welcome/login/?next=/repository/{}/projects/{}/update'.format(repo_id, proj_id))

    def test_correct_repository_and_project_loaded(self):
        response = self.get_project_update_response(0, 0)
        self.assertEqual(response.context['repository'], Repository.objects.all()[0])
        self.assertEqual(response.context['project'], Project.objects.all()[0])
        self.assertEqual(response.context['repository'], response.context['project'].repository)

    def test_non_existent_repository(self):
        response = self.get_project_update_response(10, 0)
        self.assertEqual(response.status_code, 404)

    def test_non_existent_project(self):
        response = self.get_project_update_response(0, 10)
        self.assertEqual(response.status_code, 404)

    def test_successfully_updated(self):
        response = self.post_response(0, 0)
        repo_id = get_repository_id(0)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, get_all_projects_url(0))

    def test_updating_non_existent(self):
        response = self.post_response(0, 10)
        self.assertEqual(response.status_code, 404)


class ChangeIssueStatusTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        fill_test_data()

    def send_ajax_request(self, repo_id=0, issue_id=0, status='DONE'):
        repo_id = get_repository_id(repo_id)
        issue_id = get_issue_id(issue_id)
        self.client.login(username=USER1_USERNAME, password=USER1_PASSWORD)
        response = self.client.get(reverse('update_issue', kwargs={'repo_id': repo_id}),
                                   {'i_id': issue_id, 'list_id': status}, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        return response

    def test_user_not_logged_in(self):
        repo_id = get_repository_id()
        issue_id = Issue.objects.all()[0].id
        response = self.client.get(reverse('update_issue', kwargs={'repo_id': repo_id}),
                                   {'i_id': issue_id, 'list_id': 'DONE'}, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response,
                             '/welcome/login/?next=/repository/{}/projects/ajax/update_issue/%3Fi_id%3D{}%26list_id%3DDONE'
                             .format(repo_id, issue_id))

    def test_view_url_exists_at_desired_location(self):
        repo_id = get_repository_id()
        issue_id = Issue.objects.all()[0].id
        self.client.login(username=USER1_USERNAME, password=USER1_PASSWORD)
        response = self.client.get('/repository/{}/projects/ajax/update_issue/'.format(repo_id),
                                   {'i_id': issue_id, 'list_id': 'DONE'}, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.send_ajax_request(0, 1, 'ONGOING')
        self.assertEqual(response.status_code, 200)

    def test_status_successfully_changed(self):
        response = self.send_ajax_request(0, 2, 'TODO')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Issue.objects.all()[2].issue_status, 'TODO')
        self.assertFalse(Issue.objects.all()[2].closed)

    def test_status_successfully_changed_and_reopened(self):
        response = self.send_ajax_request(0, 4, 'TODO')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Issue.objects.all()[4].issue_status, 'TODO')
        self.assertFalse(Issue.objects.all()[4].closed)

    def test_status_successfully_changed_to_done_and_closed(self):
        response = self.send_ajax_request(0, 4, 'DONE')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Issue.objects.all()[4].issue_status, 'DONE')
        self.assertTrue(Issue.objects.all()[4].closed)
        
    def test_change_status_to_incorrect_value(self):
        response = self.send_ajax_request(0, 4, 'SOME_STATUS')
        self.assertEqual(response.status_code, 400)

    def test_change_status_of_non_existent_issue(self):
        response = self.send_ajax_request(0, 44, 'TODO')
        self.assertEqual(response.status_code, 400)
