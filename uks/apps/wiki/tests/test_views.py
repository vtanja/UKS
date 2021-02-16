
from django.contrib.auth.models import User
from django.http import Http404
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.repository.models import Repository
from apps.user.models import HistoryItem
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

    def request(self, repo_id):
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        return self.client.get(reverse('wiki-overview', kwargs={'id': repo_id}))

    def test_view_url_exists_at_desired_location_wiki_exist(self):
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        response = self.client.get('/repository/1/wiki/')
        self.assertEqual(response.status_code, 302)

    def test_view_url_exists_at_desired_location_wiki_not_exist(self):
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        response = self.client.get('/repository/4/wiki/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.request(4)
        self.assertEqual(response.status_code, 200)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('wiki-overview', kwargs={'id': 1}))
        self.assertRedirects(response, '/welcome/login/?next=/repository/1/wiki/')

    def test_view_uses_correct_template(self):
        response = self.request(4)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wiki/wiki_list.html')

    def test_repository_with_no_wikis(self):
        response = self.request(4)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context_data['wikis']) == 0)

    def test_HTTP404_if_repository_doesnt_exist(self):
        repo_id = len(Repository.objects.all())+1
        response = self.request(repo_id)
        self.assertEqual(response.status_code, 404)


class WikiDeleteViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        fill_test_db()

    def request(self, repo_id, wiki_id):
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        return  self.client.delete(reverse('wiki-delete', kwargs={'id': repo_id, 'pk': wiki_id}))

    def test_view_url_accessible_by_location(self):
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        response = self.client.delete('/repository/1/wiki/1/delete/')
        self.assertEqual(response.status_code, 302)

    def test_view_url_accessible_by_name(self):
        response = self.request(1,1)
        self.assertEqual(response.status_code, 302)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('wiki-delete', kwargs={'id': 1, 'pk': 1}))
        self.assertRedirects(response, '/welcome/login/?next=/repository/1/wiki/1/delete/')

    def test_deleting_non_existent_wiki(self):
        wiki_id = Wiki.objects.all().count()+1
        response = self.request(1, wiki_id)
        self.assertEqual(response.status_code, 404)

    def test_history_item_added_on_delete(self):
        start_of_the_test = timezone.now()
        response = self.request(2, 3)
        self.assertEqual(response.status_code, 302)
        change = HistoryItem.objects.filter(dateChanged__gt=start_of_the_test, belongsTo=response.wsgi_request.user,
                                              message__contains='deleted wiki page')
        self.assertEqual(len(change), 1)


class WikiDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        fill_test_db()

    def request(self, repo_id, wiki_id):
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        return self.client.get(reverse('wiki-details', kwargs={'id': repo_id, 'pk': wiki_id}))

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('wiki-details', kwargs={'id': 1, 'pk': 1}))
        self.assertRedirects(response, '/welcome/login/?next=/repository/1/wiki/1/')

    def test_view_url_exists_at_desired_location(self):
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        response = self.client.get('/repository/1/wiki/1/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.request(1, 1)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.request(1, 1)
        self.assertTemplateUsed(response, 'wiki/wiki_detail.html')

    def test_HTTP404_if_repository_doesnt_exist(self):
        repo_id = Repository.objects.all().count()+1
        response = self.request(repo_id, 1)
        self.assertEqual(response.status_code, 404)

    def test_HTTP404_if_wiki_doesnt_exist(self):
        repo_id = Repository.objects.all().count() + 1
        wiki_id = Wiki.objects.all().count()+1
        response = self.request(repo_id, wiki_id)
        self.assertEqual(response.status_code, 404)

    def test_view_for_wiki_that_exists(self):
        response = self.request(1, 1)
        self.assertTrue(response.context['wiki'] is not None)
        self.assertEqual(response.context['wiki'], Wiki.objects.all()[0])


class CreateWikiViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        fill_test_db()

    def request(self, repo_id):
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        return self.client.get(reverse('wiki-add', kwargs={'id': repo_id}))

    def request_post(self, repo_id):
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        return self.client.post(reverse('wiki-add', kwargs={'id': repo_id}),
                                    {'title': 'Test wiki 4', 'content': 'Test description'})

    def test_redirect_if_user_not_logged_in(self):
        response = self.client.get('/repository/1/wiki/add/')
        self.assertRedirects(response, '/welcome/login/?next=/repository/1/wiki/add/')

    def test_redirect_if_user_not_logged_in_creates_wiki(self):
        response = self.client.post(reverse('wiki-add', kwargs={'id': 1}),
                                    {'title': 'Test wiki 3', 'content': 'Test description'})
        self.assertRedirects(response, '/welcome/login/?next=/repository/1/wiki/add/')

    def test_view_url_exists_at_desired_location(self):
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        response = self.client.get('/repository/1/wiki/add/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.request(1)
        self.assertEqual(response.status_code, 200)

    def test_view_shows_correct_template(self):
        response = self.request(1)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, WIKI_FORM)

    def test_HTTP404_if_adding_to_non_existent_repository(self):
        repo_id = Repository.objects.all().count()+1
        response = self.request(repo_id)
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_redirects_to_wiki_list_on_success(self):
        response = self.request_post(1)
        self.assertEqual(response.status_code, 302)

    def test_logged_in_user_can_access(self):
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        response = self.client.post(reverse('wiki-add', kwargs={'id': 1}))
        self.assertEqual(str(response.wsgi_request.user), USER_USERNAME)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, WIKI_FORM)

    def test_if_correct_repo_is_loaded(self):
        response = self.request(1)

        repository = Repository.objects.get(id=1)
        self.assertEqual(response.context['repository'], repository )
        self.assertEqual(len(response.context['wikis']), Wiki.objects.filter(repository=repository).count())
        for wiki in response.context['wikis']:
            self.assertEqual(wiki.repository, repository)

    def test_history_item_added_on_create(self):
        start_of_the_test = timezone.now()
        response = self.request_post(1)
        self.assertEqual(response.status_code, 302)
        change = HistoryItem.objects.filter(dateChanged__gt=start_of_the_test, belongsTo=response.wsgi_request.user,
                                                message__contains='created')
        self.assertEqual(len(change), 1)


class WikiUpdateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        fill_test_db()

    def get_request(self, repo_id, wiki_id):
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        return self.client.get(reverse('wiki-update', kwargs={'id': repo_id, 'pk': wiki_id}))

    def post_request(self, repo_id, wiki_id):
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        return self.client.post(reverse('wiki-update', kwargs={'id': 1, 'pk': 1}),
                                    {'title': 'Test wiki 1', 'content': 'Test description 2'})

    def test_redirect_if_user_not_logged_in(self):
        response = self.client.get('/repository/1/wiki/1/edit/')
        self.assertRedirects(response, '/welcome/login/?next=/repository/1/wiki/1/edit/')

    def test_redirect_if_user_not_logged_in_updates_wiki(self):
        response = self.client.post(reverse('wiki-update', kwargs={'id': 1, 'pk': 1}),
                                    {'title': 'Test wiki 2', 'content': 'Test description 2'})
        self.assertRedirects(response, '/welcome/login/?next=/repository/1/wiki/1/edit/')

    def test_view_url_exists_at_desired_location(self):
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        response = self.client.get('/repository/1/wiki/1/edit/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.get_request(1, 1)
        self.assertEqual(response.status_code, 200)

    def test_view_shows_correct_template(self):
        response = self.get_request(1, 1)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, WIKI_FORM)

    def test_logged_in_user_can_access(self):
        response = self.get_request(1, 1)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.wsgi_request.user), USER_USERNAME)
        self.assertTemplateUsed(response, WIKI_FORM)

    def test_HTTP404_changing_wiki_from_non_existent_repository(self):
        repo_id = Repository.objects.all().count()+1
        response = self.get_request(repo_id, 1)

        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_HTTP404_changing_non_existing_wiki(self):
        wiki = Wiki.objects.all().count()+1
        response = self.get_request(1, wiki)

        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_history_item_added_on_update(self):
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        start_of_the_test = timezone.now()
        response = self.post_request(1, 1)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/repository/1/wiki/1/')
        change = HistoryItem.objects.filter(dateChanged__gt=start_of_the_test, belongsTo=response.wsgi_request.user,
                                                          message__contains='changed')
        self.assertEqual(len(change), 1)