from django.test import TestCase

from ..models import Label
from .test_views import test_data_base


def get_label(index=0):
    return Label.objects.all()[index]


class LabelModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        test_data_base()

    def test_label_name(self):
        label = get_label()
        verbose_name = label._meta.get_field('name').verbose_name
        self.assertEquals(verbose_name, 'name')

    def test_label_name_max_length(self):
        label = get_label()
        max_length = label._meta.get_field('name').max_length
        self.assertEquals(max_length, 30)

    def test_label_description_validators(self):
        label = get_label()
        description_validators = label._meta.get_field('description').validators
        self.assertEquals(description_validators, [])

    def test_label_color_format(self):
        label = get_label()
        color_format = label._meta.get_field('color').format
        self.assertEquals(color_format, 'hexa')