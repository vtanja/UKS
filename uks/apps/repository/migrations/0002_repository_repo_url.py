# Generated by Django 3.1.5 on 2021-02-03 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='repository',
            name='repo_url',
            field=models.CharField(default='https://github.com/vtanja/UKS', max_length=100),
        ),
    ]
