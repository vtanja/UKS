from django.test import TestCase
from django.urls import reverse

from apps.wiki.models import Wiki
from apps.wiki.tests.test_views import fill_test_db


class WikiModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        fill_test_db()

    def test_title_label(self):
        wiki = Wiki.objects.get(pk=1)
        verbose_name = wiki._meta.get_field('title').verbose_name
        self.assertEquals(verbose_name, 'title')

    def test_content_label(self):
        wiki = Wiki.objects.get(pk=1)
        verbose_name = wiki._meta.get_field('content').verbose_name
        self.assertEquals(verbose_name, 'content')

    def test_title_max_length(self):
        wiki = Wiki.objects.get(pk=1)
        max_length = wiki._meta.get_field('title').max_length
        self.assertEquals(max_length, 100)

    def test_repository_not_null(self):
        wiki = Wiki.objects.get(pk=1)
        is_null = wiki._meta.get_field('repository').null
        self.assertTrue(not is_null)

    def test_get_absolute_url(self):
        wiki = Wiki.objects.get(pk=1)
        self.assertEqual(wiki.get_absolute_url(),
                         reverse('wiki-details', args=[str(wiki.repository.id), str(wiki.id)]))

