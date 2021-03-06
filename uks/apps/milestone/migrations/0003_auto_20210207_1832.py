# Generated by Django 3.1.5 on 2021-02-07 18:32

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('milestone', '0002_auto_20210204_2312'),
    ]

    operations = [
        migrations.AlterField(
            model_name='milestone',
            name='dateCreated',
            field=models.DateField(blank=True, default=datetime.date.today, verbose_name='Created'),
        ),
        migrations.AlterField(
            model_name='milestone',
            name='dateUpdated',
            field=models.DateField(blank=True, default=datetime.date.today, verbose_name='Last updated'),
        ),
    ]
