# Generated by Django 3.1.5 on 2021-02-17 21:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0005_auto_20210215_2240'),
    ]

    operations = [
        migrations.AlterField(
            model_name='repository',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='repository',
            name='name',
            field=models.CharField(max_length=30, unique=True),
        ),
    ]