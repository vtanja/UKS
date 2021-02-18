from django.test import TestCase

from ..models import Label
from .test_views import test_data_base


class LabelModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        test_data_base()

    def test_label_name(self):
        label = Label.objects.get(pk=1)
        verbose_name = label._meta.get_field('name').verbose_name
        self.assertEquals(verbose_name, 'name')

    def test_label_name_max_length(self):
        label = Label.objects.get(pk=1)
        max_length = label._meta.get_field('name').max_length
        self.assertEquals(max_length, 30)

    def test_label_description_validators(self):
        label = Label.objects.get(pk=1)
        description_validators = label._meta.get_field('description').validators
        self.assertEquals(description_validators, [])

    def test_label_color_format(self):
        label = Label.objects.get(pk=1)
        color_format = label._meta.get_field('color').format
        self.assertEquals(color_format, 'hexa')