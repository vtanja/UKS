# Generated by Django 3.1.5 on 2021-02-12 15:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0003_wikihistoryitem'),
    ]

    operations = [
        migrations.DeleteModel(
            name='WikiHistoryItem',
        ),
    ]
