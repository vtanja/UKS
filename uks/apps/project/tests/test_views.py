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
