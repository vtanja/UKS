# Generated by Django 3.1.5 on 2021-02-09 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('label', '0001_initial'),
        ('issue', '0010_auto_20210204_1922'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='labels',
            field=models.ManyToManyField(blank=True, to='label.Label'),
        ),
    ]
