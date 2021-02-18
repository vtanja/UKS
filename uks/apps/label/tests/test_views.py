from django.contrib.auth.models import User
from django.http import Http404
from django.test import TestCase
from django.urls import reverse

from ..models import Label
from ...repository.models import Repository

USER1_USERNAME = 'user1'
USER1_PASSWORD = 'jxbl23!c*'
USER2_USERNAME = 'user2'
USER2_PASSWORD = 'mc29*x!dsu'
USER3_USERNAME = 'user3'
USER3_PASSWORD = '73jzy5_*d'

LABEL_FORM = 'label/create_label.html'
DELETE_FROM = 'label/delete_label.html'
LABEL_LIST_FORM = 'label/label_list.html'


def test_dataBase():
    # Create users
    user1 = User.objects.create_user(username=USER1_USERNAME, password=USER1_PASSWORD)
    user2 = User.objects.create_user(username=USER2_USERNAME, password=USER2_PASSWORD)
    user3 = User.objects.create_user(username=USER3_USERNAME, password=USER3_PASSWORD)
    user1.save()
    user2.save()
    user3.save()

    # Create repositories
    repository1 = Repository.objects.create(name='repository1', description='desc1', owner=user1)
    repository2 = Repository.objects.create(name='repository2', description='desc2', owner=user2)
    repository3 = Repository.objects.create(name='repository3', description='desc3', owner=user3)
    repository1.save()
    repository2.save()
    repository3.save()

    # Create labels
    label1 = Label.objects.create(name='label1', description='label description1', color='#FF1818FF',
                                  repository=repository1)
    label2 = Label.objects.create(name='label2', description='label description2', color='#1FFFF6FF',
                                  repository=repository1)
    label3 = Label.objects.create(name='label3', description='label description3', color='#607BFFFF',
                                  repository=repository2)
    label4 = Label.objects.create(name='label4', description='label description4', color='#FF56C2FF',
                                  repository=repository2)
    label5 = Label.objects.create(name='label5', description='label description5', color='#3400FFFF',
                                  repository=repository3)
    label6 = Label.objects.create(name='label6', description='label description6', color='#DF98FFFF',
                                  repository=repository3)

    label1.save()
    label2.save()
    label3.save()
    label4.save()
    label5.save()
    label6.save()


def get_label_and_repository_id(label=0, repository=0):
    if label != -1:
        label_id = Label.objects.all()[label].id
    else:
        labels = Label.objects.all()
        label_id = labels[len(labels) - 1].id + 1
    repository_id = get_repository_id(repository)
    return repository_id, label_id


def get_repository_id(repository=0):
    if repository != -1:
        repository_id = Repository.objects.all()[repository].id
    else:
        repositories = Repository.objects.all()
        repository_id = repositories[len(repositories) - 1].id + 1
    return repository_id


class LabelListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_dataBase()

    def get_repository_labels(self, repository_id=0):
        repository_id = get_repository_id(repository_id)
        response = self.client.get(reverse('repository_labels', kwargs={'id': repository_id}))
        return response, repository_id

    def test_view_url_accessible_by_name(self):
        response, _ = self.get_repository_labels()
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name_and_test_template(self):
        response, _ = self.get_repository_labels()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, LABEL_LIST_FORM)

    def test_repository_with_labels(self):
        response, _ = self.get_repository_labels()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['object_list']) != 0)

    def test_repository_labels_count_and_labels_repository(self):
        response, repository = self.get_repository_labels()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['object_list']) == 2)
        for label in response.context['object_list']:
            self.assertEqual(label.repository.id, repository)

    def test_repository_not_exist(self):
        response, _ = self.get_repository_labels(-1)
        self.assertEqual(response.status_code, 404)


class CreateLabelViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_dataBase()

    def get_create_label_response(self, repository=0):
        repository_id = get_repository_id(repository)
        self.client.login(username=USER1_USERNAME, password=USER1_PASSWORD)
        response = self.client.get(reverse('create_label', kwargs={'id': repository_id}))
        return response

    def test_logged_in_user_can_access(self):
        response = self.get_create_label_response(0)
        self.assertEqual(str(response.wsgi_request.user), USER1_USERNAME)
        self.assertEqual(response.status_code, 200)

    def test_correct_template_form(self):
        response = self.get_create_label_response(0)
        self.assertTemplateUsed(response, LABEL_FORM)

    def test_bad_repository_for_form(self):
        response = self.get_create_label_response(-1)
        self.assertEqual(response.status_code, 404)

    def test_successfully_added_new_label(self):
        repository = get_repository_id(0)
        self.client.login(username=USER1_USERNAME, password=USER1_PASSWORD)
        response = self.client.post(reverse('create_label', kwargs={'id': repository}),
                                    {'name': 'Label name123', 'description': 'Label description', 'color': '#3375FFFF'})
        self.assertEqual(response.status_code, 302)

    def test_successfully_redirect(self):
        repository = get_repository_id(0)
        self.client.login(username=USER1_USERNAME, password=USER1_PASSWORD)
        response = self.client.post(reverse('create_label', kwargs={'id': repository}),
                                    {'name': 'Label name123', 'description': 'Label description', 'color': '#3375FFFF'})
        self.assertRedirects(response, '/repository/{}/labels/'.format(repository))

    def test_added_new_label_with_bad_repository(self):
        repository = get_repository_id(-1)
        self.client.login(username=USER1_USERNAME, password=USER1_PASSWORD)
        response = self.client.post(reverse('create_label', kwargs={'id': repository}),
                                    {'name': 'Label name123', 'description': 'Label description', 'color': '#3375FFFF'})
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)


class EditLabelViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_dataBase()

    def get_label_edit_view(self, repository_id=0, label_id=0):
        repository_id, label_id = get_label_and_repository_id(repository=repository_id, label=label_id)
        response = self.client.get(reverse('label-edit', kwargs={'id': repository_id, 'pk': label_id}))
        return response, repository_id, label_id

    def logged_user_get_edit_view(self, repository_id=0, label_id=0):
        self.client.login(username=USER1_USERNAME, password=USER1_PASSWORD)
        return self.get_label_edit_view(repository_id, label_id)

    def test_user_can_access(self):
        response, _, _ = self.logged_user_get_edit_view()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.wsgi_request.user), USER1_USERNAME)

    def test_check_form(self):
        response, _, _ = self.logged_user_get_edit_view()
        self.assertTemplateUsed(response, LABEL_FORM)

    def test_check_non_existing_label(self):
        response, _, _ = self.logged_user_get_edit_view(label_id=-1)
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_check_edit_function(self):
        _, repository_id, label_id = self.logged_user_get_edit_view()
        response = self.client.post(reverse('label-edit', kwargs={'id': repository_id, 'pk': label_id}),
                                    {'name': 'Label name456', 'description': 'Label description456',
                                     'color': '#3671FFFF'})
        self.assertEqual(response.status_code, 302)

    def test_check_edit_function_non_existing_label(self):
        _, repository_id, label_id = self.logged_user_get_edit_view()
        response = self.client.post(reverse('label-edit', kwargs={'id': repository_id, 'pk': 8}),
                                    {'name': 'Label name456', 'description': 'Label description456',
                                     'color': '#3671FFFF'})
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)


class DeleteLabelViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_dataBase()

    def get_label_delete_view(self, repository_id=0, label_id=0):
        repository_id, label_id = get_label_and_repository_id(repository=repository_id, label=label_id)
        response = self.client.get(reverse('label-delete', kwargs={'id': repository_id, 'pk': label_id}))
        return response, repository_id, label_id

    def logged_user_get_delete_view(self, repository_id=0, label_id=0):
        self.client.login(username=USER1_USERNAME, password=USER1_PASSWORD)
        return self.get_label_delete_view(repository_id, label_id)

    def test_user_can_access(self):
        response, _, _ = self.logged_user_get_delete_view()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.wsgi_request.user), USER1_USERNAME)

    def test_check_form(self):
        response, _, _ = self.logged_user_get_delete_view()
        self.assertTemplateUsed(response, DELETE_FROM)

    def test_check_delete_function(self):
        _, repository_id, label_id = self.logged_user_get_delete_view()
        response = self.client.post(reverse('label-delete', kwargs={'id': repository_id, 'pk': label_id}))
        self.assertEqual(response.status_code, 302)

    def test_check_delete_non_existing_label(self):
        _, repository_id, label_id = self.logged_user_get_delete_view()
        response = self.client.post(reverse('label-delete', kwargs={'id': repository_id, 'pk': 8}))
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)