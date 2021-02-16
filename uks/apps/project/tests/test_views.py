from django.test import TestCase
from django.urls import reverse
from .test_models import fill_test_data
from apps.repository.models import Repository
from apps.project.models import Project
from apps.issue.models import Issue


def get_repository_id(repo_id):
    if repo_id < len(Repository.objects.all()):
        repo_id = Repository.objects.all()[repo_id].id
    return repo_id


def get_repository_and_project_id(repo_id=0, pk=0):
    if repo_id < len(Repository.objects.all()):
        repo_id = Repository.objects.all()[repo_id].id
    if pk < len(Project.objects.all()):
        pk = Project.objects.all()[pk].id
    return repo_id, pk


class ProjectListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        fill_test_data()

    def get_repository_projects_response(self, repo_id=0):
        repo_id = get_repository_id(repo_id)
        self.client.login(username='user1', password='aBcDeF1234')
        response = self.client.get(reverse('repository_projects', kwargs={'repo_id': repo_id}))
        return response

    def test_view_url_exists_at_desired_location(self):
        repo_id = get_repository_id(0)
        self.client.login(username='user1', password='aBcDeF1234')
        response = self.client.get('/repository/{}/projects/'.format(repo_id))
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.get_repository_projects_response()
        self.assertEqual(response.status_code, 200)

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

    # da li su dobri projekti
    # da li je ulogovan korisnik


class ProjectCreateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        fill_test_data()

    def get_create_project_response(self, repo_id=0):
        repo_id = get_repository_id(repo_id)
        self.client.login(username='user1', password='aBcDeF1234')
        response = self.client.get(reverse('create_project', kwargs={'repo_id': repo_id}))
        return response

    def test_view_url_exists_at_desired_location(self):
        repo_id = get_repository_id(0)
        self.client.login(username='user1', password='aBcDeF1234')
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

    def test_successfully_added(self):
        repo_id = get_repository_id(0)
        self.client.login(username='user1', password='aBcDeF1234')
        response = self.client.post(reverse('create_project', kwargs={'repo_id': repo_id}),
                                    {'name': 'test project', 'description': 'test description'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/repository/{}/projects/'.format(repo_id))

    def test_add_to_non_existent_repository(self):
        repo_id = get_repository_id(len(Repository.objects.all()) + 1)
        self.client.login(username='user1', password='aBcDeF1234')
        response = self.client.post(reverse('create_project', kwargs={'repo_id': repo_id}),
                                    {'name': 'test project', 'description': 'test description'})
        self.assertEqual(response.status_code, 404)

    # da li je ucitan odg repository


class ProjectDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        fill_test_data()

    def get_project_details_response(self, repo_id=0, pk=0):
        repo_id, pk = get_repository_and_project_id(repo_id, pk)
        self.client.login(username='user1', password='aBcDeF1234')
        response = self.client.get(reverse('project_details', kwargs={'repo_id': repo_id, 'pk': pk}))
        return response

    def test_view_url_exists_at_desired_location(self):
        repo_id, proj_id = get_repository_and_project_id()
        self.client.login(username='user1', password='aBcDeF1234')
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
        response = self.get_project_details_response(10, 0)
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
        self.client.login(username='user1', password='aBcDeF1234')
        response = self.client.get(reverse('project_delete', kwargs={'repo_id': repo_id, 'pk': pk}))
        return response

    def post_response(self, repo_id=0, pk=0):
        repo_id, pk = get_repository_and_project_id(repo_id, pk)
        self.client.login(username='user1', password='aBcDeF1234')
        response = self.client.post(reverse('project_delete', kwargs={'repo_id': repo_id, 'pk': pk}))
        return response

    def test_view_url_exists_at_desired_location(self):
        repo_id, proj_id = get_repository_and_project_id()
        self.client.login(username='user1', password='aBcDeF1234')
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

    def test_correct_repository_and_project_loaded(self):
        response = self.get_project_delete_response(0, 0)
        self.assertEqual(response.context['repository'], Repository.objects.all()[0])
        self.assertEqual(response.context['project'], Project.objects.all()[0])
        self.assertEqual(response.context['repository'], response.context['project'].repository)

    def test_non_existent_repository(self):
        response = self.get_project_delete_response(10, 0)
        self.assertEqual(response.status_code, 404)

    def test_non_existent_project(self):
        response = self.get_project_delete_response(0, 10)
        self.assertEqual(response.status_code, 404)

    def test_successfully_deleted(self):
        response = self.post_response(0, 0)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/repository/{}/projects/'.format(1))

    def test_deleting_non_existent(self):
        response = self.post_response(0, 10)
        self.assertEqual(response.status_code, 404)


class ProjectUpdateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        fill_test_data()

    def get_project_update_response(self, repo_id=0, pk=0):
        repo_id, pk = get_repository_and_project_id(repo_id, pk)
        self.client.login(username='user1', password='aBcDeF1234')
        response = self.client.get(reverse('project_update', kwargs={'repo_id': repo_id, 'pk': pk}))
        return response

    def post_response(self, repo_id=0, pk=0):
        repo_id, pk = get_repository_and_project_id(repo_id, pk)
        self.client.login(username='user1', password='aBcDeF1234')
        response = self.client.post(reverse('project_update', kwargs={'repo_id': repo_id, 'pk': pk}),
                                    {'name': 'edited test name', 'description': 'edited test description'})
        return response

    def test_view_url_exists_at_desired_location(self):
        repo_id, proj_id = get_repository_and_project_id()
        self.client.login(username='user1', password='aBcDeF1234')
        response = self.client.get('/repository/{}/projects/{}/update'.format(repo_id, proj_id))
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.get_project_update_response()
        self.assertEqual(response.status_code, 200)
