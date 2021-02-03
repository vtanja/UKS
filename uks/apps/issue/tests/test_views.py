from django.contrib.auth.models import User
from django.http import Http404
from django.test import TestCase
from django.urls import reverse

from security.models import SiteUser
from ...repository.models import Repository
from ..models import Issue


class IssueListViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        test_user = User.objects.create_user(username='testuser', password='1E4@DAc#a1p')
        test_user1 = User.objects.create_user(username='testuser1', password='4XC%4@1LSp')
        test_user.save()
        test_user1.save()

        test_repository = Repository.objects.create(name='test_repository', description='test')
        test_repository1 = Repository.objects.create(name='test_repository1', description='test2')

        test_site_user = SiteUser.objects.create(user=test_user)
        test_site_user.repositories.add(test_repository)
        test_site_user.repositories.add(test_repository1)

        test_issue1 = Issue.objects.create(title='test issue', description='test', repository=test_repository, created_by=test_user)
        test_issue2 = Issue.objects.create(title='test issue', description='test desc', repository=test_repository, created_by=test_user)
        test_issue3 = Issue.objects.create(title='test issue 3', description='test', repository=test_repository, created_by=test_user1)
        test_issue1.save()
        test_issue2.save()
        test_issue3.save()

    def test_view_url_exists_at_desired_location(self):
        repository = Repository.objects.get(id=1)
        response = self.client.get('/repository/{}/issues/'.format(repository.id))
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        repository = Repository.objects.get(id=1)
        response = self.client.get(reverse('repository_issues', kwargs={'id': repository.id}))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        repository = Repository.objects.get(id=1)
        response = self.client.get(reverse('repository_issues', kwargs={'id': repository.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'issue/issue_list.html')

    def test_repository_with_no_issues(self):
        repository = Repository.objects.get(id=2)
        response = self.client.get(reverse('repository_issues', kwargs={'id': repository.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['object_list']) == 0)

    def test_repository_with_issues(self):
        repository = Repository.objects.get(id=1)
        response = self.client.get(reverse('repository_issues', kwargs={'id': repository.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['object_list']) == 3)

    def test_repository_doesnt_exist(self):
        response = self.client.get(reverse('repository_issues', kwargs={'id': 42}))
        self.assertEqual(response.status_code, 404)
        self.assertRaisesMessage(Http404, expected_message='No Issue matches the given query.')
