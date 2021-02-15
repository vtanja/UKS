from django.contrib.auth.models import User
from django.test import TestCase

# Create your tests here.
from apps.repository.models import Repository
from apps.issue.models import Issue
from apps.project.models import Project
from django.urls import reverse


def fill_test_data():
    user1 = User.objects.create_user(username='user1', password='aBcDeF1234')
    user2 = User.objects.create_user(username='user2', password='GhIjKl1234')
    user1.save()
    user2.save()

    repository1 = Repository.objects.create(name='test_repository1', description='test_repository_description', owner=user1)

    project1 = Project.objects.create(name='test project 1', description='test description', repository=repository1)
    project2 = Project.objects.create(name='test project 2', description='test description', repository=repository1)
    project3 = Project.objects.create(name='test project 3', description='test description', repository=repository1)

    test_issue1 = Issue.objects.create(title='test issue 1', description='test description', repository=repository1,
                                       created_by=user1, project=project1)
    test_issue2 = Issue.objects.create(title='test issue 2', description='test description', repository=repository1,
                                       created_by=user1, closed=True, project=project1)
    test_issue3 = Issue.objects.create(title='test issue 3', description='test description', repository=repository1,
                                       created_by=user1, project=project1)
    test_issue4 = Issue.objects.create(title='test issue 4', description='test description', repository=repository1,
                                       created_by=user1, project=project1)
    test_issue5 = Issue.objects.create(title='test issue 5', description='test description', repository=repository1,
                                       created_by=user1, project=project1)


class ProjectModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        fill_test_data()

    def test_name_label(self):
        project = Project.objects.get(id=1)
        field_label = project._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')

    def test_description_label(self):
        project = Project.objects.get(id=1)
        field_label = project._meta.get_field('description').verbose_name
        self.assertEqual(field_label, 'description')

    def test_name_max_length(self):
        project = Project.objects.get(pk=1)
        max_length = project._meta.get_field('name').max_length
        self.assertEquals(max_length, 30)
