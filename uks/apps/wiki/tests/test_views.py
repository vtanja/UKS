
from django.contrib.auth.models import User
from django.http import Http404
from django.test import TestCase
from django.urls import reverse

from apps.repository.models import Repository
from apps.wiki.models import Wiki

USER_USERNAME = 'testuser'
USER1_USERNAME = 'testuser1'
USER2_USERNAME = 'testuser2'
USER_PASSWORD = '1E4@DAc#a1p'
USER1_PASSWORD = '4XC%4@1LSp'
USER2_PASSWORD = '4*uxX#sd23'

WIKI_FORM = 'wiki/wiki_form.html'


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
    test_repository3 = Repository.objects.create(name='test_repository 3', description='test', owner=test_user)
    test_repository.save()
    test_repository1.save()
    test_repository2.save()
    test_repository3.save()

    # Create issues and add them to repositories
    test_wiki1 = Wiki.objects.create(title='test wiki 1', content='test 1 desc', repository=test_repository)
    test_wiki2 = Wiki.objects.create(title='test wiki 2', content='test 2 desc', repository=test_repository)
    test_wiki3 = Wiki.objects.create(title='test wiki 3', content='test 3 desc', repository=test_repository1)
    test_wiki4 = Wiki.objects.create(title='test wiki 4', content='test 3 desc', repository=test_repository1)

    test_wiki1.save()
    test_wiki2.save()
    test_wiki3.save()
    test_wiki4.save()

class WikiListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        fill_test_db()

    def test_view_url_exists_at_desired_location_wiki_exist(self):
        login = self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        response = self.client.get('/repository/1/wiki/')
        self.assertEqual(response.status_code, 302)

    def test_view_url_exists_at_desired_location_wiki_not_exist(self):
        login = self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        response = self.client.get('/repository/4/wiki/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        login = self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        response = self.client.get(reverse('wiki-overview', kwargs={'id': 4}))
        self.assertEqual(response.status_code, 200)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('wiki-overview', kwargs={'id': 1}))
        self.assertRedirects(response, f'/welcome/login/?next=/repository/1/wiki/')

    def test_view_uses_correct_template(self):
        login = self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        response = self.client.get(reverse('wiki-overview', kwargs={'id': 4}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wiki/wiki_list.html')

    def test_repository_with_no_wikis(self):
        login = self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        response = self.client.get(reverse('wiki-overview', kwargs={'id': 4}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context_data['wikis']) == 0)

    def test_HTTP404_if_repository_doesnt_exist(self):
        login = self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        repo_id = len(Repository.objects.all())+1
        response = self.client.get(reverse('wiki-overview', kwargs={'id': repo_id}))
        self.assertEqual(response.status_code, 404)


class WikiDeleteViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        fill_test_db()

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('wiki-delete', kwargs={'id': 1, 'pk': 1}))
        self.assertRedirects(response, f'/welcome/login/?next=/repository/1/wiki/1/delete/')

    def test_redirects_to_wiki_list_on_success(self):
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        response = self.client.delete(reverse('wiki-delete', kwargs={'id': 1, 'pk': 1}))
        self.assertEqual(response.status_code, 302)


class WikiDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        fill_test_db()

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('wiki-details', kwargs={'id': 1, 'pk': 1}))
        self.assertRedirects(response, f'/welcome/login/?next=/repository/1/wiki/1/')

    def test_view_url_accessible_by_name(self):
        login = self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        response = self.client.get(reverse('wiki-details', kwargs={'id': 1, 'pk': 1}))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        login = self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        response = self.client.get(reverse('wiki-details', kwargs={'id': 1, 'pk': 1}))
        self.assertTemplateUsed(response, 'wiki/wiki_detail.html')

    def test_HTTP404_if_repository_doesnt_exist(self):
        login = self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        repo_id = Repository.objects.all().count()+1
        response = self.client.get(reverse('wiki-details', kwargs={'id': repo_id, 'pk': 1}))
        self.assertEqual(response.status_code, 404)

    def test_HTTP404_if_wiki_doesnt_exist(self):
        login = self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        repo_id = Repository.objects.all().count() + 1
        wiki_id = Wiki.objects.all().count()+1
        response = self.client.get(reverse('wiki-details', kwargs={'id': repo_id, 'pk': wiki_id}))
        self.assertEqual(response.status_code, 404)

    def test_view_for_wiki_that_exists(self):
        login = self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        response = self.client.get(reverse('wiki-details', kwargs={'id': 1, 'pk': 1}))
        self.assertTrue(response.context['wiki'] is not None)