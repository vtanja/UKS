# Generated by Django 3.1.5 on 2021-02-04 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('issue', '0009_auto_20210204_1644'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='closed',
            field=models.BooleanField(default=False),
        ),
    ]