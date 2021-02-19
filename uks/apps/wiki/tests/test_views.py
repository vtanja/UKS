
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import get_object_or_404
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
    user_test = User.objects.create_user(username=USER_USERNAME, password=USER_PASSWORD)
    user_test1 = User.objects.create_user(username=USER1_USERNAME, password=USER1_PASSWORD)
    user_test2 = User.objects.create_user(username=USER2_USERNAME, password=USER2_PASSWORD)
    user_test.save()
    user_test1.save()
    user_test2.save()

    # Create repositories
    repository_test = Repository.objects.create(name='test_repository', description='test', owner=user_test)
    repository_test1 = Repository.objects.create(name='test_repository1', description='test2', owner=user_test)
    repository_test2 = Repository.objects.create(name='test_repository2', description='desc', owner=user_test)
    repository_test3 = Repository.objects.create(name='test_repository 3', description='test', owner=user_test)
    repository_test.save()
    repository_test1.save()
    repository_test2.save()
    repository_test3.save()

    # Create issues and add them to repositories
    test_wiki1 = Wiki.objects.create(title='test wiki 1', content='test 1 desc', repository=repository_test)
    test_wiki2 = Wiki.objects.create(title='test wiki 2', content='test 2 desc', repository=repository_test)
    test_wiki3 = Wiki.objects.create(title='test wiki 3', content='test 3 desc', repository=repository_test1)
    test_wiki4 = Wiki.objects.create(title='test wiki 4', content='test 3 desc', repository=repository_test1)

    test_wiki1.save()
    test_wiki2.save()
    test_wiki3.save()
    test_wiki4.save()


def get_wiki_and_repository_id(wiki=0, repository=0):
    if wiki != -1:
        wiki_id = Wiki.objects.all()[wiki].id
    else:
        wikis = Wiki.objects.all()
        wiki_id = wikis[len(wikis) - 1].id + 1
    repository_id = get_repository_id(repository)
    return repository_id, wiki_id


def get_repository_id(repository=0):
    if repository != -1:
        repository_id = Repository.objects.all()[repository].id
    else:
        repositories = Repository.objects.all()
        repository_id = repositories[len(repositories) - 1].id + 1
    return repository_id

class WikiListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        fill_test_db()

    def request(self, repo_id):
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        return self.client.get(reverse('wiki-overview', kwargs={'repo_id': repo_id}))

    def test_view_url_exists_at_desired_location_wiki_exist(self):
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        repo_id = get_repository_id()
        response = self.client.get('/repository/{}/wiki/'.format(repo_id))
        self.assertEqual(response.status_code, 302)

    def test_view_url_exists_at_desired_location_wiki_not_exist(self):
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        repo_id = get_repository_id(3)
        response = self.client.get('/repository/{}/wiki/'.format(repo_id))
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        repo_id = get_repository_id(3)
        response = self.request(repo_id)
        self.assertEqual(response.status_code, 200)

    def test_redirect_if_not_logged_in(self):
        repo_id = get_repository_id()
        response = self.client.get(reverse('wiki-overview', kwargs={'repo_id':repo_id}))
        self.assertRedirects(response, '/welcome/login/?next=/repository/{}/wiki/'.format(repo_id))

    def test_view_uses_correct_template(self):
        repo_id = get_repository_id(3)
        response = self.request(repo_id)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wiki/wiki_list.html')

    def test_repository_with_no_wikis(self):
        repo_id = get_repository_id(3)
        response = self.request(repo_id)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context_data['wikis']) == 0)

    def test_HTTP404_if_repository_doesnt_exist(self):
        repo_id = get_repository_id(-1)
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        response = self.client.get(reverse('wiki-overview', kwargs={'repo_id': repo_id}))
        self.assertEqual(response.status_code, 404)


class WikiDeleteViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        fill_test_db()

    def request(self, repo_id, wiki_id):
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        return  self.client.delete(reverse('wiki-delete', kwargs={'repo_id': repo_id, 'pk': wiki_id}))

    def test_view_url_accessible_by_location(self):
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        repo_id, wiki_id = get_wiki_and_repository_id()
        response = self.client.delete('/repository/{}/wiki/{}/delete/'.format(repo_id, wiki_id))
        self.assertEqual(response.status_code, 302)

    def test_view_url_accessible_by_name(self):
        repo_id, wiki_id = get_wiki_and_repository_id()
        response = self.request(repo_id, wiki_id)
        self.assertEqual(response.status_code, 302)

    def test_redirect_if_not_logged_in(self):
        repo_id, wiki_id = get_wiki_and_repository_id()
        response = self.client.get(reverse('wiki-delete', kwargs={'repo_id': repo_id, 'pk': wiki_id}))
        self.assertRedirects(response, '/welcome/login/?next=/repository/{}/wiki/{}/delete/'.format(repo_id, wiki_id))

    def test_deleting_non_existent_wiki(self):
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        repo_id, wiki_id = get_wiki_and_repository_id(-1)
        response = self.client.delete(reverse('wiki-delete', kwargs={'repo_id': repo_id, 'pk': wiki_id}))
        self.assertEqual(response.status_code, 404)

    def test_history_item_added_on_delete(self):
        start_of_the_test = timezone.now()
        repo_id, wiki_id = get_wiki_and_repository_id(1, 2)
        response = self.request(repo_id, wiki_id)
        self.assertEqual(response.status_code, 302)
        change = HistoryItem.objects.filter(date_changed__gt=start_of_the_test, belongs_to=response.wsgi_request.user,
                                              message__contains='deleted wiki page')
        self.assertEqual(len(change), 1)

    def test_user_without_permission_deleting(self):
        self.client.login(username=USER1_USERNAME, password=USER1_PASSWORD)
        repo_id, wiki_id = get_wiki_and_repository_id(1, 2)
        response = self.client.delete(reverse('wiki-delete', kwargs={'repo_id': repo_id, 'pk': wiki_id}))
        self.assertEqual(response.status_code, 403)


class WikiDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        fill_test_db()

    def request(self, repo_id, wiki_id):
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        return self.client.get(reverse('wiki-details', kwargs={'repo_id': repo_id, 'pk': wiki_id}))

    def test_redirect_if_not_logged_in(self):
        repo_id, wiki_id = get_wiki_and_repository_id()
        response = self.client.get(reverse('wiki-details', kwargs={'repo_id': repo_id, 'pk': wiki_id}))
        self.assertRedirects(response, '/welcome/login/?next=/repository/{}/wiki/{}/'.format(repo_id, wiki_id))

    def test_view_url_exists_at_desired_location(self):
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        repo_id, wiki_id = get_wiki_and_repository_id()
        response = self.client.get('/repository/{}/wiki/{}/'.format(repo_id, wiki_id))
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        repo_id, wiki_id = get_wiki_and_repository_id()
        response = self.request(repo_id, wiki_id)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        repo_id, wiki_id = get_wiki_and_repository_id()
        response = self.request(repo_id, wiki_id)
        self.assertTemplateUsed(response, 'wiki/wiki_detail.html')

    def test_HTTP404_if_repository_doesnt_exist(self):
        repo_id, wiki_id = get_wiki_and_repository_id(0, -1)
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        response = self.client.get(reverse('wiki-details', kwargs={'repo_id': repo_id, 'pk': wiki_id}))
        self.assertEqual(response.status_code, 404)

    def test_HTTP404_if_wiki_doesnt_exist(self):
        repo_id, wiki_id = get_wiki_and_repository_id(-1, -1)
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        response = self.client.get(reverse('wiki-details', kwargs={'repo_id': repo_id, 'pk': wiki_id}))
        self.assertEqual(response.status_code, 404)

    def test_view_for_wiki_that_exists(self):
        repo_id, wiki_id = get_wiki_and_repository_id()
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        response = self.client.get(reverse('wiki-details', kwargs={'repo_id': repo_id, 'pk': wiki_id}))
        self.assertTrue(response.context_data['wiki'] is not None)
        self.assertIn(response.context_data['wiki'], Wiki.objects.all())
        self.assertEqual(response.context_data['wiki'].repository_id, repo_id)


class CreateWikiViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        fill_test_db()

    def request(self, repo_id):
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        return self.client.get(reverse('wiki-add', kwargs={'repo_id': repo_id}))

    def request_post(self, repo_id):
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        return self.client.post(reverse('wiki-add', kwargs={'repo_id': repo_id}),
                                    {'title': 'Test wiki 4', 'content': 'Test description x'})

    def test_redirect_if_user_not_logged_in(self):
        repo_id = get_repository_id()
        response = self.client.get('/repository/{}/wiki/add/'.format(repo_id))
        self.assertRedirects(response, '/welcome/login/?next=/repository/{}/wiki/add/'.format(repo_id))

    def test_redirect_if_user_not_logged_in_creates_wiki(self):
        repo_id = get_repository_id()
        response = self.client.post(reverse('wiki-add', kwargs={'repo_id': repo_id}),
                                    {'title': 'Test wiki 3', 'content': 'Test description xx'})
        self.assertRedirects(response, '/welcome/login/?next=/repository/{}/wiki/add/'.format(repo_id))

    def test_view_url_exists_at_desired_location(self):
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        repo_id = get_repository_id()
        response = self.client.get('/repository/{}/wiki/add/'.format(repo_id))
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        repo_id = get_repository_id()
        response = self.request(repo_id)
        self.assertEqual(response.status_code, 200)

    def test_view_shows_correct_template(self):
        repo_id = get_repository_id()
        response = self.request(repo_id)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, WIKI_FORM)

    def test_HTTP404_if_adding_to_non_existent_repository(self):
        repo_id = get_repository_id(-1)
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        response = self.client.get(reverse('wiki-add', kwargs={'repo_id': repo_id}))
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_redirects_to_wiki_list_on_success(self):
        repo_id = get_repository_id()
        response = self.request_post(repo_id)
        self.assertEqual(response.status_code, 302)

    def test_logged_in_user_can_access(self):
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        repo_id = get_repository_id()
        response = self.client.post(reverse('wiki-add', kwargs={'repo_id': repo_id}))
        self.assertEqual(str(response.wsgi_request.user), USER_USERNAME)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, WIKI_FORM)

    def test_if_correct_repo_is_loaded(self):
        repo_id = get_repository_id()
        repository = get_object_or_404(Repository, id=repo_id)
        response = self.request(repo_id)
        self.assertEqual(response.context['repository'], repository )
        self.assertEqual(len(response.context['wikis']), Wiki.objects.filter(repository=repository).count())
        for wiki in response.context['wikis']:
            self.assertEqual(wiki.repository, repository)

    def test_history_item_added_on_create(self):
        start_of_the_test = timezone.now()
        repo_id = get_repository_id()
        response = self.request_post(repo_id)
        self.assertEqual(response.status_code, 302)
        change = HistoryItem.objects.filter(date_changed__gt=start_of_the_test, belongs_to=response.wsgi_request.user,
                                                message__contains='created')
        self.assertEqual(len(change), 1)

    def test_user_without_permission_creating(self):
        self.client.login(username=USER1_USERNAME, password=USER1_PASSWORD)
        repo_id = get_repository_id(1)
        response = self.client.post(reverse('wiki-add', kwargs={'repo_id': repo_id}),
                                    {'title': 'Test wiki 4', 'content': 'Test description xxx'})
        self.assertEqual(response.status_code, 403)


class WikiUpdateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        fill_test_db()

    def get_request(self, repo_id, wiki_id):
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        return self.client.get(reverse('wiki-update', kwargs={'repo_id': repo_id, 'pk': wiki_id}))

    def post_request(self, repo_id, wiki_id):
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        return self.client.post(reverse('wiki-update', kwargs={'repo_id': repo_id, 'pk': wiki_id}),
                                    {'title': 'Test wiki 1', 'content': 'Test description 2 x'})

    def test_redirect_if_user_not_logged_in(self):
        repo_id, wiki_id = get_wiki_and_repository_id()
        response = self.client.get('/repository/{}/wiki/{}/edit/'.format(repo_id, wiki_id))
        self.assertRedirects(response, '/welcome/login/?next=/repository/{}/wiki/{}/edit/'.format(repo_id, wiki_id))

    def test_redirect_if_user_not_logged_in_updates_wiki(self):
        repo_id, wiki_id = get_wiki_and_repository_id()
        response = self.client.post(reverse('wiki-update', kwargs={'repo_id': repo_id, 'pk': wiki_id}),
                                    {'title': 'Test wiki 2', 'content': 'Test description 2 xx'})
        self.assertRedirects(response, '/welcome/login/?next=/repository/{}/wiki/{}/edit/'.format(repo_id, wiki_id))

    def test_view_url_exists_at_desired_location(self):
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        repo_id, wiki_id = get_wiki_and_repository_id()
        response = self.client.get('/repository/{}/wiki/{}/edit/'.format(repo_id, wiki_id))
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        repo_id, wiki_id = get_wiki_and_repository_id()
        response = self.get_request(repo_id, wiki_id)
        self.assertEqual(response.status_code, 200)

    def test_view_shows_correct_template(self):
        repo_id, wiki_id = get_wiki_and_repository_id()
        response = self.get_request(repo_id, wiki_id)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, WIKI_FORM)

    def test_logged_in_user_can_access(self):
        repo_id, wiki_id = get_wiki_and_repository_id()
        response = self.get_request(repo_id, wiki_id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.wsgi_request.user), USER_USERNAME)
        self.assertTemplateUsed(response, WIKI_FORM)

    def test_HTTP404_changing_wiki_from_non_existent_repository(self):
        repo_id, wiki_id = get_wiki_and_repository_id(0, -1)
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        response =self.client.get(reverse('wiki-update', kwargs={'repo_id': repo_id, 'pk': wiki_id}))

        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_HTTP404_changing_non_existing_wiki(self):
        repo_id, wiki_id = get_wiki_and_repository_id(-1, 0)
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        response = self.client.get(reverse('wiki-update', kwargs={'repo_id': repo_id, 'pk': wiki_id}))

        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_history_item_added_on_update(self):
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        start_of_the_test = timezone.now()
        repo_id, wiki_id = get_wiki_and_repository_id()
        response = self.post_request(repo_id, wiki_id)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/repository/{}/wiki/{}/'.format(repo_id, wiki_id))
        change = HistoryItem.objects.filter(date_changed__gt=start_of_the_test, belongs_to=response.wsgi_request.user,
                                                          message__contains='changed')
        self.assertEqual(len(change), 1)

    def test_user_without_permission_updating(self):
        self.client.login(username=USER1_USERNAME, password=USER1_PASSWORD)
        repo_id, wiki_id = get_wiki_and_repository_id(1, 2)
        response = self.client.post(reverse('wiki-update', kwargs={'repo_id': repo_id, 'pk': wiki_id}),
                                    {'title': 'Test wiki 1', 'content': 'Test description 2 '})
        self.assertEqual(response.status_code, 403)

class HistoryListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        fill_test_db()

    def request(self, repo_id, wiki_id):
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        return self.client.get(reverse('wiki-history', kwargs={'repo_id': repo_id, 'pk':wiki_id}))

    def test_view_url_exists_at_desired_location(self):
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        repo_id, wiki_id = get_wiki_and_repository_id()
        response = self.client.get('/repository/{}/wiki/{}/history/'.format(repo_id, wiki_id))
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        repo_id, wiki_id = get_wiki_and_repository_id()
        response = self.request(repo_id, wiki_id)
        self.assertEqual(response.status_code, 200)

    def test_redirect_if_not_logged_in(self):
        repo_id, wiki_id = get_wiki_and_repository_id()
        response = self.client.get(reverse('wiki-history', kwargs={'repo_id':repo_id, 'pk':wiki_id}))
        self.assertRedirects(response, '/welcome/login/?next=/repository/{}/wiki/{}/history/'.format(repo_id, wiki_id))

    def test_view_uses_correct_template(self):
        repo_id, wiki_id = get_wiki_and_repository_id()
        response = self.request(repo_id, wiki_id)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wiki/wiki_history.html')

    def test_HTTP404_if_repository_doesnt_exist(self):
        repo_id, wiki_id = get_wiki_and_repository_id(-1, 0)
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        response = self.client.get(reverse('wiki-history', kwargs={'repo_id': repo_id, 'pk':wiki_id}))
        self.assertEqual(response.status_code, 404)

    def test_HTTP404_if_wiki_doesnt_exist(self):
        repo_id, wiki_id = get_wiki_and_repository_id(0, -1)
        self.client.login(username=USER_USERNAME, password=USER_PASSWORD)
        response = self.client.get(reverse('wiki-history', kwargs={'repo_id': repo_id, 'pk': wiki_id}))
        self.assertEqual(response.status_code, 404)

    def test_user_without_permission_access_history(self):
        self.client.login(username=USER1_USERNAME, password=USER1_PASSWORD)
        repo_id, wiki_id = get_wiki_and_repository_id(1, 2)
        response = self.client.get(reverse('wiki-history', kwargs={'repo_id': repo_id, 'pk': wiki_id}))
        self.assertEqual(response.status_code, 403)