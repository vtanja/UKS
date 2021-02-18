from django.contrib.auth.models import User
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
        self.assertTemplateUsed(response, 'label/label_list.html')

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


