# Generated by Django 3.1.5 on 2021-02-19 17:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tag', '0002_tag_commit'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tag',
            name='repository',
        ),
        migrations.AddField(
            model_name='tag',
            name='dateCreated',
            field=models.DateField(blank=True, verbose_name='Created'),
        ),
    ]
