from django.contrib.auth.models import User
from django.test import TestCase

# Create your tests here.
from apps.repository.models import Repository
from apps.issue.models import Issue
from apps.project.models import Project
from django.urls import reverse


USER1_USERNAME = 'user1'
USER2_USERNAME = 'user2'
USER1_PASSWORD = 'aBcDeF1234'
USER2_PASSWORD = 'GhIjKl1234'


def fill_test_data():
    user1 = User.objects.create_user(username=USER1_USERNAME, password=USER1_PASSWORD)
    user2 = User.objects.create_user(username=USER2_USERNAME, password=USER2_PASSWORD)
    user1.save()
    user2.save()

    repository1 = Repository.objects.create(name='test_repository1', description='test_repository_description1',
                                            owner=user1)
    repository2 = Repository.objects.create(name='test_repository2', description='test_repository_description2',
                                            owner=user1)
    repository3 = Repository.objects.create(name='test_repository3', description='test_repository_description3',
                                            owner=user2)
    repository1.save()
    repository2.save()
    repository3.save()

    project1 = Project.objects.create(name='test project 1', description='test description 1', repository=repository1)
    project2 = Project.objects.create(name='test project 2', description='test description 2', repository=repository1)
    project3 = Project.objects.create(name='test project 3', description='test description 3', repository=repository1)
    project4 = Project.objects.create(name='test project 4', description='test description 4', repository=repository3)
    project1.save()
    project2.save()
    project3.save()
    project4.save()

    test_issue1 = Issue.objects.create(title='test issue 1', description='test description 1', repository=repository1,
                                       created_by=user1, project=project1, issue_status='TODO')
    test_issue2 = Issue.objects.create(title='test issue 2', description='test description 2', repository=repository1,
                                       created_by=user1, closed=True, project=project1, issue_status='DONE')
    test_issue3 = Issue.objects.create(title='test issue 3', description='test description 3', repository=repository1,
                                       created_by=user1, project=project1, issue_status='ONGOING')
    test_issue4 = Issue.objects.create(title='test issue 4', description='test description 4', repository=repository1,
                                       created_by=user1, project=project1, issue_status='TODO')
    test_issue5 = Issue.objects.create(title='test issue 5', description='test description 5', repository=repository1,
                                       created_by=user1, closed=True, project=project1, issue_status='DONE')

    test_issue1.save()
    test_issue2.save()
    test_issue3.save()
    test_issue4.save()
    test_issue5.save()


def get_project(index=0):
    return Project.objects.all()[index]


class ProjectModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        fill_test_data()

    def test_name_label(self):
        project = get_project()
        field_label = project._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')

    def test_description_label(self):
        project = get_project()
        field_label = project._meta.get_field('description').verbose_name
        self.assertEqual(field_label, 'description')

    def test_name_max_length(self):
        project = get_project()
        max_length = project._meta.get_field('name').max_length
        self.assertEquals(max_length, 30)

    def test_repository_not_null(self):
        project = get_project()
        is_null = project._meta.get_field('repository').null
        self.assertFalse(is_null)

    def test_object_name_is_name(self):
        project = get_project()
        self.assertEqual(project.name, str(project))

    def test_get_absolute_url(self):
        project = get_project()
        self.assertEqual(project.get_absolute_url(),
                         reverse('project_details', args=[str(project.repository.id), str(project.id)]))
