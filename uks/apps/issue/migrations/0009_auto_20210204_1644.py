# Generated by Django 3.1.5 on 2021-02-04 16:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('milestone', '0001_initial'),
        ('issue', '0008_issue_milestone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='milestone',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='milestone.milestone'),
        ),
    ]
